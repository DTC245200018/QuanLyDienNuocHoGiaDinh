# Hệ thống Quản lý Hóa đơn Điện Nước Hộ Gia đình có tích hợp AI

Đồ án môn Ứng dụng Trí tuệ nhân tạo.

## 1. Công nghệ

- Backend: Python 3.12+, FastAPI, SQLAlchemy, Pydantic
- Database: Microsoft SQL Server (Windows Authentication)
- Driver: ODBC Driver 17 for SQL Server + pyodbc
- AI: Groq API (OpenAI-compatible, ví dụ model openai/gpt-oss-20b), có fallback khi API lỗi
- Frontend: HTML5, CSS3, JavaScript, Jinja2 (server-side render)

## 2. Chức năng chính

1. Đăng nhập và phân quyền (Quản lý / Khách thuê)
2. Quản lý hộ gia đình (kèm công tơ, tài khoản khách)
3. Nhập chỉ số thủ công (từ chối nếu chỉ số mới nhỏ hơn chỉ số cũ)
4. Cấu hình đơn giá điện / nước
5. Lập hóa đơn theo kỳ
6. Thanh toán và công nợ
7. Chatbot AI: hỏi-đáp phân tích tiêu thụ, công nợ, gợi ý tiết kiệm (dữ liệu từ CSDL)
8. Dashboard; tìm kiếm / lọc

## 3. Cấu trúc thư mục

```text
QuanLyDienNuocHoGiaDinh/
├── backend/
│   └── app/
├── frontend/
│   ├── templates/
│   └── static/
├── .env.example
├── requirements.txt
├── TEST_CASE.md
└── README.md
```

## 4. Cài đặt trên Windows

Yêu cầu:

- Python 3.12+
- SQL Server đang chạy (thường SQLEXPRESS)
- ODBC Driver 17 for SQL Server
- SSMS (khuyến nghị)
- Tài khoản Groq API key: https://console.groq.com

### Bước 1 – Tạo database (SSMS)

```sql
CREATE DATABASE QuanLyDienNuoc;
```

### Bước 2 – Môi trường ảo

```powershell
cd $env:USERPROFILE\Desktop\QuanLyDienNuocHoGiaDinh
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Bước 3 – File .env

```powershell
copy .env.example .env
```

Nội dung mẫu (KHÔNG commit file .env có key thật):

```env
DB_SERVER=localhost\SQLEXPRESS
DB_DATABASE=QuanLyDienNuoc
DB_DRIVER=ODBC Driver 17 for SQL Server
AI_PROVIDER=groq
AI_API_KEY=your_groq_api_key
AI_API_URL=https://api.groq.com/openai/v1/chat/completions
AI_MODEL=openai/gpt-oss-20b
```

### Bước 4 – Kiểm tra kết nối

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -c "from app.co_so_du_lieu.ket_noi import kiem_tra_ket_noi; print('OK' if kiem_tra_ket_noi() else 'FAIL')"
```

### Bước 5 – Tạo bảng

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m app.co_so_du_lieu.tao_bang
```

### Bước 6 – (Tuỳ chọn) Dữ liệu mẫu

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m app.tien_ich.tao_bo_du_lieu_10_ho
```

### Bước 7 – Chạy web

```powershell
$env:PYTHONPATH = "$PWD\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- Web: http://127.0.0.1:8000
- Chatbot quản lý: http://127.0.0.1:8000/ai
- Chatbot khách: http://127.0.0.1:8000/khach/ai

## 5. Tài khoản demo

- Quản lý: admin / admin123
- Khách thuê: khach01 / khach123 (hoặc tài khoản tạo khi thêm hộ)

## 6. Ghi chú AI (Chatbot)

- Hỏi-đáp tiếng Việt; số liệu lấy từ database (không bịa số)
- AI không tính tiền hóa đơn; lập HĐ và thanh toán độc lập với AI
- Ngoài phạm vi: từ chối lịch sự
- API lỗi hoặc thiếu key: fallback từ CSDL; nhãn [AI · Groq] khác với [Dự phòng · không kết nối AI]
- Lịch sử hội thoại chỉ trong phiên đăng nhập
- Khách thuê: chatbot chỉ dùng dữ liệu hộ được gán

## 7. Lỗi thường gặp

- Activate.ps1 bị chặn: Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
- Không kết nối SQL: kiểm tra service SQL Server, instance, database QuanLyDienNuoc, ODBC 17
- Port 8000 bận: đổi --port 8001
- AI HTTP 400/404 model: đổi AI_MODEL trên console Groq
- Chỉ thấy fallback: kiểm tra AI_API_KEY, AI_API_URL, AI_MODEL
- ModuleNotFoundError app: nhớ set $env:PYTHONPATH = "$PWD\backend" trước khi chạy

## 8. Thành viên

- Đinh Bảo Khanh
- Vũ Quang Minh