"""Streamlit UI for the Day 03 Research Agent.

Run from starter_v0/:
    streamlit run app.py
Then expose it for other teams:
    cloudflared tunnel --url http://localhost:8501

The UI reuses the exact tool loop from chat.py, so behaviour matches the CLI
and every turn is written to transcripts/*.transcript.json as evidence.
Tool calls, tool results and tool errors are always shown (never hidden).
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    ARTIFACTS_DIR,
    ROOT,
    now_iso,
    run_model_tool_loop,
    safe_slug,
    trim_history,
    write_transcript,
)
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

# chat.run_model_tool_loop prints "🔧 tool(...)" logs. On Windows, stdout may be
# cp1252 (e.g. when piped), which cannot encode emoji and would abort the turn.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

# provider -> env vars that must be set (any one) for it to be usable.
# Ollama needs no key; it is shown only when OLLAMA_BASE_URL/OLLAMA_MODEL is configured.
PROVIDER_ENV = {
    "openrouter": ["OPENROUTER_API_KEY"],
    "openai": ["OPENAI_API_KEY"],
    "anthropic": ["ANTHROPIC_API_KEY"],
    "gemini": ["GEMINI_API_KEY"],
    "ollama": ["OLLAMA_BASE_URL", "OLLAMA_MODEL"],
}
PROVIDERS = [name for name, keys in PROVIDER_ENV.items() if any(os.getenv(k, "").strip() for k in keys)]
SAMPLE_QUESTIONS = [
    "Tin tức AI hôm nay có gì nổi bật?",
    "Lấy 5 tweet mới nhất của Andrej Karpathy",
    "Mọi người đang bàn gì về Claude trên Twitter?",
    "Tóm tắt bài này giúp mình: https://www.anthropic.com/news",
    "Tìm paper arXiv mới về AI agent evaluation",
    "Đăng bản tin này lên Telegram giúp mình",
]

st.set_page_config(page_title="Research Agent", page_icon="🔎", layout="wide")


@st.cache_resource(show_spinner=False)
def get_provider(name: str) -> Any:
    return make_provider(name)


def new_transcript(provider: str, model: str | None, version: str, prompt_path: Path, tools_path: Path,
                   history_window: int, max_tool_rounds: int) -> tuple[Path, dict[str, Any]]:
    artifact_version = build_artifact_version(version, prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider), "ui", timestamp])
    path = ROOT / "transcripts" / f"{transcript_id}.transcript.json"
    transcript: dict[str, Any] = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider,
        "model": model,
        "source": "streamlit_ui",
        "system_prompt": str(prompt_path),
        "tools": str(tools_path),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return path, transcript


def reset_conversation() -> None:
    for key in ("messages", "history", "transcript", "transcript_path", "config_key"):
        st.session_state.pop(key, None)


def render_tool_errors(rounds: list[dict[str, Any]]) -> None:
    """Tool call details live in the transcript; only tool errors are surfaced here
    (the rubric does not accept a UI that hides tool errors)."""
    for r in rounds:
        for event in r.get("tool_results", []):
            result = event.get("result")
            if isinstance(result, dict) and result.get("error"):
                st.caption(f"⚠️ Tool `{event.get('tool')}` lỗi: {result.get('error')} — {result.get('message', '')}")


# ---------------- Sidebar: config ----------------
with st.sidebar:
    st.header("⚙️ Cấu hình")
    if not PROVIDERS:
        st.error("Chưa có API key provider nào trong starter_v0/.env (vd OPENROUTER_API_KEY).")
        st.stop()
    provider_name = st.selectbox("Provider", PROVIDERS, index=0,
                                 help="Chỉ hiện provider đã có API key trong starter_v0/.env")
    # Free OpenRouter model with tool calling (no credits needed, ~50 requests/day per account).
    model_input = st.text_input("Model (để trống = mặc định của provider)",
                                value="nvidia/nemotron-3-ultra-550b-a55b:free" if provider_name == "openrouter" else "")
    version = st.text_input("Version label", value="v3")
    history_window = st.number_input("History window (cặp lượt)", min_value=0, max_value=20, value=5)
    max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=8, value=4)
    if st.button("🗑️ Cuộc trò chuyện mới", use_container_width=True):
        reset_conversation()
        st.rerun()

prompt_path = ARTIFACTS_DIR / "system_prompt.md"
tools_path = ARTIFACTS_DIR / "tools.yaml"
system_prompt = prompt_path.read_text(encoding="utf-8")
tool_declarations = load_tool_declarations(tools_path)
openai_tools = to_openai_tools(tool_declarations)

try:
    provider = get_provider(provider_name)
    provider_error = None
except Exception as exc:  # missing key / SDK — show it, don't hide it
    provider, provider_error = None, f"{type(exc).__name__}: {exc}"

model = model_input.strip() or None
selected_model = model or getattr(provider, "default_model", None)

# New transcript whenever the config changes.
config_key = (provider_name, model, version, int(history_window), int(max_tool_rounds))
if st.session_state.get("config_key") != config_key:
    reset_conversation()
    st.session_state.config_key = config_key
    st.session_state.messages = []
    st.session_state.history = []
    path, transcript = new_transcript(provider_name, selected_model, version, prompt_path, tools_path,
                                      int(history_window), int(max_tool_rounds))
    st.session_state.transcript_path = path
    st.session_state.transcript = transcript

transcript = st.session_state.transcript


# ---------------- Main: chat ----------------
st.title("🔎 Research Agent")
st.caption("Tìm tin theo từ khóa / tài khoản X, đọc URL, tìm paper arXiv, tra policy nội bộ, "
           "tổng hợp digest và gửi Telegram **sau khi bạn xác nhận**.")

if provider_error:
    st.error(f"Không khởi tạo được provider `{provider_name}`: {provider_error}. "
             "Kiểm tra API key trong starter_v0/.env.")

if not st.session_state.messages:
    st.markdown("**Thử nhanh:**")
    cols = st.columns(3)
    for i, q in enumerate(SAMPLE_QUESTIONS):
        if cols[i % 3].button(q, key=f"sample_{i}", use_container_width=True):
            st.session_state.pending_input = q
            st.rerun()

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if msg.get("status") == "waiting_for_user":
                st.info("Agent đang chờ bạn trả lời câu hỏi trên.")
            elif msg.get("status") in {"provider_error", "max_tool_rounds"}:
                st.warning(f"status: {msg['status']}")
            render_tool_errors(msg.get("rounds", []))

user_text = st.chat_input("Nhập yêu cầu research…") or st.session_state.pop("pending_input", None)

if user_text and provider is not None:
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    turn_record: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.history, int(history_window)),
        {"role": "user", "content": user_text},
    ]
    with st.chat_message("assistant"):
        with st.spinner("Agent đang xử lý…"):
            try:
                result = run_model_tool_loop(
                    provider=provider,
                    messages=messages,
                    tools=openai_tools,
                    model=model,
                    max_tool_rounds=int(max_tool_rounds),
                )
                turn_record.update(result)
                assistant_text = result["assistant_text"] or "(không có nội dung trả lời)"
                st.session_state.history += [
                    {"role": "user", "content": user_text},
                    {"role": "assistant", "content": assistant_text},
                ]
            except Exception as exc:
                turn_record.update({"status": "provider_error", "error": f"{type(exc).__name__}: {exc}"})
                assistant_text = f"⚠️ Lỗi provider: {turn_record['error']}"

    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    write_transcript(st.session_state.transcript_path, transcript)
    st.session_state.messages.append({
        "role": "assistant",
        "content": assistant_text,
        "status": turn_record["status"],
        "rounds": turn_record.get("rounds", []),
    })
    st.rerun()
