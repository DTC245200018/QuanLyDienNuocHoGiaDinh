# BỘ TEST CASE – Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia đình có tích hợp AI

**Phiên bản:** 1.1

**Môi trường:** Windows, FastAPI, SQL Server, Groq API

**Cấu trúc code:** backend/ + frontend/

**Tài khoản thử:**
- Quản lý: admin / admin123
- Khách thuê: khach01 / khach123 (hoặc tài khoản khách tạo khi thêm hộ)

**Cách chạy app trước khi test:**

```powershell
cd QuanLyDienNuocHoGiaDinh
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "$PWD\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

---

## TC01 – Đăng nhập Quản lý (UC001)

- **Mục tiêu:** Đăng nhập thành công với role Quản lý
- **Bước:**
  1. Mở /dang-nhap
  2. Nhập admin / admin123
  3. Bấm Đăng nhập
- **Kỳ vọng:** Chuyển tới /dashboard, menu đầy đủ chức năng quản lý
- **Kết quả:** Pass / Fail
- **Ghi chú:**

---

## TC02 – Đăng nhập sai mật khẩu (UC001)

- **Mục tiêu:** Hệ thống từ chối đăng nhập sai
- **Bước:**
  1. Nhập admin / sai_mat_khau
  2. Bấm Đăng nhập
- **Kỳ vọng:** Hiện thông báo lỗi, không vào dashboard
- **Kết quả:** Pass / Fail

---

## TC03 – Đăng nhập Khách thuê (UC001)

- **Mục tiêu:** Khách thuê vào đúng trang hộ mình
- **Bước:**
  1. Đăng nhập tài khoản khách (vd: khach01 / khach123)
- **Kỳ vọng:** Vào /khach, thấy thông tin hộ được gán; menu chỉ Nhà tôi / Gợi ý AI / Đăng xuất
- **Kết quả:** Pass / Fail

---

## TC04 – Thêm hộ gia đình (UC002)

- **Mục tiêu:** Thêm hộ mới thành công
- **Bước:**
  1. Login admin
  2. Vào Hộ gia đình
  3. Nhập tên hộ, số người
  4. Lưu
- **Kỳ vọng:** Thông báo thành công; hộ xuất hiện trong bảng; (nếu có) tạo công tơ + tài khoản khách
- **Kết quả:** Pass / Fail

---

## TC05 – Công tơ điện/nước theo hộ (UC002)

- **Mục tiêu:** Mỗi hộ có công tơ điện và nước
- **Bước:**
  1. Thêm hộ mới (hoặc chọn hộ có sẵn)
  2. Kiểm tra danh sách công tơ / chỉ số theo mã hộ
- **Kỳ vọng:** Có đủ công tơ điện + nước gắn đúng hộ
- **Kết quả:** Pass / Fail

---

## TC06 – Nhập chỉ số hợp lệ (UC003)

- **Mục tiêu:** Lưu chỉ số khi mới >= cũ
- **Bước:**
  1. Vào Chỉ số
  2. Chọn công tơ, chỉ số cũ 1000, mới 1100
  3. Lưu
- **Kỳ vọng:** Lưu thành công, hiện trong lịch sử
- **Kết quả:** Pass / Fail

---

## TC07 – Chặn chỉ số mới < chỉ số cũ (UC003)

- **Mục tiêu:** Không cho lưu dữ liệu sai
- **Bước:**
  1. Nhập chỉ số cũ 1100, mới 1000
  2. Lưu
- **Kỳ vọng:** Báo lỗi, không lưu, không dùng để tính hóa đơn
- **Kết quả:** Pass / Fail

---

## TC08 – IoT giả lập (tuỳ chọn)

- **Mục tiêu:** Script giả lập có thể ghi chỉ số (không bắt buộc trong demo chính)
- **Bước:**
  1. Demo chính dùng nhập chỉ số thủ công
  2. (Tuỳ chọn) chạy script IoT với PYTHONPATH=backend
- **Kỳ vọng:** Luồng demo chính không phụ thuộc IoT
- **Kết quả:** Pass / Fail / Bỏ qua
- **Ghi chú:** IoT không bắt buộc trong phạm vi demo

---

## TC09 – Lập hóa đơn theo kỳ (UC004)

- **Mục tiêu:** Tính tiền từ chỉ số x đơn giá (+ phụ phí nếu có)
- **Bước:**
  1. Có chỉ số + đơn giá áp dụng
  2. Lập hóa đơn kỳ YYYY-MM cho 1 hộ
- **Kỳ vọng:** Hóa đơn tạo ra; tổng = điện + nước (+ phụ phí); trạng thái phù hợp
- **Kết quả:** Pass / Fail

---

## TC10 – Chatbot AI phân tích / công nợ / gợi ý (UC005 + UC006)

- **Mục tiêu:** Chatbot hỏi-đáp dựa trên dữ liệu CSDL; không bịa số
- **Bước:**
  1. Login admin, mở /ai (hoặc khách mở /khach/ai)
  2. Nhập câu hỏi tự nhiên, ví dụ: Hộ 22 còn nợ bao nhiêu? / Gợi ý tiết kiệm / Phân tích hộ 22
  3. Bấm Gửi
- **Kỳ vọng:** Có trả lời tiếng Việt; số liệu khớp DB; có nhãn [AI · Groq] khi API thành công
- **Kết quả:** Pass / Fail
- **Ghi chú:** Không dùng luồng Chọn hộ rồi Chạy phân tích kiểu form một lần

---

## TC11 – AI fallback khi Groq lỗi (UC005 / UC006)

- **Mục tiêu:** Vẫn trả lời dự phòng khi Groq lỗi; nghiệp vụ cốt lõi không phụ thuộc AI
- **Bước:**
  1. Tạm đặt AI_API_KEY sai (hoặc xóa key) trong .env, restart server
  2. Hỏi lại cùng câu như TC10
  3. Khôi phục key đúng, restart
- **Kỳ vọng:** Có nhãn [Dự phòng · không kết nối AI]; vẫn có nhận xét từ DB/quy tắc; lập HĐ và thanh toán vẫn chạy
- **Kết quả:** Pass / Fail

---

## TC12 – Thanh toán một phần và đủ (UC008)

- **Mục tiêu:** Cập nhật công nợ đúng
- **Bước:**
  1. Chọn hóa đơn chưa TT
  2. Trả một phần nhỏ hơn tổng, kiểm tra trạng thái một phần
  3. Trả tiếp phần còn lại, kiểm tra đã thanh toán
- **Kỳ vọng:** so_tien_da_tra tăng đúng; trạng thái đổi đúng
- **Kết quả:** Pass / Fail

---

## TC13 – Cấu hình đơn giá (UC007)

- **Mục tiêu:** Đơn giá điện/nước áp dụng khi lập HĐ
- **Bước:**
  1. Vào Đơn giá, cập nhật đơn giá đang áp dụng
  2. Lập hóa đơn mới
- **Kỳ vọng:** Hóa đơn dùng đúng đơn giá đang hiệu lực
- **Kết quả:** Pass / Fail

---

## TC14 – Khách thuê chỉ xem hộ mình (UI)

- **Mục tiêu:** Khách không vào trang quản lý
- **Bước:**
  1. Login khách
  2. Thử mở /dashboard, /hoa-don, /thanh-toan, /ai (admin)
- **Kỳ vọng:** Redirect về /khach hoặc /khach/ai; không thao tác quản trị
- **Kết quả:** Pass / Fail

---

## TC15 – Khách AI không lộ dữ liệu hộ khác

- **Mục tiêu:** Chatbot khách chỉ dùng dữ liệu hộ được gán
- **Bước:**
  1. Login khách hộ A
  2. Hỏi công nợ / phân tích
  3. Thử hỏi theo mã hộ B (khác A) nếu biết
- **Kỳ vọng:** Chỉ số liệu hộ A; không tiết lộ số liệu hộ B
- **Kết quả:** Pass / Fail

---

## TC16 – Phân biệt nguồn Groq vs fallback

- **Mục tiêu:** Cùng một câu hỏi, hai trạng thái API khác nhau thì nhãn khác nhau
- **Bước:**
  1. API OK: hỏi 1 câu, chụp nhãn [AI · Groq]
  2. API lỗi: hỏi lại, chụp nhãn [Dự phòng · không kết nối AI]
- **Kỳ vọng:** Hai nhãn khác rõ; không dùng chung một nhãn
- **Kết quả:** Pass / Fail

---

## Tổng hợp

Điền khi test thật trên commit hiện tại:

- TC01:
- TC02:
- TC03:
- TC04:
- TC05:
- TC06:
- TC07:
- TC08:
- TC09:
- TC10:
- TC11:
- TC12:
- TC13:
- TC14:
- TC15:
- TC16:

**Người test:**

**Ngày test:**

**Commit / phiên bản:**