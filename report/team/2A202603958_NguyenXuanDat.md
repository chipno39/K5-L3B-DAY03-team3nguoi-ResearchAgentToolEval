# Báo cáo cá nhân — NguyenXuanDat-2A202603958

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Nguyễn Xuân Đạt
- MSSV: 2A202603958
- Email: xuandat31804@gmail.com

## 2. Phần việc phụ trách

Trưởng nhóm, Prompt & Eval Lead:
- Cấu hình môi trường và API key (`starter_v0/.env`), kiểm tra provider (preflight) và bộ test.
- Chạy baseline v0 và ba vòng tối ưu v1–v4 (kèm v2a, v5 bị loại) trên bộ eval base; chạy eval group cho v3, v4, v5.
- Chỉnh `artifacts/system_prompt.md` và mô tả tool trong `artifacts/tools.yaml`; ghi `artifacts/version_log.csv`.
- Khai báo tool mới của Thành viên 2 (`research_deduplicate`) vào `tools.yaml` và kiểm tra contract.


## 3. Đóng góp cụ thể


- **Setup (CP1):** cài Python 3.12 (Python 3.15 không cài được PyYAML), tạo `.env`, preflight OpenRouter OK, `pytest` xanh (62 passed, 17 skipped lúc đầu).
- **v0 (baseline):** case_accuracy 0.70 (14/20). Lỗi: out_of_scope (R08, R14), missing_info (R10, R11), wrong_boundary (R12), wrong_tool (R13). Nguyên nhân: prompt starter cố ý bảo model đoán thay vì hỏi, gửi không cần xác nhận.
- **v1:** bỏ các chỉ dẫn xấu, thêm "thiếu thông tin thì gọi `clarify`" và "`send` phải xác nhận". 0.70 → 0.80.
- **v2a (đã loại):** thêm rule routing vào prompt. 0.80 → 0.75, model hỏi lại quá mức (R01, M06), nên loại bỏ.
- **v2:** prompt về v1, viết lại mô tả 5 tool (khi nào dùng / không dùng, quy ước tham số). 0.80 → 0.90, multiturn 1.00.
- **v3:** thêm tool `research_deduplicate`; base 0.90, group 0.80.
- **v4:** làm rõ ranh giới trong `tools.yaml` (clarify yes_no cho mọi gửi/đăng, fetch dùng ngay khi có link, mapping tên → handle, `clarify.response_type` là required). Base 0.95, group 0.90.
- **v5 (đã loại):** thêm rule xác nhận mạnh hơn vào prompt. Base 0.85, group 0.80, nên hoàn lại prompt v1.
- **Tool mới:** viết khai báo YAML cho `research_deduplicate` và kiểm tra `test_tool_contract.py` (60 passed).


## 4. Bằng chứng

- **File/commit/PR:**
  - `starter_v0/artifacts/version_log.csv` (v0, v1, v2a, v2, v3, v4, v5).
  - Run files trong `starter_v0/runs/`:
    - v0: `v0_B_base_openrouter_20261110T182631564136.json`
    - v1: `v1_B_base_openrouter_20261110T184106278929.json`
    - v2: `v2_B_base_openrouter_20261110T185151086231.json`
    - v3: `v3_B_base_openrouter_20261110T185727578233.json`, `v3_B_group_openrouter_20261110T185805644931.json`
    - v4: `v4_B_base_openrouter_20261110T192002429743.json`, `v4_B_group_openrouter_20261110T192038241104.json`
  - Commit `4e986b7` và PR #4 (merge vào `main` ở commit `30eb96a`); PR #3 cho phần CP2 trước đó.
- **AI/công cụ đã dùng và cách tự kiểm tra kết quả:**
  - Dùng Claude (Claude Code) để hỗ trợ viết prompt, mô tả tool, chạy eval và đọc log.
  - Tự kiểm tra: mọi số liệu lấy từ run JSON qua `scripts/parse_runs.py`; chỉ dùng run có `provider_error_cases = 0` và `measured_cases = total_cases`; chạy `pytest tests/test_tool_contract.py` trước mỗi lần chạy eval; kiểm tra hash prompt/tools khác nhau giữa các version.


## 5. Tự đánh giá

- **Làm tốt:** mỗi version chỉ đổi một nhóm giả thuyết; v2a và v5 giảm điểm nên bị loại thay vì giữ lại để báo cáo đẹp; số liệu có thể kiểm tra lại từ run JSON.
- **Còn yếu:**
 - Hai case R12 (base) và G07 (group) chưa pass ở v4: model hỏi bằng `response_type=text` thay vì `yes_no`, hoặc coi "ok, gửi luôn" là đã xác nhận.
  - Kết quả giữa các lần chạy dao động (ví dụ G07 pass một lần rồi fail), nên chênh 0.05 chỉ là 1 case.
  - Khai báo YAML của `research_deduplicate` do tôi viết, chưa được Thành viên 2 xác nhận.
- **Nếu có thêm thời gian:** chạy lặp R12 và G07 nhiều lần để đo độ dao động; đổi G05 sang tool mới; sửa mô tả `clarify`/`send` thêm một vòng (v6).
