# Báo cáo nhóm — Day 03 Research Agent Tool Eval

> Báo cáo gồm 2 phần có hạn khác nhau:
> - **Phần A (mục 2)** — giới thiệu agent, ngắn gọn 1 trang. **Xong trước Team showdown (16:30)** để team khác hiểu nhanh agent có tool gì, làm được gì. Có thể làm thêm poster `report/team/poster.html` hoặc `poster.svg`.
> - **Phần B (mục 3–7)** — chi tiết và bằng chứng, dựa trên log thật. Hoàn thiện trước deadline nộp bài.
>
> Mỗi bảng phải trỏ được tới file thật: run JSON, transcript, commit. Cách chấm xem [RUBRIC.md](../../RUBRIC.md).

## 1. Thông tin nhóm

- Tên nhóm:team3nguoi
- Thành viên và phân công: xem [TEAM.md](../../TEAM.md)
- Provider/model dùng cho v0–v3: OpenRouter · `openai/gpt-4o-mini` (mặc định của provider)

## 2. Mục tiêu và cách tiếp cận — PHẦN A: Giới thiệu agent

### A1. Agent này làm được gì

**Research agent cho tin AI/công nghệ:** tìm tin trên web (có lọc tin tức theo ngày/tuần/tháng), xem bài đăng của một tài khoản X hoặc tìm bài theo từ khóa, đọc và tóm tắt một URL, tìm và đọc paper arXiv, tra policy nội bộ công ty, gom kết quả thành digest markdown và **chỉ gửi lên Telegram sau khi người dùng xác nhận**. Khi thiếu thông tin (không rõ tài khoản nào, link nào), agent hỏi lại thay vì tự đoán.

**Cách chạy UI:**

```bash
cd starter_v0
pip install -r requirements.txt
streamlit run app.py                 # http://localhost:8501
cloudflared tunnel --url http://localhost:8501   # lấy link public
```

UI (`starter_v0/app.py`) dùng chung vòng lặp tool với `chat.py`, giao diện chat gọn cho người dùng; chi tiết tool call được ghi đầy đủ vào `starter_v0/transcripts/*_ui_*.transcript.json`, còn **lỗi tool luôn hiện một dòng cảnh báo** dưới câu trả lời (không che lỗi). Sidebar chỉ liệt kê provider đã có API key trong `.env`.

**Link dùng thử (deploy):**

> URL: https://clothing-systems-specification-relaxation.trycloudflare.com _(Cloudflare Quick Tunnel tới `localhost:8501`; link tạm thời, chỉ sống khi máy chạy UI và lệnh `cloudflared tunnel --url http://localhost:8501` còn chạy — mỗi lần chạy lại sẽ ra link mới)_

### A2. Tool agent có

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | Hỏi lại khi thiếu thông tin hoặc xin xác nhận yes/no trước khi gửi | không |
| timeline | Lấy bài đăng gần đây của một tài khoản X (handle không có `@`) | không |
| social_search | Tìm bài đăng X theo từ khóa (`Latest` / `Top`) | không |
| lookup | Tìm trên web (Tavily); `topic=news`, `timeframe` | không |
| fetch | Đọc nội dung một URL (Firecrawl) | không |
| format | Gom kết quả thành digest markdown | không |
| send | Gửi văn bản lên Telegram, chỉ khi `confirmed=true` | không |
| policy | Tra cứu policy nội bộ | không |
| papers | Tìm paper arXiv | không |
| paper_text | Tải PDF arXiv và trích text | không |
| research_deduplicate | Loại các kết quả trùng URL (chuẩn hóa URL) trong danh sách kết quả đã có | **có** |

### A3. Câu hỏi mẫu để thử

1. `Tin tức AI hôm nay có gì nổi bật?` → `lookup(topic=news, timeframe=day)`
2. `Lấy 5 tweet mới nhất của Andrej Karpathy` → `timeline(screenname=karpathy, limit=5)`
3. `Tóm tắt bài này giúp mình` → agent hỏi lại link; trả lời bằng URL → `fetch`
4. `Tìm paper arXiv mới về AI agent evaluation` → `papers`
5. `Đăng bản tin này lên Telegram giúp mình` → agent xin xác nhận trước, không gửi ngay
6. `Lọc trùng giúp mình: https://openai.com/blog/gpt-5 , https://www.anthropic.com/news/claude , https://OpenAI.com/blog/gpt-5/` → `research_deduplicate` (còn 2 link)


## 3. Giải pháp

