# Báo cáo cá nhân — QuachNgocHuy-2A202603956

Đổi tên file theo quy tắc `MSSV_HoTen.md`.

Ví dụ: `20241234_NguyenVanAn.md`.

## 1. Thông tin thành viên

- Họ tên: Quách Ngọc Huy
- MSSV: 2A202603956
- Email: zellsed123@gmail.com

## 2. Phần việc phụ trách

Tôi làm phần CP3: viết một tool mới cho agent và 3 test case cho tool đó. Tool tôi viết là `research_deduplicate`, dùng để lọc các kết quả research bị trùng URL.

## 3. Đóng góp cụ thể

- Viết tool `research_deduplicate` trong `tool.py`: chuẩn hóa URL (bỏ dấu `/` cuối, bỏ fragment, domain và scheme về chữ thường) rồi giữ lại item đầu tiên của mỗi URL. Item không có URL thì giữ nguyên. Input sai kiểu thì trả về dict lỗi chứ không raise exception.
- Viết `TOOL.md` mô tả tool.
- Viết 3 test case:
  - Happy path: 4 item, trong đó 2 item trùng URL sau khi chuẩn hóa, kết quả còn 3 item và danh sách gốc không bị sửa.
  - Bad input: truyền `items="not-a-list"`, tool trả về lỗi `TypeError`.
  - Failure: một item có `url` là số (123), tool trả về dict lỗi `TypeError`.

## 4. Bằng chứng

- File/commit/PR:
  - Branch `feat/QuachNgocHuy-2A202603956`
  - Commit `555612c`: "update: tool research deduplicate"
  - PR #5: "update: tool research deduplicate"
- AI/công cụ đã dùng và cách tự kiểm tra kết quả: xử dụng AI để nắm bắt đề tài, phần cần làm và những việc cần làm

## 5. Tự đánh giá

Tool chạy đúng với 3 test đã viết. Hạn chế là mới chuẩn hóa URL ở mức cơ bản, chưa xử lý `www.` hay tham số `utm_*`. Nếu có thời gian tôi sẽ bổ sung phần này.
