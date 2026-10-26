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

Phương pháp: kiểm thử hộp đen (giao diện web + URL).  
Môi trường: Windows, FastAPI http://127.0.0.1:8000, SQL Server, Groq API.  
Người test: Đinh Bảo Khanh, Vũ Quang Minh.  
Hoàn tất: 18/10/2026 · nhánh main.

---

## TC01 – Đăng nhập quản lý đúng
- **Chức năng:** Đăng nhập  
- **Điều kiện trước:** App chạy, có user admin  
- **Dữ liệu:** user: admin / pass: admin123  
- **Bước:** Mở /dang-nhap → nhập admin / admin123 → Đăng nhập  
- **Kỳ vọng:** Vào Dashboard quản lý  
- **Kết quả:** Pass | 10/10/2026 | UC001

## TC02 – Sai mật khẩu
- **Chức năng:** Đăng nhập  
- **Điều kiện trước:** App chạy  
- **Dữ liệu:** admin / sai_mk  
- **Bước:** Nhập mật khẩu sai → Đăng nhập  
- **Kỳ vọng:** Báo lỗi, không vào được  
- **Kết quả:** Pass | 10/10/2026

## TC03 – Để trống form đăng nhập
- **Chức năng:** Đăng nhập  
- **Điều kiện trước:** App chạy  
- **Dữ liệu:** user/pass trống  
- **Bước:** Bỏ trống form → Đăng nhập  
- **Kỳ vọng:** Không đăng nhập được  
- **Kết quả:** Pass | 10/10/2026

## TC04 – Khách không vào trang quản trị
- **Chức năng:** Phân quyền  
- **Điều kiện trước:** Đã login khach01  
- **Dữ liệu:** Truy cập /dashboard hoặc /phong  
- **Bước:** Login khách → gõ URL quản trị  
- **Kỳ vọng:** Chuyển về khu khách / không xem quản trị  
- **Kết quả:** Pass | 10/10/2026

## TC05 – Đăng nhập khách đúng
- **Chức năng:** Đăng nhập khách  
- **Điều kiện trước:** Có khach01 gắn hộ  
- **Dữ liệu:** khach01 / khach123  
- **Bước:** Đăng nhập khách  
- **Kỳ vọng:** Vào trang Nhà tôi  
- **Kết quả:** Pass | 10/10/2026

## TC06 – Đăng xuất
- **Chức năng:** Đăng xuất  
- **Điều kiện trước:** Đã login  
- **Bước:** Bấm Đăng xuất  
- **Kỳ vọng:** Về trang đăng nhập, mất phiên  
- **Kết quả:** Pass | 10/10/2026

## TC07 – Xem danh sách hộ
- **Chức năng:** Hộ gia đình  
- **Điều kiện trước:** Login admin, có ~10 hộ  
- **Bước:** Vào Quản lý hộ  
- **Kỳ vọng:** Hiển thị danh sách hộ  
- **Kết quả:** Pass | 11/10/2026 | UC002

## TC08 – Thêm hộ mới
- **Chức năng:** Hộ gia đình  
- **Điều kiện trước:** Login admin  
- **Dữ liệu:** Tên hộ mới, số người ≥ 1  
- **Bước:** Thêm hộ → Lưu  
- **Kỳ vọng:** Tạo hộ + công tơ Đ/N + tài khoản khách  
- **Kết quả:** Pass | 11/10/2026

## TC09 – Thêm hộ trùng tên
- **Chức năng:** Hộ gia đình  
- **Điều kiện trước:** Đã có hộ A  
- **Dữ liệu:** Tên trùng hộ A  
- **Bước:** Thêm hộ cùng tên  
- **Kỳ vọng:** Báo lỗi / không tạo trùng  
- **Kết quả:** Fail → Pass (chỉnh message; test lại 12/10/2026)

## TC10 – Tìm kiếm hộ theo mã/tên
- **Chức năng:** Hộ gia đình  
- **Điều kiện trước:** Có dữ liệu hộ  
- **Dữ liệu:** Từ khóa mã hoặc một phần tên  
- **Bước:** Gõ ô tìm kiếm  
- **Kỳ vọng:** Chỉ hiện hộ khớp  
- **Kết quả:** Pass | 11/10/2026

## TC11 – Xóa hộ chưa có HĐ
- **Chức năng:** Hộ gia đình  
- **Điều kiện trước:** Hộ mới, chưa lập HĐ  
- **Bước:** Xóa hộ đó  
- **Kỳ vọng:** Xóa thành công  
- **Kết quả:** Pass | 11/10/2026

## TC12 – Xóa hộ đã có HĐ
- **Chức năng:** Hộ gia đình  
- **Điều kiện trước:** Hộ đã có hóa đơn  
- **Bước:** Xóa hộ đó  
- **Kỳ vọng:** Từ chối xóa, báo đã có HĐ  
- **Kết quả:** Pass | 11/10/2026

