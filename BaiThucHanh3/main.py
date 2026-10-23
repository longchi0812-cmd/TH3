"""
BÀI THỰC HÀNH SỐ 3 - DỊCH VỤ QUẢN LÝ SẢN PHẨM (PRODUCT MANAGEMENT SERVICE)
Kiến trúc Hướng dịch vụ (SOA - Service-Oriented Architecture):
- Cổng dịch vụ riêng: localhost:8001
- CSDL riêng: products.db (Database-per-Service)
- RESTful API đầy đủ: GET, POST, PUT, DELETE /products
- Xác thực liên dịch vụ (Inter-service Auth) qua AuthService của Bài thực hành 2 (localhost:8000/auth)
"""
import sys
import os
from contextlib import asynccontextmanager
from typing import List, Optional

import sys
import os

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
import httpx

from database import get_db, init_db
from schemas import ProductCreate, ProductUpdate, ProductResponse
from controllers.product_controller import ProductController
from auth_middleware import verify_token, AUTH_SERVICE_URL

# Lifespan: Khởi tạo bảng CSDL và nạp dữ liệu ban đầu
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("[ProductService] Khoi tao Co so du lieu rieng (products.db)...")
    init_db()
    yield
    print("[ProductService] Dung dich vu.")

app = FastAPI(
    title="Product Management Service (Bài Thực Hành Số 3)",
    description=(
        "Dịch vụ quản lý sản phẩm độc lập tuân theo kiến trúc Hướng dịch vụ (SOA).\n"
        "- Cổng riêng: localhost:8001\n"
        "- CSDL riêng: products.db\n"
        "- Xác thực liên dịch vụ qua AuthService Bài 2 (localhost:8000/auth)"
    ),
    version="1.0.0",
    lifespan=lifespan
)

# 1. Cấu hình CORS để cho phép gọi API từ mọi Frontend / Browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================================
# RESTFUL API CÁC ENDPOINT QUẢN LÝ SẢN PHẨM (THEO YÊU CẦU ĐỀ BÀI)
# =====================================================================

# API 1: GET /products - Lấy danh sách tất cả các sản phẩm
@app.get(
    "/products",
    response_model=List[ProductResponse],
    summary="Lấy danh sách tất cả các sản phẩm",
    tags=["Product Management"]
)
def get_all_products(
    skip: int = Query(0, ge=0, description="Số lượng bản ghi bỏ qua (phân trang)"),
    limit: int = Query(100, ge=1, le=500, description="Số lượng bản ghi tối đa lấy về"),
    search: Optional[str] = Query(None, description="Tìm kiếm theo tên sản phẩm"),
    db: Session = Depends(get_db)
):
    """
    **GET /products**: Lấy danh sách sản phẩm trong kho.
    - Hỗ trợ phân trang: `skip`, `limit`.
    - Hỗ trợ tìm kiếm theo tên: `search`.
    """
    products = ProductController.get_all(db, skip=skip, limit=limit, search=search)
    return products


# API 2: GET /products/{id} - Lấy thông tin chi tiết một sản phẩm
@app.get(
    "/products/{id}",
    response_model=ProductResponse,
    summary="Lấy thông tin chi tiết một sản phẩm",
    tags=["Product Management"]
)
def get_product_by_id(
    id: int,
    db: Session = Depends(get_db)
):
    """
    **GET /products/{id}**: Lấy thông tin chi tiết sản phẩm theo ID.
    - Trả về mã lỗi 404 nếu không tìm thấy.
    """
    product = ProductController.get_by_id(db, product_id=id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sản phẩm có ID = {id} trong hệ thống!"
        )
    return product


