# BÀI THỰC HÀNH SỐ 3: XÂY DỰNG DỊCH VỤ QUẢN LÝ SẢN PHẨM (PRODUCT MANAGEMENT)

## 1. Giới thiệu & Mục tiêu
Bài thực hành số 3 tập trung vào việc thiết kế và xây dựng **Dịch vụ Quản lý Sản phẩm (Product Management Service)** theo đúng nguyên lý của **Kiến trúc Hướng Dịch Vụ (SOA - Service-Oriented Architecture)**:
1. **Dịch vụ độc lập (Loose Coupling)**: Dịch vụ hoạt động trên một tiến trình và cổng riêng biệt (`http://localhost:8001`).
2. **Cơ sở dữ liệu độc lập (Database-per-Service)**: Sử dụng CSDL riêng (`products.db`) tách biệt hoàn toàn với CSDL của AuthService.
3. **Chuẩn giao tiếp chuẩn hóa (Standardized Service Contract)**: Cung cấp đầy đủ các chuẩn RESTful JSON API theo chuẩn HTTP method: `GET`, `POST`, `PUT`, `DELETE`.
4. **Xác thực liên dịch vụ (Inter-Service Authentication)**: Tích hợp với dịch vụ xác thực đã xây dựng ở **Bài thực hành số 2** (chạy tại `http://localhost:8000`), xác thực danh tính người dùng qua JWT Bearer Token.

---

## 2. Cấu trúc Thư mục Dự án

```
BaiThucHanh3/
│
├── controllers/
│   ├── __init__.py
│   └── product_controller.py  # Xử lý nghiệp vụ & truy vấn CSDL cho sản phẩm
│
├── models.py                  # Khai báo cấu trúc bảng CSDL 'products' (SQLAlchemy)
├── schemas.py                 # Pydantic schemas validate request/response
├── database.py                # Kết nối CSDL riêng biệt (products.db) & seed dữ liệu
├── auth_middleware.py         # Xác thực liên dịch vụ với AuthService (Bài 2)
├── main.py                    # Khởi tạo FastAPI app, định tuyến API & Dashboard
├── test_service.py            # Script kiểm thử tự động toàn diện 100% API
├── requirements.txt           # Danh sách các thư viện cần thiết
├── run_product_service.bat    # File chạy nhanh ProductService (Port 8001)
├── run_both_services.bat      # Chạy đồng thời cả Bài 2 (Port 8000) & Bài 3 (Port 8001)
├── run_both_services.ps1      # Script PowerShell chạy song song 2 dịch vụ
└── README.md                  # Hướng dẫn chi tiết
```

---

## 3. Thiết kế Cơ sở Dữ liệu

Bảng **`products`** được lưu trữ trong CSDL riêng (`products.db`):

| Tên cột | Kiểu dữ liệu | Ràng buộc | Mô tả |
| :--- | :--- | :--- | :--- |
| `id` | `INT` | PRIMARY KEY, AUTO_INCREMENT | ID duy nhất của từng sản phẩm |
| `name` | `VARCHAR(255)` | NOT NULL, INDEX | Tên sản phẩm |
| `description` | `TEXT` | NULLABLE | Mô tả chi tiết sản phẩm |
| `price` | `DECIMAL(10, 2)` | NOT NULL, > 0 | Giá bán sản phẩm |
| `quantity` | `INT` | NOT NULL, >= 0 | Số lượng sản phẩm tồn kho |
| `created_at` | `TIMESTAMP` | NOT NULL, DEFAULT NOW | Thời điểm tạo sản phẩm |
| `updated_at` | `TIMESTAMP` | NOT NULL, DEFAULT NOW | Thời điểm cập nhật cuối cùng |

---

## 4. Thiết kế RESTful API

| Method | Endpoint | Yêu cầu Xác thực | Mô tả chức năng |
| :--- | :--- | :---: | :--- |
| `GET` | `/products` | Không | Lấy danh sách tất cả sản phẩm (hỗ trợ tìm kiếm & phân trang) |
| `GET` | `/products/{id}` | Không | Xem chi tiết 1 sản phẩm theo ID (trả về 404 nếu không tìm thấy) |
| `POST` | `/products` | **Có** (Bearer Token) | Thêm sản phẩm mới (HTTP 201 Created) |
| `PUT` | `/products/{id}` | **Có** (Bearer Token) | Cập nhật thông tin sản phẩm theo ID |
| `DELETE` | `/products/{id}` | **Có** (Bearer Token) | Xóa sản phẩm khỏi CSDL |
| `GET` | `/health` | Không | Kiểm tra trạng thái hoạt động của Service |
| `GET` | `/docs` | Không | Giao diện Swagger UI tương tác trực tiếp |
| `GET` | `/` | Không | Dashboard trực quan kiểm thử CRUD và đăng nhập |