## TC13 – Xem / lọc công tơ theo hộ
- **Chức năng:** Chỉ số  
- **Điều kiện trước:** Login admin  
- **Dữ liệu:** Chọn hoặc tìm mã hộ  
- **Bước:** Lọc công tơ theo hộ  
- **Kỳ vọng:** Chỉ hiện công tơ hộ đó  
- **Kết quả:** Pass | 12/10/2026 | UC003

## TC14 – Nhập chỉ số hợp lệ
- **Chức năng:** Chỉ số  
- **Điều kiện trước:** Có công tơ  
- **Dữ liệu:** chỉ số mới ≥ chỉ số cũ  
- **Bước:** Nhập chỉ số → Lưu  
- **Kỳ vọng:** Lưu thành công  
- **Kết quả:** Pass | 12/10/2026

## TC15 – Chỉ số mới < chỉ số cũ
- **Chức năng:** Chỉ số  
- **Điều kiện trước:** Có công tơ  
- **Dữ liệu:** cũ = 100, mới = 90  
- **Bước:** Nhập chỉ số mới nhỏ hơn cũ → Lưu  
- **Kỳ vọng:** Từ chối, cảnh báo, không dùng tính HĐ  
- **Kết quả:** Pass | 12/10/2026

## TC16 – Thiếu dữ liệu bắt buộc khi nhập chỉ số
- **Chức năng:** Chỉ số  
- **Điều kiện trước:** Form nhập chỉ số  
- **Dữ liệu:** Bỏ trống chỉ số mới  
- **Bước:** Lưu form trống  
- **Kỳ vọng:** Không lưu / báo lỗi  
- **Kết quả:** Pass | 12/10/2026

## TC17 – Xem đơn giá hiện tại
- **Chức năng:** Đơn giá  
- **Điều kiện trước:** Login admin  
- **Bước:** Vào Cấu hình đơn giá  
- **Kỳ vọng:** Hiện đơn giá điện/nước đang áp dụng  
- **Kết quả:** Pass | 13/10/2026 | UC007

## TC18 – Cập nhật đơn giá > 0
- **Chức năng:** Đơn giá  
- **Điều kiện trước:** Login admin  
- **Dữ liệu:** Điện/nước số dương  
- **Bước:** Sửa đơn giá → Lưu  
- **Kỳ vọng:** Lưu, áp dụng kỳ sau  
- **Kết quả:** Pass | 13/10/2026

## TC19 – Đơn giá ≤ 0 hoặc không hợp lệ
- **Chức năng:** Đơn giá  
- **Điều kiện trước:** Login admin  
- **Dữ liệu:** 0 hoặc số âm  
- **Bước:** Nhập giá không hợp lệ → Lưu  
- **Kỳ vọng:** Báo lỗi, không lưu  
- **Kết quả:** Pass | 13/10/2026

## TC20 – Lập HĐ khi có chỉ số hợp lệ
- **Chức năng:** Hóa đơn  
- **Điều kiện trước:** Hộ có chỉ số hợp lệ  
- **Dữ liệu:** Chọn hộ + kỳ YYYY-MM  
- **Bước:** Lập hóa đơn  
- **Kỳ vọng:** Tạo HĐ, trạng thái chưa TT  
- **Kết quả:** Pass | 13/10/2026 | UC004

## TC21 – Lập trùng kỳ cùng hộ
- **Chức năng:** Hóa đơn  
- **Điều kiện trước:** Đã có HĐ kỳ đó  
- **Dữ liệu:** Cùng hộ + cùng kỳ  
- **Bước:** Lập lại HĐ cùng kỳ  
- **Kỳ vọng:** Không tạo trùng / báo lỗi  
- **Kết quả:** Fail → Pass (đã chặn; test lại 14/10/2026)

## TC22 – Lập HĐ khi thiếu chỉ số
- **Chức năng:** Hóa đơn  
- **Điều kiện trước:** Hộ không có chỉ số mới  
- **Bước:** Chọn hộ đó → Lập HĐ  
- **Kỳ vọng:** Báo không đủ dữ liệu  
- **Kết quả:** Pass | 14/10/2026

## TC23 – Tìm kiếm HĐ
- **Chức năng:** Hóa đơn  
- **Điều kiện trước:** Có nhiều HĐ  
- **Dữ liệu:** Mã HĐ / mã hộ / kỳ  
- **Bước:** Tìm / lọc hóa đơn  
- **Kỳ vọng:** Lọc đúng  
- **Kết quả:** Pass | 14/10/2026

## TC24 – Thanh toán đủ
- **Chức năng:** Thanh toán  
- **Điều kiện trước:** HĐ còn nợ  
- **Dữ liệu:** Số tiền = còn nợ  
- **Bước:** Ghi nhận thanh toán  
- **Kỳ vọng:** da_thanh_toan, còn nợ 0  
- **Kết quả:** Pass | 14/10/2026 | UC008

## TC25 – Thanh toán một phần
- **Chức năng:** Thanh toán  
- **Điều kiện trước:** HĐ còn nợ  
- **Dữ liệu:** Số tiền < còn nợ  
- **Bước:** Ghi nhận thanh toán một phần  
- **Kỳ vọng:** thanh_toan_mot_phan, còn nợ giảm đúng  
- **Kết quả:** Fail → Pass (sửa cộng dồn so_tien_da_tra; test lại 15/10/2026)

