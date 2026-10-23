from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone

app = FastAPI()
security = HTTPBearer()

# Khóa bí mật dùng để tạo và kiểm tra JWT
SECRET_KEY = "my_secret_key_123"

# -------------------------
# Dữ liệu người dùng mẫu
# -------------------------
users = [
    {
        "IdUser": 1,
        "UserName": "admin",
        "Password": "123456",
        "Token": ""
    },
    {
        "IdUser": 2,
        "UserName": "user",
        "Password": "123456",
        "Token": ""
    }
]

# -------------------------
# Model đăng nhập
# -------------------------
class LoginRequest(BaseModel):
    userName: str
    password: str


# -------------------------
# Tạo JWT
# -------------------------
def create_token(username):
    payload = {
        "userName": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token


# -------------------------
# Middleware xác thực JWT
# -------------------------
@app.middleware("http")
async def jwt_middleware(request: Request, call_next):

    # Các API không cần kiểm tra token
    public_paths = ["/", "/login", "/docs", "/openapi.json"]

    if request.url.path in public_paths:
        return await call_next(request)

    # Lấy Authorization Header
    authorization = request.headers.get("Authorization")

    if not authorization:
        return JSONResponse(
            status_code=401,
            content={"message": "Missing token"}
        )

    # Kiểm tra dạng Bearer Token
    if not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid Authorization header"}
        )

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )

        request.state.user = payload["userName"]

    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=401,
            content={"message": "Token expired"}
        )

    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=401,
            content={"message": "Invalid token"}
        )

    return await call_next(request)


# -------------------------
# API trang chủ
# -------------------------
@app.get("/")
def home():
    return {
        "message": "API Bai Thuc Hanh 2"
    }


# -------------------------
# API LOGIN
# -------------------------
@app.post("/login")
def login(data: LoginRequest):

    for user in users:

        if (
            user["UserName"] == data.userName
            and user["Password"] == data.password
        ):

            token = create_token(data.userName)

            # Lưu token vào bảng User
            user["Token"] = token

            return {
                "message": "Login successful",
                "userName": data.userName,
                "token": token
            }

    raise HTTPException(
        status_code=401,
        detail="Username or password is incorrect"
    )


# -------------------------
# API AUTH
# -------------------------
@app.get("/auth")
def auth(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return {
        "message": "Token is valid",
        "userName": request.state.user
    }

# -------------------------
# API HELLO WORLD
# -------------------------
@app.get("/hello")
def hello(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    return {
        "message": "Hello World",
        "userName": request.state.user
    }