# API 3: POST /products - Thêm một sản phẩm mới (Xác thực qua Bài 2)
@app.post(
    "/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Thêm một sản phẩm mới (Yêu cầu xác thực qua AuthService Bài 2)",
    tags=["Product Management"]
)
def create_product(
    product_in: ProductCreate,
    db: Session = Depends(get_db),
    auth_user: dict = Depends(verify_token)
):
    """
    **POST /products**: Thêm một sản phẩm mới vào CSDL.
    - **Yêu cầu xác thực**: Header `Authorization: Bearer <token>`.
    - Token được kiểm tra liên dịch vụ qua AuthService của Bài thực hành số 2.
    """
    new_product = ProductController.create(db, product_in=product_in)
    return new_product


# API 4: PUT /products/{id} - Cập nhật thông tin sản phẩm (Xác thực qua Bài 2)
@app.put(
    "/products/{id}",
    response_model=ProductResponse,
    summary="Cập nhật thông tin sản phẩm (Yêu cầu xác thực qua AuthService Bài 2)",
    tags=["Product Management"]
)
def update_product(
    id: int,
    product_in: ProductUpdate,
    db: Session = Depends(get_db),
    auth_user: dict = Depends(verify_token)
):
    """
    **PUT /products/{id}**: Cập nhật thông tin sản phẩm theo ID.
    - **Yêu cầu xác thực**: Header `Authorization: Bearer <token>`.
    - Trả về 404 nếu sản phẩm không tồn tại.
    """
    updated_product = ProductController.update(db, product_id=id, product_in=product_in)
    if not updated_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sản phẩm có ID = {id} để cập nhật!"
        )
    return updated_product


# API 5: DELETE /products/{id} - Xóa một sản phẩm (Xác thực qua Bài 2)
@app.delete(
    "/products/{id}",
    summary="Xóa một sản phẩm (Yêu cầu xác thực qua AuthService Bài 2)",
    tags=["Product Management"]
)
def delete_product(
    id: int,
    db: Session = Depends(get_db),
    auth_user: dict = Depends(verify_token)
):
    """
    **DELETE /products/{id}**: Xóa một sản phẩm khỏi CSDL.
    - **Yêu cầu xác thực**: Header `Authorization: Bearer <token>`.
    - Trả về 404 nếu không tìm thấy sản phẩm.
    """
    success = ProductController.delete(db, product_id=id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Không tìm thấy sản phẩm có ID = {id} để xóa!"
        )
    return {
        "success": True,
        "message": f"Đã xóa thành công sản phẩm có ID = {id} khỏi cơ sở dữ liệu.",
        "deleted_id": id,
        "operator": auth_user.get("username", "authenticated_user")
    }


# =====================================================================
# CÁC ENDPOINT PHỤ TRỢ (HEALTH CHECK, THÔNG TIN SOA & GIAO DIỆN WEB)
# =====================================================================

@app.get("/health", summary="Kiểm tra trạng thái Service", tags=["System"])
def health_check():
    """Kiểm tra dịch vụ ProductService có đang hoạt động bình thường không."""
    return {
        "status": "healthy",
        "service": "ProductManagementService",
        "port": 8001,
        "soa_role": "Domain Business Service",
        "database": "products.db (Isolated Database-per-service)",
        "auth_provider": AUTH_SERVICE_URL
    }

@app.get("/info", summary="Thông tin kiến trúc SOA", tags=["System"])
def get_soa_info():
    """Thông tin tổng quan về kiến trúc SOA của Bài Thực Hành 3."""
    return {
        "assignment": "BÀI THỰC HÀNH SỐ 3 - Xây dựng dịch vụ quản lý sản phẩm",
        "service_name": "ProductManagementService",
        "port": 8001,
        "database": "SQLite (products.db riêng biệt)",
        "auth_service": {
            "source": "Bài thực hành số 2",
            "url": AUTH_SERVICE_URL,
            "verify_endpoint": f"{AUTH_SERVICE_URL}/auth"
        },
        "endpoints": {
            "GET /products": "Lấy danh sách tất cả sản phẩm",
            "GET /products/{id}": "Lấy chi tiết 1 sản phẩm",
            "POST /products": "Thêm sản phẩm mới (yêu cầu Bearer Token)",
            "PUT /products/{id}": "Cập nhật sản phẩm (yêu cầu Bearer Token)",
            "DELETE /products/{id}": "Xóa sản phẩm (yêu cầu Bearer Token)",
            "GET /docs": "Tài liệu Swagger tương tác trực tiếp",
            "GET /redoc": "Tài liệu ReDoc"
        }
    }