## TC26 – Số tiền thanh toán ≤ 0
- **Chức năng:** Thanh toán  
- **Điều kiện trước:** HĐ còn nợ  
- **Dữ liệu:** 0 hoặc âm  
- **Bước:** Nhập số tiền không hợp lệ  
- **Kỳ vọng:** Từ chối  
- **Kết quả:** Pass | 15/10/2026

## TC27 – Xem lịch sử thanh toán
- **Chức năng:** Thanh toán  
- **Điều kiện trước:** Đã ghi nhận TT  
- **Bước:** Mở lịch sử thanh toán  
- **Kỳ vọng:** Hiện giao dịch đã lưu  
- **Kết quả:** Pass | 15/10/2026

## TC28 – AI phân tích hộ có HĐ
- **Chức năng:** AI  
- **Điều kiện trước:** Login admin, hộ có HĐ  
- **Dữ liệu:** Vào /ai, hỏi “Phân tích hộ …” (có mã hộ)  
- **Bước:** Gửi câu hỏi trên chatbot quản lý  
- **Kỳ vọng:** Trả lời tiếng Việt trên chat theo dữ liệu hộ (nhãn [AI · Groq] khi API OK)  
- **Kết quả:** Pass | 16/10/2026 | UC005–006

## TC29 – AI hỏi công nợ (Groq hoạt động)
- **Chức năng:** AI  
- **Điều kiện trước:** API Groq hoạt động  
- **Dữ liệu:** Hỏi “Hộ … còn nợ bao nhiêu?”  
- **Bước:** Gửi câu hỏi trên /ai  
- **Kỳ vọng:** Đúng công nợ / không bịa số ngoài dữ liệu hệ thống  
- **Kết quả:** Pass | 16/10/2026

## TC30 – Fallback khi API lỗi / tắt key
- **Chức năng:** AI  
- **Điều kiện trước:** Tạm sai key hoặc không mạng AI  
- **Dữ liệu:** Tắt/sai key → hỏi lại trên chat  
- **Bước:** Hỏi trên /ai khi API lỗi  
- **Kỳ vọng:** Fallback (nhãn dự phòng); không làm hỏng lập HĐ  
- **Kết quả:** Pass | 16/10/2026

## TC31 – Khách xem AI chỉ hộ mình
- **Chức năng:** AI khách  
- **Điều kiện trước:** Login khach01  
- **Dữ liệu:** /khach/ai, hỏi gợi ý / công nợ; thử mã hộ khác  
- **Bước:** Chat trên khu khách  
- **Kỳ vọng:** Chỉ data hộ được gán; không lộ hộ khác  
- **Kết quả:** Pass | 17/10/2026

## TC32 – Xem Dashboard
- **Chức năng:** Dashboard  
- **Điều kiện trước:** Login admin  
- **Bước:** Mở /dashboard  
- **Kỳ vọng:** Có số liệu / thao tác nhanh  
- **Kết quả:** Pass | 17/10/2026

## TC33 – Vào URL quản trị khi chưa login
- **Chức năng:** Bảo mật phiên  
- **Điều kiện trước:** Đã đăng xuất  
- **Dữ liệu:** Gõ /phong, /hoa-don…  
- **Bước:** Truy cập URL quản trị không phiên  
- **Kỳ vọng:** Chuyển về đăng nhập  
- **Kết quả:** Pass | 17/10/2026

## TC34 – Form & bảng hiển thị
- **Chức năng:** Giao diện  
- **Điều kiện trước:** Chrome, cửa sổ PC  
- **Bước:** Duyệt các trang chính  
- **Kỳ vọng:** Không lỗi layout nghiêm trọng  
- **Kết quả:** Pass | 18/10/2026

## TC35 – Thao tác liên tiếp ổn định CSDL
- **Chức năng:** Ổn định CSDL  
- **Điều kiện trước:** DB SQL Server chạy  
- **Dữ liệu:** Thêm chỉ số → lập HĐ → TT  
- **Bước:** Thực hiện chuỗi nghiệp vụ  
- **Kỳ vọng:** Dữ liệu nhất quán, không mất HĐ  
- **Kết quả:** Pass | 18/10/2026

---

## Tổng hợp kết quả

| Mã | Ngày test | Kết quả |
|----|-----------|---------|
| TC01–TC06 | 10/10/2026 | Pass |
| TC07–TC12 | 11/10/2026 | Pass (TC09: Fail→Pass, test lại 12/10) |
| TC13–TC16 | 12/10/2026 | Pass |
| TC17–TC21 | 13/10/2026 | Pass (TC21: Fail→Pass, test lại 14/10) |
| TC22–TC25 | 14/10/2026 | Pass (TC25: Fail→Pass, test lại 15/10) |
| TC26–TC27 | 15/10/2026 | Pass |
| TC28–TC30 | 16/10/2026 | Pass |
| TC31–TC33 | 17/10/2026 | Pass |
| TC34–TC35 | 18/10/2026 | Pass |
