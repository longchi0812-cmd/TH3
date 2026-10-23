@echo off
title Khoi Chay He Thong SOA (Bai 2 + Bai 3)
echo ====================================================================
echo  KHOI CHAY HE THONG SOA: BAI THUC HANH 2 + BAI THUC HANH 3
echo ====================================================================

set "AUTH_DIR=D:\SOA\BaiThucHanh2"
set "PRODUCT_DIR=%~dp0"

echo [1/2] Dang khoi chay AuthService (Bai 2) tai cong 8000...
start "AuthService (Bai 2) - Port 8000" /D "%AUTH_DIR%" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"

echo Dang cho AuthService khoi dong...
ping 127.0.0.1 -n 3 > nul

echo [2/2] Dang khoi chay ProductService (Bai 3) tai cong 8001...
start "ProductService (Bai 3) - Port 8001" /D "%PRODUCT_DIR%." cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload"

echo ====================================================================
echo  CA 2 DICH VU DA DUOC MO TREN 2 CUA SO CMD RIENG BIET:
echo  1. AuthService (Bai 2):       http://127.0.0.1:8000
echo  2. ProductService (Bai 3):    http://127.0.0.1:8001
echo  3. Swagger Docs San Pham:     http://127.0.0.1:8001/docs
echo ====================================================================

echo Dang cho ProductService san sang va mo trinh duyet...
ping 127.0.0.1 -n 4 > nul
start http://127.0.0.1:8001/
