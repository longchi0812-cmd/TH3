@echo off
title Product Management Service (Bai Thuc Hanh 3) - Port 8001
echo ====================================================================
echo  KHOI CHAY PRODUCT MANAGEMENT SERVICE (BAI THUC HANH SO 3)
echo  Cong: http://127.0.0.1:8001
echo  Swagger UI: http://127.0.0.1:8001/docs
echo  Giao dien Dashboard: http://127.0.0.1:8001/
echo ====================================================================
python -m uvicorn main:app --host 127.0.0.1 --port 8001 --reload
pause