@app.post("/api/auth/login", summary="Proxy đăng nhập qua AuthService Bài 2", tags=["System"])
async def login_proxy(payload: dict):
    """
    Proxy gọi sang AuthService Bài 2 tại port 8000.
    Tránh hoàn toàn lỗi CORS trên trình duyệt khi gọi từ localhost:8001 sang localhost:8000.
    """
    username = payload.get("userName")
    password = payload.get("password")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{AUTH_SERVICE_URL}/login",
                json={"userName": username, "password": password}
            )
            return JSONResponse(status_code=res.status_code, content=res.json())
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Không thể kết nối tới AuthService Bài 2 tại {AUTH_SERVICE_URL}: {str(exc)}"
        )

# =====================================================================
# GIAO DIỆN TRỰC QUAN DASHBOARD KIỂM THỬ TẠI ROOT (/)
# =====================================================================
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def serve_dashboard():
    """Giao diện Web trực quan: Màn hình Đăng nhập trước, vào Trang chính sau khi xác thực."""
    html_content = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hệ Thống SOA - Quản Lý Sản Phẩm (Bài Thực Hành Số 3)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #2563eb;
            --primary-hover: #1d4ed8;
            --success: #16a34a;
            --warning: #d97706;
            --danger: #dc2626;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #64748b;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: var(--bg);
            color: var(--text-main);
            min-height: 100vh;
        }

        /* ==============================================================
           MÀN HÌNH 1: ĐĂNG NHẬP
           ============================================================== */
        #loginScreen {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 24px;
            animation: fadeIn 0.3s ease;
        }
        .login-card {
            width: 100%;
            max-width: 400px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 32px 28px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        .login-header {
            text-align: center;
            margin-bottom: 24px;
        }
        .login-header h1 {
            font-size: 20px;
            font-weight: 700;
            color: var(--text-main);
        }
        .login-error {
            background: #fef2f2;
            border: 1px solid #fecaca;
            color: #dc2626;
            padding: 10px 14px;
            border-radius: 6px;
            font-size: 13px;
            margin-bottom: 16px;
            display: none;
        }
        .service-status-bar {
            margin-top: 24px;
            padding-top: 16px;
            border-top: 1px solid var(--border);
            display: flex;
            justify-content: space-around;
            font-size: 11px;
            color: var(--text-muted);
        }
        .status-dot {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #16a34a;
            border-radius: 50%;
            margin-right: 6px;
        }

        /* ==============================================================
           MÀN HÌNH 2: TRANG CHÍNH QUẢN LÝ SẢN PHẨM
           ============================================================== */
        #mainScreen {
            display: none;
            padding: 24px;
            animation: fadeIn 0.3s ease;
        }
        .container { max-width: 1250px; margin: 0 auto; }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
        }
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-soa { background: #e0e7ff; color: #3730a3; border: 1px solid #c7d2fe; }
        .badge-port { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
        .badge-user { background: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; }
        .grid-layout { display: grid; grid-template-columns: 360px 1fr; gap: 20px; }
        @media (max-width: 960px) { .grid-layout { grid-template-columns: 1fr; } }
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
            margin-bottom: 20px;
        }
        .card h2 {
            font-size: 17px;
            font-weight: 700;
            margin-bottom: 16px;
            color: var(--text-main);
        }
        .form-group { margin-bottom: 14px; }
        label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; color: #334155; }
        input, textarea {
            width: 100%;
            padding: 9px 12px;
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            color: var(--text-main);
            font-size: 14px;
            font-family: inherit;
            outline: none;
            transition: all 0.2s;
        }
        input:focus, textarea:focus {
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
        }
        button {
            cursor: pointer;
            font-family: inherit;
            font-weight: 600;
            border: none;
            border-radius: 6px;
            padding: 9px 16px;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-size: 13px;
        }
        .btn-primary { background: var(--primary); color: #fff; width: 100%; }
        .btn-primary:hover { background: var(--primary-hover); }
        .btn-success { background: var(--success); color: #fff; }
        .btn-danger { background: var(--danger); color: #fff; padding: 6px 12px; font-size: 12px; }
        .btn-danger:hover { background: #b91c1c; }
        .btn-edit { background: #0284c7; color: #fff; padding: 6px 12px; font-size: 12px; }
        .btn-edit:hover { background: #0369a1; }
        .btn-secondary { background: #f8fafc; color: #334155; border: 1px solid #cbd5e1; }
        .btn-secondary:hover { background: #f1f5f9; }
        .btn-logout { background: #ffffff; color: #dc2626; border: 1px solid #fca5a5; padding: 5px 12px; font-size: 12px; }
        .btn-logout:hover { background: #fef2f2; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px; }
        th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid #e2e8f0; }
        th { background: #f8fafc; color: #475569; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px; }
        tr:hover td { background: #f8fafc; }
        .price { color: #0284c7; font-weight: 700; }
        .qty-badge { background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
        .actions { display: flex; gap: 6px; }
        .top-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; gap: 12px; }
        .search-box { max-width: 280px; }
        .links-bar { display: flex; gap: 8px; margin-top: 8px; }
        .link-btn { font-size: 12px; text-decoration: none; color: #2563eb; background: #f1f5f9; border: 1px solid #e2e8f0; padding: 4px 10px; border-radius: 5px; }
        .link-btn:hover { background: #e2e8f0; }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
    </style>
</head>
<body>

    <!-- ==============================================================
         MÀN HÌNH 1: GIAO DIỆN ĐĂNG NHẬP (AUTH SERVICE - BÀI 2)
         ============================================================== -->
    <div id="loginScreen">
        <div class="login-card">
            <div class="login-header">
                <h1>Quản Lý Sản Phẩm</h1>
            </div>

            <div id="loginErrorMsg" class="login-error"></div>

            <form onsubmit="handleLoginSubmit(event)">
                <div class="form-group">
                    <label>Tên tài khoản</label>
                    <input type="text" id="loginUser" required placeholder="Nhập tên tài khoản...">
                </div>
                <div class="form-group" style="margin-bottom: 20px;">
                    <label>Mật khẩu</label>
                    <input type="password" id="loginPass" required placeholder="Nhập mật khẩu...">
                </div>
                <button type="submit" id="btnLoginSubmit" class="btn-primary" style="padding: 12px;">
                    Đăng Nhập
                </button>
            </form>
        </div>
    </div>

    <!-- ==============================================================
         MÀN HÌNH 2: TRANG CHÍNH QUẢN LÝ SẢN PHẨM (SAU KHI ĐĂNG NHẬP)
         ============================================================== -->
    <div id="mainScreen">
        <div class="container">
            <header>
                <div>
                    <h1 style="font-size: 20px; font-weight: 800; display: flex; align-items: center; gap: 10px;">
                        Quản Lý Sản Phẩm
                    </h1>
                </div>
                <div style="display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span class="badge badge-user"><b id="headerUserName">admin</b></span>
                        <button class="btn-logout" onclick="logout()">Đăng Xuất</button>
                    </div>
                    <div style="display: flex; gap: 6px;">
                        <span class="badge badge-port">Port: 8001 (ProductService)</span>
                        <span class="badge badge-soa">Auth: Port 8000</span>
                    </div>
                </div>
            </header>

            <div class="grid-layout">
                <!-- Cột trái: Thêm / Sửa Sản Phẩm -->
                <div>
                    <div class="card">
                        <h2 id="formTitle">Thêm Sản Phẩm Mới</h2>
                        <input type="hidden" id="editProductId">
                        <div class="form-group">
                            <label>Tên sản phẩm *</label>
                            <input type="text" id="pName" placeholder="VD: Bàn phím cơ không dây...">
                        </div>
                        <div class="form-group">
                            <label>Mô tả chi tiết</label>
                            <textarea id="pDesc" rows="3" placeholder="Mô tả cấu hình, thông số..."></textarea>
                        </div>
                        <div class="form-group">
                            <label>Giá sản phẩm (VNĐ) *</label>
                            <input type="number" id="pPrice" step="1000" placeholder="VD: 1850000">
                        </div>
                        <div class="form-group">
                            <label>Số lượng trong kho *</label>
                            <input type="number" id="pQty" value="10" min="0">
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button id="btnSave" class="btn-primary" onclick="saveProduct()">Lưu Sản Phẩm</button>
                            <button id="btnCancelEdit" class="btn-secondary" style="display:none;" onclick="cancelEdit()">Hủy</button>
                        </div>
                    </div>
                </div>

                <!-- Cột phải: Danh Sách Sản Phẩm -->
                <div>
                    <div class="card">
                        <div class="top-bar">
                            <h2>Danh Sách Sản Phẩm</h2>
                            <div style="display: flex; gap: 10px;">
                                <input type="text" id="searchKeyword" class="search-box" placeholder="Tìm theo tên hoặc mã ID (#1, #2...)" oninput="loadProducts()" onkeyup="if(event.key==='Enter') loadProducts()">
                                <button class="btn-secondary" onclick="loadProducts()">Tìm kiếm</button>
                            </div>
                        </div>

                        <div style="overflow-x: auto;">
                            <table>
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Tên Sản Phẩm</th>
                                        <th>Mô Tả</th>
                                        <th>Giá (VNĐ)</th>
                                        <th>Kho</th>
                                        <th>Cập Nhật</th>
                                        <th>Hành Động</th>
                                    </tr>
                                </thead>
                                <tbody id="productTableBody">
                                    <tr><td colspan="7" style="text-align:center; padding: 20px;">Đang tải dữ liệu sản phẩm...</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let currentToken = localStorage.getItem('soa_jwt_token') || '';
        let currentUser = localStorage.getItem('soa_username') || '';

        // Kiểm tra trạng thái đăng nhập để chuyển màn hình
        function checkAuthState() {
            currentToken = localStorage.getItem('soa_jwt_token') || '';
            currentUser = localStorage.getItem('soa_username') || '';

            const loginScreen = document.getElementById('loginScreen');
            const mainScreen = document.getElementById('mainScreen');
            const headerUserName = document.getElementById('headerUserName');

            if (currentToken) {
                // ĐÃ ĐĂNG NHẬP: Ẩn login, hiện trang chính
                loginScreen.style.display = 'none';
                mainScreen.style.display = 'block';
                headerUserName.innerText = currentUser || 'admin';
                loadProducts();
            } else {
                // CHƯA ĐĂNG NHẬP: Hiện màn hình login, ẩn trang chính
                loginScreen.style.display = 'flex';
                mainScreen.style.display = 'none';
            }
        }

        function fillDemo(u, p) {
            document.getElementById('loginUser').value = u;
            document.getElementById('loginPass').value = p;
        }

        async function handleLoginSubmit(event) {
            event.preventDefault();
            const u = document.getElementById('loginUser').value.trim();
            const p = document.getElementById('loginPass').value.trim();
            const errorBox = document.getElementById('loginErrorMsg');
            const btn = document.getElementById('btnLoginSubmit');

            errorBox.style.display = 'none';
            btn.disabled = true;
            btn.innerText = 'Đang xác thực...';

            try {
                // Gọi API Proxy của ProductService (gọi tiếp sang AuthService Bài 2)
                const res = await fetch('/api/auth/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ userName: u, password: p })
                });
                const data = await res.json();

                if (res.ok && data.token) {
                    currentToken = data.token;
                    currentUser = data.userName || u;
                    localStorage.setItem('soa_jwt_token', currentToken);
                    localStorage.setItem('soa_username', currentUser);
                    checkAuthState();
                } else {
                    errorBox.innerText = 'Đăng nhập thất bại: ' + (data.detail || data.message || 'Sai tài khoản hoặc mật khẩu!');
                    errorBox.style.display = 'block';
                }
            } catch (err) {
                errorBox.innerText = 'Lỗi kết nối tới AuthService: ' + (err.message || err);
                errorBox.style.display = 'block';
            } finally {
                btn.disabled = false;
                btn.innerText = 'Đăng Nhập';
            }
        }

        function logout() {
            // Xóa sạch Token và User khỏi LocalStorage
            localStorage.removeItem('soa_jwt_token');
            localStorage.removeItem('soa_username');
            currentToken = '';
            currentUser = '';

            // Chuyển màn hình ngay lập tức về Đăng nhập
            const loginScreen = document.getElementById('loginScreen');
            const mainScreen = document.getElementById('mainScreen');
            if (loginScreen) loginScreen.style.display = 'flex';
            if (mainScreen) mainScreen.style.display = 'none';

            // Reset lại form đăng nhập
            const uInput = document.getElementById('loginUser');
            const pInput = document.getElementById('loginPass');
            if (uInput) uInput.value = '';
            if (pInput) pInput.value = '';

            const errorBox = document.getElementById('loginErrorMsg');
            if (errorBox) {
                errorBox.style.display = 'none';
            }
        }

        async function loadProducts() {
            const search = document.getElementById('searchKeyword').value;
            const url = search ? `/products?search=${encodeURIComponent(search)}` : '/products';
            const tbody = document.getElementById('productTableBody');
            try {
                const res = await fetch(url);
                const products = await res.json();
                if (!res.ok) throw new Error(products.detail || 'Lỗi tải danh sách');
                if (products.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center; padding: 20px; color: var(--text-muted);">Không có sản phẩm nào phù hợp.</td></tr>';
                    return;
                }
                tbody.innerHTML = products.map(p => `
                    <tr>
                        <td><b>#${p.id}</b></td>
                        <td><b>${escapeHtml(p.name)}</b></td>
                        <td style="max-width: 250px; color: var(--text-muted); font-size: 12px;">${escapeHtml(p.description || '')}</td>
                        <td class="price">${Number(p.price).toLocaleString('vi-VN')} đ</td>
                        <td><span class="qty-badge">${p.quantity}</span></td>
                        <td style="font-size: 11px; color: var(--text-muted);">${new Date(p.updated_at).toLocaleString('vi-VN')}</td>
                        <td>
                            <div class="actions">
                                <button class="btn-edit" onclick='startEdit(${JSON.stringify(p)})'>Sửa</button>
                                <button class="btn-danger" onclick='deleteProduct(${p.id})'>Xóa</button>
                            </div>
                        </td>
                    </tr>
                `).join('');
            } catch (err) {
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color: #ef4444; padding: 20px;">Lỗi: ${err.message}</td></tr>`;
            }
        }

        async function saveProduct() {
            const editId = document.getElementById('editProductId').value;
            const name = document.getElementById('pName').value.trim();
            const desc = document.getElementById('pDesc').value.trim();
            const price = parseFloat(document.getElementById('pPrice').value);
            const qty = parseInt(document.getElementById('pQty').value, 10);

            if (!name || isNaN(price) || isNaN(qty)) {
                alert('Vui lòng nhập đầy đủ Tên, Giá (> 0) và Số lượng (>= 0)!');
                return;
            }

            const headers = { 'Content-Type': 'application/json' };
            if (currentToken) {
                headers['Authorization'] = 'Bearer ' + currentToken;
            }

            try {
                let res, data;
                if (editId) {
                    res = await fetch(`/products/${editId}`, {
                        method: 'PUT',
                        headers: headers,
                        body: JSON.stringify({ name, description: desc, price, quantity: qty })
                    });
                } else {
                    res = await fetch('/products', {
                        method: 'POST',
                        headers: headers,
                        body: JSON.stringify({ name, description: desc, price, quantity: qty })
                    });
                }
                data = await res.json();
                if (!res.ok) {
                    if (res.status === 401) {
                        alert('Phiên đăng nhập đã hết hạn! Vui lòng đăng nhập lại.');
                        logout();
                        return;
                    }
                    alert('Thất bại: ' + (data.detail || JSON.stringify(data)));
                    return;
                }
                alert(editId ? 'Cập nhật sản phẩm thành công!' : 'Thêm sản phẩm mới thành công!');
                cancelEdit();
                loadProducts();
            } catch (err) {
                alert('Lỗi gửi request: ' + err.message);
            }
        }

        function startEdit(product) {
            document.getElementById('editProductId').value = product.id;
            document.getElementById('formTitle').innerText = `Cập Nhật Sản Phẩm #${product.id}`;
            document.getElementById('pName').value = product.name;
            document.getElementById('pDesc').value = product.description || '';
            document.getElementById('pPrice').value = product.price;
            document.getElementById('pQty').value = product.quantity;
            document.getElementById('btnSave').innerText = 'Lưu Cập Nhật';
            document.getElementById('btnCancelEdit').style.display = 'inline-flex';
        }

        function cancelEdit() {
            document.getElementById('editProductId').value = '';
            document.getElementById('formTitle').innerText = 'Thêm Sản Phẩm Mới';
            document.getElementById('pName').value = '';
            document.getElementById('pDesc').value = '';
            document.getElementById('pPrice').value = '';
            document.getElementById('pQty').value = '10';
            document.getElementById('btnSave').innerText = 'Lưu Sản Phẩm';
            document.getElementById('btnCancelEdit').style.display = 'none';
        }

        async function deleteProduct(id) {
            if (!confirm(`Bạn có chắc chắn muốn xóa sản phẩm ID #${id} không?`)) return;

            const headers = {};
            if (currentToken) {
                headers['Authorization'] = 'Bearer ' + currentToken;
            }

            try {
                const res = await fetch(`/products/${id}`, {
                    method: 'DELETE',
                    headers: headers
                });
                const data = await res.json();
                if (!res.ok) {
                    if (res.status === 401) {
                        alert('Phiên đăng nhập đã hết hạn! Vui lòng đăng nhập lại.');
                        logout();
                        return;
                    }
                    alert('Xóa thất bại: ' + (data.detail || JSON.stringify(data)));
                    return;
                }
                alert(data.message || 'Đã xóa thành công!');
                loadProducts();
            } catch (err) {
                alert('Lỗi: ' + err.message);
            }
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // Tự động kiểm tra phiên đăng nhập ngay khi vào trang
        checkAuthState();
    </script>
</body>
</html>
"""
    return HTMLResponse(content=html_content)

# =====================================================================
# CHẠY TRỰC TIẾP QUA PYTHON MAIN.PY
# =====================================================================
if __name__ == "__main__":
    import uvicorn
    # Cổng riêng biệt cho ProductService (mặc định 8001 theo yêu cầu SOA)
    port = int(os.getenv("PORT", os.getenv("PRODUCT_PORT", 8001)))
    print("============================================================")
    print(" KHOI CHAY PRODUCT MANAGEMENT SERVICE (BAI THUC HANH 3)")
    print(f" - Dia chi: http://127.0.0.1:{port}")
    print(f" - Swagger Docs: http://127.0.0.1:{port}/docs")
    print(f" - Xac thuc qua AuthService Bai 2: {AUTH_SERVICE_URL}")
    print("============================================================")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
