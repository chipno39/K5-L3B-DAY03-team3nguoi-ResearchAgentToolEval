# Team

## Thông tin nhóm

- Tên nhóm: team3nguoi
- Lớp: L3B
- Repo nhóm: `K5-L3B-DAY03-team3nguoi-ResearchAgentToolEval`
- URL repo: https://github.com/chipno39/K5-L3B-DAY03-team3nguoi-ResearchAgentToolEval
- Nhánh nộp: `main`
- Commit chốt: _(trưởng nhóm điền hash commit cuối trên `main` sau khi merge PR cuối cùng)_

## Thành viên

| STT | Họ tên | MSSV | Email | GitHub | Vai trò |
| --: | ------ | ---- | ----- | ------ | ------- |
|   1 | Nguyễn Xuân Đạt | 2A202603958 | xuandat31804@gmail.com | chipno39 | Trưởng nhóm — Prompt & Eval Lead (CP1, CP2) |
|   2 | Quách Ngọc Huy | 2A202603956 | zellsed123@gmail.com | Zellsed | Tool Developer — tool mới + unit test (CP3) |
|   3 | Vũ Lương Duy | 2A202603945 | duybaodap@gmail.com | Vuduy21 | Eval Designer, UI & Reporter (CP4, CP5) |

## Cá nhân

Mỗi thành viên có báo cáo riêng trong `report/team/` (chi tiết đóng góp, bằng chứng, công cụ AI đã dùng):

- [2A202603958_NguyenXuanDat.md](report/team/2A202603958_NguyenXuanDat.md)
- [2A202603956_QuachNgocHuy.md](report/team/2A202603956_QuachNgocHuy.md)
- [2A202603945_VuLuongDuy.md](report/team/2A202603945_VuLuongDuy.md)

## NguyenXuanDat-2A202603958

### Phần việc phụ trách

- Setup môi trường, API key, preflight provider, `pytest` (CP1).
- Baseline v0 và các vòng tối ưu `system_prompt.md` / `tools.yaml` v1–v5 (CP2), ghi `artifacts/version_log.csv`.
- Khai báo tool mới `research_deduplicate` trong `tools.yaml`; review và merge PR.

### Đóng góp cụ thể

- v0 0.70 → v1 0.80 (bỏ chỉ dẫn xấu) → v2 0.90 (mô tả tool "dùng/không dùng" + convention args) → v4 0.95 (ranh giới xác nhận `send`, mapping tên → handle); thử và loại v2a, v5 (rule trong prompt làm điểm giảm).
- Transcript live chat v4 và bảng B1, B2, B4 trong group report.

### Bằng chứng

- Commit `fd90a6a`, `4e986b7`, `d945dab`; PR #3, #4, #6.
- `starter_v0/runs/v0_…` → `v5_…`, `starter_v0/transcripts/v4_openrouter_20261110T223711599834.transcript.json`.

## QuachNgocHuy-2A202603956

### Phần việc phụ trách

- Tool mới `research_deduplicate` và unit test (CP3).

### Đóng góp cụ thể

- `tools/research_deduplicate/tool.py`: chuẩn hóa URL (scheme/host lowercase, bỏ `/` cuối, bỏ fragment), giữ bản đầu tiên, giữ item không có URL, không sửa input, trả error dict khi sai kiểu.
- `TOOL.md` và 3 test trong `tests/test_tools_todo.py` (happy path, input xấu, nhánh lỗi); `pytest` 0 failed.

### Bằng chứng

- Commit `5d92487`, `555612c`; PR #2, #5.

## VuLuongDuy-2A202603945

### Phần việc phụ trách

- 10 eval case nhóm (CP4), UI Streamlit + Cloudflare Tunnel, live chat, tổng hợp group report (CP5).

### Đóng góp cụ thể

- `data/eval_group.json` (5 single + 5 multi turn, G05 route tới `research_deduplicate`); run group v3/v4/v6 (v6: 9/10).
- `app.py` (UI Streamlit), `scripts/report_tables.py`; transcript live chat v3; link dùng thử.
- v6 `tools.yaml`: hoàn thiện description `format`, `policy`, `papers`, `paper_text` → extension 0.70 → 0.90.
- Group report Phần A, B3, B5, khó khăn, reflection.

### Bằng chứng

- Commit `b6953fd`, `5fcc1e1`, `8fef3fc` và các commit UI trên nhánh `duy`; PR #1.
- `starter_v0/runs/v6_B_{base,group,extension}_openrouter_20261111T03…json`.
