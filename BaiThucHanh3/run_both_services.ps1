# Script PowerShell khởi chạy đồng thời Bài 2 (Auth) và Bài 3 (Products)
$authDir = "D:\SOA\BaiThucHanh2"
$productDir = $PSScriptRoot

Write-Host "====================================================================" -ForegroundColor Cyan
Write-Host " KHỞI CHẠY HỆ THỐNG SOA: BÀI THỰC HÀNH 2 + BÀI THỰC HÀNH 3" -ForegroundColor Cyan
Write-Host "====================================================================" -ForegroundColor Cyan

Write-Host "[1/2] Đang khởi chạy AuthService (Bài 2) tại cổng 8000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$authDir'; python -m uvicorn main:app --port 8000 --reload"

Start-Sleep -Seconds 2

Write-Host "[2/2] Đang khởi chạy ProductService (Bài 3) tại cổng 8001..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$productDir'; python -m uvicorn main:app --port 8001 --reload"

Write-Host ""
Write-Host "Đã khởi chạy 2 dịch vụ trên 2 cửa sổ riêng biệt!" -ForegroundColor Green
Write-Host "1. AuthService (Bài 2):       http://localhost:8000" -ForegroundColor White
Write-Host "2. ProductService (Bài 3):    http://localhost:8001" -ForegroundColor White
Write-Host "3. Swagger UI Sản Phẩm:       http://localhost:8001/docs" -ForegroundColor White
Write-Host ""

Start-Sleep -Seconds 3
Start-Process "http://localhost:8001/"
