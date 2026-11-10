# Báo cáo cá nhân — 2A202603945_VuLuongDuy

## 1. Thông tin thành viên

- Họ tên: Vũ Lương Duy
- MSSV: 2A202603945
- Email: duybaodap@gmail.com
- GitHub: Vuduy21 · nhánh làm việc: `duy`

## 2. Phần việc phụ trách

Thành viên 3 — **Eval Designer, UI & Reporter** (CP4, CP5; rubric C5, C6, C7):

- Viết 10 eval case của nhóm (`starter_v0/data/eval_group.json`), có case route tới tool mới.
- Dựng UI Streamlit cho Team showdown và chạy live chat lấy transcript.
- Viết báo cáo nhóm `report/team/group_report.md` (Phần A + tổng hợp Phần B).

## 3. Đóng góp cụ thể

- **10 eval case (5 single + 5 multi turn)**, không trùng case base, mỗi case một hành vi:
  - Args/convention mới: tên → handle chưa có trong base (`ylecun`, `demishassabis`), `timeframe=month` (base chỉ có day/week).
  - Boundary 2 chiều cho `send`: G07 (chưa duyệt nội dung → phải hỏi `yes_no`) và G08 (đã xác nhận rõ → phải gửi, không hỏi lại vô hạn).
  - Không dùng tool: G03 (câu cảm ơn), G04 (đặt vé — ngoài phạm vi).
  - Multi-turn: đổi nguồn Twitter → arXiv (G09), carry-over `topic=news` và đổi `timeframe` (G10).
  - G05 route tới tool mới `research_deduplicate` (2 URL chỉ khác hoa/thường và `/` cuối). Trước khi tool merge, G05 tạm trỏ tới `papers` để không làm đỏ `test_tool_contract.py`.
  - Kết quả v3: **8/10 PASS**; 2 case fail (G04, G07) phát hiện lỗi thật mà base eval chưa phủ. G07 là lý do nhóm làm rõ boundary của `send` ở v4.
  - Kết quả v4 (sau khi G05 trỏ tới tool mới): **9/10 PASS**, G05 PASS; G08 chuyển sang FAIL (đã xác nhận vẫn bị hỏi lại) — cặp G07/G08 đo được đánh đổi quá liều ↔ quá rụt rè.
- **UI Streamlit `starter_v0/app.py`**: tái sử dụng `run_model_tool_loop` của `chat.py` để hành vi giống CLI; hiện tool call/kết quả/lỗi tool từng lượt (không che lỗi); ghi transcript `*_ui_*`; chỉ liệt kê provider có API key; model mặc định free có tool calling. Sửa lỗi `UnicodeEncodeError` (emoji log trên stdout cp1252 làm UI báo nhầm `provider_error`).
- **Version v6 (`tools.yaml`)**: đọc run extension v4 (0.70) thấy 2/3 case fail do `policy_area` sai (`all`/bỏ trống) vì description chỉ ghi "Nhóm". Giả thuyết: viết lại description 4 tool còn mơ hồ (`format`, `policy`, `papers`, `paper_text`) với "khi nào dùng / không dùng" + mapping chủ đề → `policy_area`. Kết quả: base 0.95 → 0.95, group 0.90 → 0.90, **extension 0.70 → 0.90**; ghi dòng v6 trong `version_log.csv`.
- **Script `starter_v0/scripts/report_tables.py`**: sinh bảng B1–B4 từ `version_log.csv`, `runs/*.json`, `transcripts/*.json`; chỉ dùng run hợp lệ, đánh dấu run không hợp lệ.
- **Live chat v3**: 2 phiên `chat.py` (7 lượt) gồm yêu cầu thường, thiếu thông tin rồi bổ sung, yêu cầu đăng Telegram.
- **Báo cáo nhóm**: Phần A (A1–A3), Phần B (B1–B5a, khó khăn, reflection); sửa `tools_hash` dòng v3 trong `version_log.csv` bị ghi thiếu (12 → 64 ký tự, lấy từ run JSON).

## 4. Bằng chứng

- File/commit/PR:
  - `b6953fd` — eval_group.json, app.py, report_tables.py, Phần A (merge vào `main` qua PR #1)
  - `d4ab035`, `ed65783`, `5017ac8`, `89e2e32`, `e2aae99` — sửa và hoàn thiện UI
  - Run group: `starter_v0/runs/v3_B_group_openrouter_20261110T191010402195.json` (v3), `starter_v0/runs/v4_B_group_openrouter_20261111T031818497981.json` (v4, bản chính thức trong B3)
  - v6: `starter_v0/runs/v6_B_base_openrouter_20261111T033521944265.json`, `v6_B_group_openrouter_20261111T033552562715.json`, `v6_B_extension_openrouter_20261111T033619605580.json` (so với `v4_B_extension_openrouter_20261111T033317775499.json`)
  - Transcript UI với model free tự gọi `send(confirmed=true)`: `starter_v0/transcripts/v3_openrouter_ui_20261110T192155318540.transcript.json`
  - Transcript: `starter_v0/transcripts/v3_openrouter_20261110T191021129813.transcript.json`, `starter_v0/transcripts/v3_openrouter_20261110T191135924190.transcript.json`
- AI/công cụ đã dùng và cách tự kiểm tra kết quả:
  - Dùng **Claude Code** để phân tích đề, viết nháp eval case, code UI, script báo cáo.
  - Tự kiểm tra: chạy `pytest` (contract test xanh sau mỗi thay đổi eval); validate `eval_group.json` bằng chính `load_cases`/`validate_expected_tools` của `run_eval.py`; test UI bằng `streamlit.testing.AppTest` với fake provider rồi chạy thật với OpenRouter; mọi số liệu trong báo cáo lấy từ run/transcript thật, đối chiếu `artifact_version` với `version_log.csv`.

## 5. Tự đánh giá

- **Làm tốt:** eval nhóm bắt được 2 lỗi thật (G07 gọi `send` không xin xác nhận, G04 hỏi lại thay vì từ chối) và chỉ ra nguyên nhân: description `send` trong `tools.yaml` vẫn là bản mơ hồ của starter. UI minh bạch (hiện lỗi tool), có transcript làm bằng chứng.
- **Chưa tốt:** lượt live chat đầu tiên đặt câu "Tóm tắt bài này" ngay sau khi agent đã liệt kê bài, nên không kiểm tra được kịch bản thiếu thông tin — phải chạy thêm phiên thứ hai. Eval chỉ kiểm tra tên tool cho G05/G09 (args do model tự dựng), nên không đo được chất lượng args của các case đó.
- **Học được:** eval đo lựa chọn của model, unit test đo code của tool — cần cả hai; một case "fail" có giá trị khi nó chỉ ra đúng chỗ cần sửa (prompt hay tool declaration).
