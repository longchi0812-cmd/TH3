# Hệ Thống SOA (Service-Oriented Architecture)

Repository chứa mã nguồn các bài thực hành môn Kiến trúc Hướng dịch vụ (SOA):

## Cấu trúc dự án
- **`BaiThucHanh2/` - AuthService (Cổng 8000)**:
  - Quản trị người dùng, đăng nhập, cấp và xác thực JSON Web Token (JWT).
  - Cung cấp endpoint xác thực liên dịch vụ `/auth`.
- **`BaiThucHanh3/` - Product Management Service (Cổng 8001)**:
  - Quản lý sản phẩm (CRUD: Thêm, sửa, xóa, tìm kiếm, phân trang).
  - Cơ sở dữ liệu riêng biệt SQLite (`products.db`).
  - Giao diện Dashboard kiểm thử tích hợp.
  - Xác thực liên dịch vụ qua AuthService của Bài 2.

## Hướng dẫn khởi chạy nhanh
Truy cập vào thư mục `BaiThucHanh3` và chạy file batch:
- **Click đúp `run_both_services.bat`**: Tự động mở 2 dịch vụ trên 2 cổng 8000 và 8001, đồng thời mở Dashboard tại `http://127.0.0.1:8001/`.