---

## 5. Cơ chế Xác thực Liên dịch vụ (SOA Inter-Service Auth)

Theo nguyên tắc SOA, khi người dùng thực hiện các thao tác thay đổi dữ liệu (`POST`, `PUT`, `DELETE`):
1. Client gửi HTTP Request kèm Header: `Authorization: Bearer <token>`.
2. `ProductService` (Port 8001) trích xuất token và thực hiện gọi HTTP Request sang `AuthService` (Bài thực hành số 2) tại:
   ```
   GET http://localhost:8000/auth
   Header: Authorization: Bearer <token>
   ```
3. Nếu `AuthService` phản hồi HTTP 200 (`{"message": "Token is valid", "userName": "admin"}`): Request được phê duyệt và chuyển tiếp cho `ProductController` xử lý.
4. Nếu Token sai hoặc hết hạn: `AuthService` trả về 401, `ProductService` lập tức chặn truy cập và trả về HTTP 401 Unauthorized.
5. Trường hợp `AuthService` ngoại tuyến, `ProductService` tự động chuyển sang cơ chế kiểm tra JWT cục bộ (với `SECRET_KEY` dùng chung của Bài 2) để đảm bảo tính sẵn sàng cao (High Availability).

---

## 6. Hướng dẫn Khởi chạy & Kiểm thử

### Bước 1: Khởi chạy cả 2 dịch vụ (Bài 2 & Bài 3)
Chỉ cần nhấp đúp chuột vào file:
```cmd
run_both_services.bat
```
*(Hệ thống sẽ tự động bật 2 cửa sổ CMD: một cửa sổ chạy Bài 2 tại port 8000, một cửa sổ chạy Bài 3 tại port 8001 và tự động mở trình duyệt tới `http://127.0.0.1:8001/`)*

Hoặc nếu muốn khởi chạy thủ công:
- **Cửa sổ 1 (Bài 2):**
  ```bash
  cd D:\SOA\BaiThucHanh2
  python -m uvicorn main:app --port 8000 --reload
  ```
- **Cửa sổ 2 (Bài 3):**
  ```bash
  cd C:\Users\Admin\.gemini\antigravity-ide\scratch\BaiThucHanh3
  python -m uvicorn main:app --port 8001 --reload
  ```

---

### Bước 2: Kiểm thử tự động (Automated Test)
Chạy script kiểm thử:
```bash
python test_service.py
```
Kết quả kiểm thử tự động kiểm tra:
- Khởi tạo & Health check service
- Lấy danh sách sản phẩm (GET /products)
- Lấy chi tiết sản phẩm (GET /products/1)
- Thử thêm sản phẩm khi không có token (bị chặn 401)
- Đăng nhập lấy Token từ AuthService Bài 2
- Thêm sản phẩm mới có Token (POST /products -> 201 Created)
- Cập nhật sản phẩm có Token (PUT /products/{id} -> 200 OK)
- Xóa sản phẩm có Token (DELETE /products/{id} -> 200 OK)
- Kiểm tra lại sản phẩm đã xóa (GET /products/{id} -> 404 Not Found)

---

### Bước 3: Kiểm thử bằng Swagger UI hoặc Trực Quan (Giao diện Web)
1. Truy cập: **`http://localhost:8001/`** để sử dụng giao diện trực quan:
   - Bấm nút **"Đăng Nhập Qua AuthService (Bài 2)"** (tài khoản `admin` / `123456`) để nhận Token.
   - Thêm, sửa, xóa sản phẩm trực tiếp trên giao diện.
2. Truy cập: **`http://localhost:8001/docs`** để dùng Swagger UI chuẩn OpenAPI 3.0.

---

### Ví dụ Lệnh cURL Kiểm thử Trực Tiếp:

**1. Lấy danh sách sản phẩm:**
```bash
curl -X GET "http://127.0.0.1:8001/products"
```

**2. Đăng nhập qua Bài 2 lấy token:**
```bash
curl -X POST "http://127.0.0.1:8000/login" -H "Content-Type: application/json" -d "{\"userName\": \"admin\", \"password\": \"123456\"}"
```

**3. Thêm sản phẩm mới (sử dụng Token lấy được):**
```bash
curl -X POST "http://127.0.0.1:8001/products" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <TOKEN_CỦA_BẠN>" \
     -d "{\"name\": \"Tai nghe AirPods Pro\", \"description\": \"Chống ồn chủ động\", \"price\": 5490000.00, \"quantity\": 20}"
```