- **`system_prompt.md` (giữ ở bản v1):** bỏ các chỉ dẫn xấu của starter ("đừng hỏi, cứ đoán", "gửi luôn", "chỉ một bước"); thay bằng: thiếu thông tin thì gọi `clarify`; gửi phải xác nhận; không gọi tool khi không cần.
- **`tools.yaml` (v2 → v6, bản nộp là v6):** viết lại mô tả mỗi tool theo dạng "dùng khi nào / không dùng khi nào"; ghi rõ quy ước tham số (handle không có `@`, `topic=news`, `timeframe`, `search_type=Top|Latest`); làm rõ ranh giới xác nhận của `send` (hỏi `clarify` yes_no trước, `confirmed=true` chỉ sau khi người dùng đồng ý); mapping tên → handle (vd Yann LeCun → `ylecun`); `clarify.response_type` là bắt buộc. v6 hoàn thiện nốt 4 tool còn mô tả ngắn của starter (`format`, `policy`, `papers`, `paper_text`): khi nào dùng / không dùng, ý nghĩa từng `template`, mapping chủ đề → `policy_area`, `sort_by=submittedDate` cho "paper mới", `max_pages` theo số trang user yêu cầu.
- **Tool mới `research_deduplicate`:** nhận danh sách kết quả, loại bỏ trùng theo URL đã chuẩn hóa, giữ bản đầu tiên, giữ item không có URL, không sửa danh sách đầu vào, trả error dict khi dữ liệu sai kiểu. Agent nên gọi khi đã có nhiều kết quả từ `lookup`/`social_search`/`fetch` và cần gộp bài trùng.

## 4. Kết quả — PHẦN B: Chi tiết và bằng chứng

### B1. Version Evidence

Metric là `case_accuracy` trên bộ `eval_base` (20 case). Tất cả run có `provider_error_cases == 0` và `measured_cases == total_cases`.

| Version | Changed Artifact | Hypothesis | Metric Before | Metric After | Run File |
|---|---|---|---:|---:|---|
| v0 | baseline | Đo hành vi trước khi sửa | – | 0.70 | `runs/v0_B_base_openrouter_20261110T182631564136.json` |
| v1 | system_prompt.md | Bỏ chỉ dẫn xấu, thêm "thiếu thì clarify", "gửi phải xác nhận" | 0.70 | 0.80 | `runs/v1_B_base_openrouter_20261110T184106278929.json` |
| v2a (loại) | system_prompt.md | Thêm rule routing vào prompt | 0.80 | 0.75 | `runs/v2_B_base_openrouter_20261110T184722003498.json` |
| v2 | tools.yaml | Mô tả tool rõ "dùng/không dùng" + quy ước tham số, prompt về v1 | 0.80 | 0.90 | `runs/v2_B_base_openrouter_20261110T185151086231.json` |
| v3 | tools.yaml | Thêm tool `research_deduplicate` | 0.90 | 0.90 | `runs/v3_B_base_openrouter_20261110T185727578233.json` |
| v4 | tools.yaml | Làm rõ ranh giới xác nhận, mapping tên → handle, `response_type` bắt buộc | 0.90 | 0.95 | `runs/v4_B_base_openrouter_20261110T192002429743.json` |
| v5 (loại) | system_prompt.md | Rule xác nhận mạnh hơn trong prompt | 0.95 | 0.85 | `runs/v5_B_base_openrouter_20261110T192201652942.json` |
| **v6 (bản nộp)** | tools.yaml | Model chọn sai `policy_area` (`all`/bỏ trống) vì description chỉ ghi "Nhóm"; mô tả rõ 4 tool còn lại + mapping chủ đề → `policy_area` sẽ sửa lỗi policy mà không làm giảm base/group (prompt giữ v1) | 0.95 | 0.95 | `runs/v6_B_base_openrouter_20261111T033521944265.json` |

v6 không đổi điểm base (vẫn chỉ R12 FAIL) nhưng đo trên bộ **extension** (10 case policy/arXiv — nơi 4 tool này được dùng): v4 = 0.70 → v6 = **0.90**. E01 (tweet viral có phải fact → `source_citation`) và E08 (workflow research → `ai_research`) từ FAIL thành PASS; còn E06 FAIL (gọi `policy` nhưng bỏ `lookup`). Run: `runs/v4_B_extension_openrouter_20261111T033317775499.json` → `runs/v6_B_extension_openrouter_20261111T033619605580.json`.

