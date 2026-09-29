# BỘ TEST CASE – Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia đình có tích hợp AI

**Phiên bản:** 1.0  
**Môi trường:** Windows, FastAPI, SQL Server, Gemini API  
**Tài khoản thử:**
- Quản lý: `admin` / `admin123`
- Khách thuê: `khach01` / `khach123`

---

## TC01 – Đăng nhập Quản lý (UC001)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Đăng nhập thành công với role Quản lý |
| **Bước** | 1. Mở /dang-nhap<br>2. Nhập admin / admin123<br>3. Bấm Đăng nhập |
| **Kỳ vọng** | Chuyển tới /dashboard, menu đầy đủ chức năng quản lý |
| **Kết quả** | ☐ Pass / ☐ Fail |
| **Ghi chú** | |

---

## TC02 – Đăng nhập sai mật khẩu (UC001)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Hệ thống từ chối đăng nhập sai |
| **Bước** | 1. Nhập admin / sai_mat_khau<br>2. Bấm Đăng nhập |
| **Kỳ vọng** | Hiện thông báo lỗi, không vào dashboard |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC03 – Đăng nhập Khách thuê (UC001)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Khách thuê vào đúng trang hộ mình |
| **Bước** | 1. Đăng nhập khach01 / khach123 |
| **Kỳ vọng** | Vào /khach, thấy hộ P101, menu chỉ Hộ / AI / Đăng xuất |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC04 – Thêm hộ gia đình (UC002)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Thêm hộ mới thành công |
| **Bước** | 1. Login admin<br>2. Vào Hộ gia đình<br>3. Nhập tên hộ mới, số người<br>4. Lưu |
| **Kỳ vọng** | Hiện thông báo thành công, hộ xuất hiện trong bảng |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC05 – Gắn công tơ điện/nước (UC002)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Mỗi hộ có công tơ điện + nước |
| **Bước** | 1. POST /api/cong-to (dien, ma_phong=X)<br>2. POST /api/cong-to (nuoc, ma_phong=X)<br>3. GET /api/cong-to/phong/X |
| **Kỳ vọng** | 2 công tơ, đúng loại, đúng hộ |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC06 – Nhập chỉ số hợp lệ (UC003)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Lưu chỉ số khi mới ≥ cũ |
| **Bước** | 1. Vào Chỉ số<br>2. Chọn công tơ, chỉ số cũ 1000, mới 1100<br>3. Lưu |
| **Kỳ vọng** | Lưu thành công, hiện trong lịch sử |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC07 – Chặn chỉ số mới < chỉ số cũ (UC003)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Không cho lưu dữ liệu sai |
| **Bước** | 1. Nhập chỉ số cũ 1100, mới 1000<br>2. Lưu |
| **Kỳ vọng** | Báo lỗi, không lưu, không dùng để tính hóa đơn |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC08 – IoT giả lập gửi chỉ số (UC003)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Công tơ giả lập ghi chỉ số tự động |
| **Bước** | 1. Chạy `python -m app.tien_ich.iot_gia_lap`<br>2. Xem trang Chỉ số / GET /api/chi-so |
| **Kỳ vọng** | Có bản ghi mới, ghi_chu chứa "IoT gia lap", chỉ số tăng số nguyên |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC09 – Lập hóa đơn tự động (UC004)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Tính tiền từ chỉ số × đơn giá + phụ phí |
| **Bước** | 1. Đảm bảo có chỉ số + đơn giá<br>2. Lập hóa đơn kỳ YYYY-MM cho 1 hộ |
| **Kỳ vọng** | Hóa đơn tạo ra, tổng tiền = điện + nước + phụ phí, trạng thái chưa thanh toán |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC10 – AI phân tích & cảnh báo (UC005 + UC006)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | AI nhận xét từ dữ liệu có sẵn, có gợi ý tiết kiệm |
| **Bước** | 1. Vào AI Cảnh báo<br>2. Chọn hộ có hóa đơn<br>3. Chạy phân tích |
| **Kỳ vọng** | Có nội dung tiếng Việt, mức độ thap/trung_binh/cao; không bịa số liệu ngoài DB |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC11 – AI fallback khi API lỗi (UC006)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Hệ thống vẫn chạy khi Gemini lỗi |
| **Bước** | 1. Tạm đổi AI_API_KEY sai trong .env<br>2. Chạy phân tích AI<br>3. Khôi phục key |
| **Kỳ vọng** | Vẫn có nhận xét fallback; lập hóa đơn vẫn bình thường |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC12 – Thanh toán một phần & đủ (UC008)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Cập nhật công nợ đúng |
| **Bước** | 1. Chọn hóa đơn chưa TT<br>2. Trả một phần &lt; tổng<br>3. Kiểm tra trạng thái "một phần"<br>4. Trả tiếp phần còn lại → "đã thanh toán" |
| **Kỳ vọng** | so_tien_da_tra tăng đúng; trạng thái đổi đúng |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC13 – Cấu hình đơn giá / phụ phí (UC007)

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Có đơn giá điện, nước và phụ phí áp dụng khi lập HĐ |
| **Bước** | 1. GET /api/don-gia, GET /api/phu-phi<br>2. Lập hóa đơn mới |
| **Kỳ vọng** | Hóa đơn dùng đúng đơn giá đang áp dụng |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## TC14 – Khách thuê chỉ xem hộ mình

| Mục | Nội dung |
|-----|----------|
| **Mục tiêu** | Phân quyền: khách không vào được trang quản lý |
| **Bước** | 1. Login khach01<br>2. Thử mở /dashboard, /hoa-don, /thanh-toan |
| **Kỳ vọng** | Bị chuyển về /khach hoặc không thao tác quản lý được |
| **Kết quả** | ☐ Pass / ☐ Fail |

---

## Tổng hợp

| Mã | Pass | Fail | Ghi chú |
|----|------|------|---------|
| TC01–TC14 | | | Điền khi test thật |

**Người test:** …………………………  
**Ngày test:** …………………………