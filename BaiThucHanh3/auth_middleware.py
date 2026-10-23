"""
Middleware / Dependency Xác thực người dùng qua AuthService (Bài thực hành số 2)
Tuân theo kiến trúc Hướng dịch vụ (SOA):
- ProductService độc lập, gọi HTTP sang AuthService (Bài 2) tại /auth để kiểm tra tính hợp lệ của Token.
- Hỗ trợ fallback giải mã JWT cục bộ (với SECRET_KEY của Bài 2) khi AuthService offline, đảm bảo tính sẵn sàng cao.
"""
import os
from typing import Optional
from fastapi import Header, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
import jwt

# Cấu hình địa chỉ AuthService từ Bài 2 (mặc định localhost:8000)
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "my_secret_key_123")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# Security scheme cho Swagger UI (Hiển thị nút Authorize màu xanh trên Swagger UI)
security = HTTPBearer(auto_error=False)

async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Dependency kiểm tra tính hợp lệ của Token thông qua AuthService (Bài thực hành số 2).
    Hỗ trợ nhận Token qua HTTPBearer (Swagger UI) lẫn Header Authorization trực tiếp.
    Bắn lỗi HTTP 401 Unauthorized nếu token thiếu, sai hoặc hết hạn.
    """
    token = None
    if credentials and credentials.credentials:
        token = credentials.credentials.strip()
    elif authorization:
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1].strip()
        else:
            token = authorization.strip()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Yêu cầu đăng nhập: Thiếu Authorization header (Bearer token). Vui lòng đăng nhập qua AuthService (Bài 2).",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # -------------------------------------------------------------
    # 1. GỌI SANG AUTH SERVICE (BÀI THỰC HÀNH 2) QUA HTTP REST API
    # -------------------------------------------------------------
    auth_service_online = False
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(
                f"{AUTH_SERVICE_URL}/auth",
                headers={"Authorization": f"Bearer {token}"}
            )
            auth_service_online = True

            if response.status_code == 200:
                data = response.json()
                return {
                    "username": data.get("userName"),
                    "verified_via": "AuthService_Bai2 (Remote HTTP)",
                    "auth_service_url": AUTH_SERVICE_URL,
                    "details": data
                }
            elif response.status_code == 401:
                # AuthService Bài 2 trả về 401
                error_msg = response.json().get("message", "Token không hợp lệ hoặc đã hết hạn")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Xác thực thất bại từ AuthService Bài 2: {error_msg}",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                # Phản hồi lỗi khác từ AuthService
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Lỗi phản hồi từ AuthService: HTTP {response.status_code}",
                    headers={"WWW-Authenticate": "Bearer"},
                )

    except httpx.RequestError as exc:
        # AuthService chưa bật hoặc không kết nối được
        print(f"[ProductService] Cảnh báo SOA: Không thể kết nối tới AuthService tại {AUTH_SERVICE_URL} ({exc}). Chuyển sang fallback giải mã JWT.")

    # -------------------------------------------------------------
    # 2. FALLBACK NỘI BỘ NẾU AUTH SERVICE CHƯA BẬT (DÙNG CHUNG SECRET_KEY)
    # -------------------------------------------------------------
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {
            "username": payload.get("userName"),
            "verified_via": "Local_JWT_Fallback (Shared Secret)",
            "auth_service_url": AUTH_SERVICE_URL,
            "details": payload
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token đã hết hạn sử dụng. Vui lòng đăng nhập lại qua AuthService (Bài 2).",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ. Truy cập bị từ chối.",
            headers={"WWW-Authenticate": "Bearer"},
        )