Kết quả trên `eval_group` (10 case): v3 = 0.80 (`runs/v3_B_group_openrouter_20261110T185805644931.json`), v4 = 0.90 (`runs/v4_B_group_openrouter_20261110T192038241104.json`), v5 = 0.80 (`runs/v5_B_group_openrouter_20261110T192220185840.json`). Các run này dùng bản G05 tạm (route tới `papers`). Sau khi G05 được đổi sang route tới tool mới `research_deduplicate`, chạy lại v4: **0.90** (9/10, G05 PASS) — `runs/v4_B_group_openrouter_20261111T031818497981.json`; v6 = **0.90** (cùng kết quả từng case) — `runs/v6_B_group_openrouter_20261111T033552562715.json` (bản chính thức cho B3).


### B2. Failure Analysis

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R08_out_of_scope | out_of_scope | `send` | Gọi `send` dù không cần tool | v1: bỏ "just go ahead" → pass |
| R14_out_of_scope_coding | out_of_scope | `send` | Gọi `send` cho câu hỏi lập trình | v1 → pass |
| R10_missing_handle | missing_info | `timeline` | Đoán handle thay vì hỏi lại | v2: mô tả tool + `clarify` → pass |
| R11_missing_url | missing_info | `fetch` | Đoán URL thay vì hỏi lại | v2 → pass |
| R12_confirm_before_send | wrong_boundary | `send` | Gửi ngay không xin xác nhận | v1/v2 chuyển sang `clarify`, nhưng v4 vẫn đặt `response_type=text` thay vì `yes_no` → **chưa pass** |
| R13_parallel_web_and_tweets | wrong_tool | `lookup` + `social_search` | Sai args: `query="AI news"`, thiếu `topic=news` | v1/v2 → pass |

### B3. Team Eval Cases

`starter_v0/data/eval_group.json` — 5 single turn + 5 multi turn. Run chính thức: `starter_v0/runs/v6_B_group_openrouter_20261111T033552562715.json` (v6 — bản nộp, `gpt-4o-mini`, 10/10 measured, 0 provider error) — **9/10 PASS**; v4 cho kết quả từng case giống hệt (`runs/v4_B_group_openrouter_20261111T031818497981.json`).

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_timeline_name_to_handle_limit (single) | "Yann LeCun" → `ylecun`, `limit=3` | `timeline(screenname=ylecun, limit=3)` | PASS |
| G02_news_timeframe_month (single) | tin tức tháng này → `topic=news`, `timeframe=month` | `lookup(topic=news, timeframe=month)` | PASS |
| G03_smalltalk_no_tool (single) | Câu cảm ơn không cần tool | no tool | PASS |
| G04_out_of_scope_booking (single) | Đặt vé ngoài phạm vi | no tool (refuse) | PASS |
| G05_route_new_tool (single) | **Route tới tool mới**: user đã có 3 kết quả, 2 URL chỉ khác hoa/thường và `/` cuối → phải lọc trùng, không tìm lại | `research_deduplicate` | PASS |
| G06_clarify_then_handle (multi) | Lượt 1 thiếu tài khoản, lượt 2 bổ sung tên | `timeline(screenname=demishassabis)` | PASS |
| G07_send_needs_confirmation (multi) | "Gửi luôn" khi chưa duyệt → vẫn xác nhận | `clarify(response_type=yes_no)` | PASS |
| G08_send_after_explicit_confirm (multi) | User đã xác nhận rõ → gửi | `send(confirmed=true)` | **FAIL** (agent gọi `clarify(response_type=yes_no)` thêm lần nữa thay vì `send`) |

Diễn biến qua các version: ở v3, G04 (hỏi lại giờ bay thay vì từ chối) và G07 (gọi thẳng `send`) FAIL; v4 làm rõ boundary của `send` trong `tools.yaml` nên G07 PASS — nhưng boundary "chặt" hơn lại làm G08 FAIL (user đã xác nhận rõ vẫn bị hỏi lại). Cặp G07/G08 cho thấy đánh đổi giữa *quá liều* và *quá rụt rè* mà base eval không đo được.
| G09_switch_social_to_papers (multi) | Đổi nguồn ở lượt sau | `papers` | PASS |
| G10_carryover_change_timeframe (multi) | Giữ `topic=news`, đổi `timeframe` | `lookup(topic=news, timeframe=month)` | PASS |

### B4. Live Chat Evidence

Lấy từ `starter_v0/transcripts/*.transcript.json`.

Transcript: `starter_v0/transcripts/v4_openrouter_20261110T223711599834.transcript.json` (một phiên 4 lượt, `artifact_version = v4+p94ed41cdeb08+te3a16f863216`, model `openai/gpt-4o-mini`, provider OpenRouter).

| Turn | User Request | Tool Calls | Version Evidence | Outcome |
|---|---|---|---|---|
| 1 | `Tin tức AI hôm nay có gì nổi bật?` (yêu cầu thường) | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | v4 | Đúng: route tới `lookup`, dùng `topic=news`, `timeframe=day`, trả 5 tin kèm link |
| 2 | `Tóm tắt bài này giúp mình` (thiếu URL) | Không gọi tool | v4 | Đúng hành vi: agent hỏi lại URL thay vì đoán. Lưu ý: agent hỏi bằng văn bản thường, không gọi tool `clarify` |
| 3 | `https://openai.com/blog/gpt-5` (bổ sung URL) | `fetch(url="https://openai.com/blog/gpt-5")` | v4 | Đúng: route tới `fetch`. Trang trả 404 nên agent báo lỗi trung thực và đề nghị tìm bài khác, không bịa nội dung |
| 4 | `Đăng bản tin này lên Telegram giúp mình` (yêu cầu gửi/đăng) | Không gọi tool (không gọi `send`) | v4 | Đúng ranh giới: agent hiển thị nội dung và hỏi "Bạn có muốn đăng không?" trước khi gửi. Lưu ý: hỏi bằng văn bản thường, không gọi `clarify` với `response_type=yes_no`; cùng nguyên nhân với R12 chưa pass ở mục B2 |

Transcript bổ sung (v3, `gpt-4o-mini`): `starter_v0/transcripts/v3_openrouter_20261110T191021129813.transcript.json` (tin AI → `lookup`+`format`; đọc URL → `fetch`; yêu cầu đăng Telegram → hiện nội dung và hỏi xác nhận, không gọi `send`) và `starter_v0/transcripts/v3_openrouter_20261110T191135924190.transcript.json` (thiếu tài khoản → hỏi lại; bổ sung "Andrej Karpathy" → agent xin xác nhận thừa cả việc đọc tweet và đoán sai handle `andrejkarpathy`).

Nhận xét: cả 3 loại hành vi cần chứng minh (yêu cầu thường, thiếu thông tin rồi bổ sung, xin xác nhận trước khi gửi) đều xuất hiện. Hạn chế: ở lượt 2 và 4 agent không dùng tool `clarify`; hành vi đúng nhưng không qua tool như thiết kế. Chưa gửi Telegram thật (chưa cấu hình `TELEGRAM_BOT_TOKEN`/`TELEGRAM_CHAT_ID`), nên chưa có bằng chứng cho bonus gửi Telegram.

### B5a. Required Evidence — Tool mới, unit test, UI

| Item | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Tool mới `research_deduplicate` | `starter_v0/tools/research_deduplicate/tool.py`, `TOOL.md` | Loại trùng URL chuẩn hóa, giữ thứ tự, không sửa đầu vào | Trả error dict khi `items` không phải list hoặc `url` không phải chuỗi |
| Unit test tool mới | `starter_v0/tests/test_tools_todo.py` — `pytest`: 70 passed, 14 skipped, 0 failed | 3 test: happy path, input sai kiểu, URL không phải chuỗi | 14 skip còn lại là stub của tool có sẵn |
| UI | `starter_v0/app.py`; lệnh chạy ở A1; `streamlit` trong `requirements.txt` | Streamlit dùng chung vòng lặp tool với `chat.py`; ghi transcript `*_ui_*`; chỉ liệt kê provider có API key | Lỗi tool luôn hiện cảnh báo (không che lỗi). Link dùng thử (Cloudflare Tunnel, tạm thời): https://clothing-systems-specification-relaxation.trycloudflare.com — đã kiểm tra từ ngoài, `/_stcore/health` trả 200 |

Tool unit tests: 3 test cho tool mới; ví dụ lỗi unit test bắt được mà eval không bắt: `item["url"] = 123` phải trả `{"error": "TypeError"}` (đầu vào model không bao giờ gửi qua eval). Tương tự, eval G05 chỉ kiểm tra model **gọi** `research_deduplicate`; nếu tool quên chuẩn hóa dấu `/` cuối thì eval vẫn PASS nhưng `test_my_new_tool_happy_path` FAIL (`unique_count` 4 thay vì 3).

### B5. Bonus Evidence

Nhóm **không làm bonus**: không chạy model local (B7), chỉ có 1 tool mới, không gửi Telegram thật (không cấu hình `TELEGRAM_CHAT_ID` — nhờ vậy khi team khác dùng thử UI, `send` không thể gửi thật), 14 stub test của tool có sẵn vẫn skip.

### B7. Small Local Model Challenge (bonus)

Không thực hiện.

## 5. Khó khăn và cách xử lý

- **Python 3.15 không cài được PyYAML** (không có wheel, cần build tools). Cài thêm Python 3.12 và dùng bản này cho mọi lệnh.
- **Thêm rule routing vào prompt làm giảm điểm (v2a: 0.80 → 0.75):** model hỏi lại quá mức (R01, M06). Chuyển rule sang mô tả tool (v2) thì tăng lên 0.90.
- **Mô tả tool tự mâu thuẫn:** bản v2 vừa ghi "không dùng `clarify` để xin xác nhận" vừa ghi "dùng yes_no cho việc đó"; sửa ở v4.
- **Kết quả không ổn định giữa các lần chạy** với cùng cấu hình (một case có thể pass rồi fail), nên chênh 0.05 chỉ là 1 case.
- **v5 (rule xác nhận mạnh hơn trong prompt) làm kết quả xấu hơn** (base 0.85, group 0.80), nên hoàn lại prompt v1.
- **UI báo `provider_error` dù model chạy đúng:** `chat.py` in log `🔧 tool(...)`; khi Streamlit chạy với stdout cp1252 (Windows) thì emoji gây `UnicodeEncodeError`. Sửa: `app.py` ép stdout UTF-8.
- **OpenRouter 402 / hết credit:** tài khoản free tier ($0) không chạy được model trả phí lâu dài. UI để mặc định model miễn phí có tool calling (`nvidia/nemotron-3-ultra-550b-a55b:free`) cho người dùng thử; mọi eval vẫn chạy `gpt-4o-mini` để so sánh công bằng. Model free chậm hơn 2–4 lần (64–113 giây cho câu hỏi tin tức, so với ~26 giây của `gpt-4o-mini`) và đôi khi chạm `max_tool_rounds` (gọi `social_search`/`lookup` liên tục 4 lần mà không tổng hợp).
- **Eval G05 phụ thuộc tool mới chưa merge:** tạm route tới `papers` để không làm đỏ `test_tool_contract.py`, đổi sang `research_deduplicate` sau khi tool được merge và chạy lại group v4.


## 6. Tổng hợp đóng góp

Chi tiết đóng góp của từng thành viên nằm trong [TEAM.md](../../TEAM.md) và các báo cáo cá nhân `report/team/MSSV_HoTen.md`.

## 7. Hạn chế và hướng cải thiện — B6. Reflection

- **Fix thuộc `system_prompt.md`:** bỏ chỉ dẫn xấu của starter (đoán thay vì hỏi, gửi không cần xác nhận, ép một bước) — v1 tăng 0.70 → 0.80.
- **Fix thuộc `tools.yaml`:** mô tả "dùng/không dùng", quy ước tham số, mapping tên → handle, ranh giới xác nhận — v2 và v4 tăng 0.80 → 0.90 → 0.95; mapping chủ đề → `policy_area` (v6) tăng extension 0.70 → 0.90. Cả v2a và v5 (nhồi rule vào prompt) đều làm điểm giảm → rule routing/args nên nằm cạnh tool mà nó mô tả.
- **Failure cần review thủ công:** R12 (base) và G08 (group). R12 kỳ vọng `response_type=yes_no` nhưng model hỏi "bạn muốn đăng nội dung nào?" bằng `text`, điều này hợp lý khi chưa có nội dung. G08 cho thấy agent hỏi thêm một lần dù người dùng đã xác nhận.
- **Prompt/tools không chuyển được sang model khác:** trên UI với model free `nvidia/nemotron-3-ultra-550b-a55b:free` (prompt/tools v3), câu hỏi chỉ là "Tin tức AI hôm nay có gì nổi bật?" nhưng model gọi `lookup` → `format` → **`send(confirmed=true)`** dù user không yêu cầu gửi (`starter_v0/transcripts/v3_openrouter_ui_20261110T192155318540.transcript.json`); tin không đi được chỉ vì thiếu `TELEGRAM_CHAT_ID`. Kết luận: cờ `confirmed` do **model** tự điền nên không phải guardrail thật; về lâu dài cần xác nhận phía ứng dụng (người dùng bấm nút) thay vì tin vào args.
- **Nếu có thêm một vòng:** chạy lặp R12 và G08 nhiều lần để đo độ dao động; sửa E06 (yêu cầu "làm bản tin + kiểm tra policy" chỉ gọi `policy`, bỏ `lookup`); thử làm rõ trong mô tả `send` khi nào câu trả lời của người dùng được coi là đã xác nhận (để G08 PASS mà G07 không FAIL lại).


## 8. Tài liệu tham khảo

- `starter_v0/artifacts/version_log.csv`, `starter_v0/runs/*.json`, `starter_v0/tests/test_tools_todo.py`
- [RUBRIC.md](../../RUBRIC.md), [CHECKPOINTS.md](../../CHECKPOINTS.md)
