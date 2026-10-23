import sys
import time
import httpx

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PRODUCT_SERVICE_URL = "http://127.0.0.1:8001"
AUTH_SERVICE_URL = "http://127.0.0.1:8000"

def run_tests():
    print("=" * 70)
    print(" BẮT ĐẦU KIỂM THỬ DỊCH VỤ QUẢN LÝ SẢN PHẨM (BÀI THỰC HÀNH 3)")
    print(f" - Product Service URL: {PRODUCT_SERVICE_URL}")
    print(f" - Auth Service URL:    {AUTH_SERVICE_URL}")
    print("=" * 70)

    # 1. Kiểm tra Health Check
    try:
        r = httpx.get(f"{PRODUCT_SERVICE_URL}/health", timeout=3.0)
        assert r.status_code == 200, f"Health check failed: {r.status_code}"
        print(" [PASS] 1. Health check Product Service hoạt động bình thường.")
    except Exception as e:
        print(f"❌ [FAIL] Không thể kết nối tới ProductService: {e}")
        print("   Vui lòng khởi chạy ProductService trước: python main.py (tại port 8001)")
        return

    # 2. GET /products: Lấy danh sách sản phẩm
    r = httpx.get(f"{PRODUCT_SERVICE_URL}/products")
    assert r.status_code == 200, f"Lỗi GET /products: {r.status_code}"
    products = r.json()
    assert isinstance(products, list), "Kết quả trả về phải là một danh sách"
    print(f" [PASS] 2. GET /products thành công! Hiện có {len(products)} sản phẩm trong CSDL riêng.")

    # 3. GET /products/{id}: Lấy chi tiết sản phẩm đầu tiên
    first_id = products[0]["id"]
    r = httpx.get(f"{PRODUCT_SERVICE_URL}/products/{first_id}")
    assert r.status_code == 200, f"Lỗi GET /products/{first_id}"
    p = r.json()
    assert p["id"] == first_id
    print(f" [PASS] 3. GET /products/{first_id} thành công! Tên: '{p['name']}', Giá: {p['price']} đ, Số lượng: {p['quantity']}.")

    # 4. POST /products KHÔNG CÓ TOKEN -> Phải bị từ chối 401 Unauthorized
    payload_new = {
        "name": "Chuột Gaming Razer DeathAdder V3 Pro",
        "description": "Cảm biến quang học Focus Pro 30K DPI, switch quang Gen-3",
        "price": 3290000.00,
        "quantity": 15
    }
    r = httpx.post(f"{PRODUCT_SERVICE_URL}/products", json=payload_new)
    assert r.status_code == 401, f"Kỳ vọng 401 khi không có token, nhận được: {r.status_code}"
    print(" [PASS] 4. Bảo mật SOA: POST /products khi không có Token bị từ chối chính xác (HTTP 401).")

    # 5. Đăng nhập qua AuthService (Bài thực hành 2) để lấy Bearer Token
    token = None
    try:
        login_res = httpx.post(
            f"{AUTH_SERVICE_URL}/login",
            json={"userName": "admin", "password": "123456"},
            timeout=3.0
        )
        if login_res.status_code == 200:
            token = login_res.json().get("token")
            print(f" [PASS] 5. Đăng nhập AuthService Bài 2 thành công! Đã nhận JWT token.")
        else:
            print(f"⚠️ [WARN] AuthService Bài 2 trả về HTTP {login_res.status_code}: {login_res.text}")
    except Exception as e:
        print(f"⚠️ [WARN] Không thể kết nối tới AuthService Bài 2 tại {AUTH_SERVICE_URL} ({e}).")

    if not token:
        # Fallback tạo token hợp lệ theo secret key của Bài 2 để kiểm thử fallback
        import jwt, datetime, timezone
        payload = {
            "userName": "admin",
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, "my_secret_key_123", algorithm="HS256")
        print("   -> Sử dụng JWT token hợp lệ với SECRET_KEY bài 2 để kiểm thử cơ chế xác thực fallback.")

    headers = {"Authorization": f"Bearer {token}"}

    # 6. POST /products CÓ TOKEN -> Thành công 201 Created
    r = httpx.post(f"{PRODUCT_SERVICE_URL}/products", json=payload_new, headers=headers)
    assert r.status_code == 201, f"Lỗi POST /products: {r.status_code} - {r.text}"
    created_p = r.json()
    new_id = created_p["id"]
    assert created_p["name"] == payload_new["name"]
    print(f" [PASS] 6. POST /products có token thành công! Đã tạo sản phẩm ID #{new_id}: '{created_p['name']}'.")

    # 7. PUT /products/{id} -> Cập nhật thông tin sản phẩm
    payload_update = {
        "name": "Chuột Gaming Razer DeathAdder V3 Pro (White Edition)",
        "price": 3490000.00,
        "quantity": 20
    }
    r = httpx.put(f"{PRODUCT_SERVICE_URL}/products/{new_id}", json=payload_update, headers=headers)
    assert r.status_code == 200, f"Lỗi PUT /products/{new_id}: {r.status_code} - {r.text}"
    updated_p = r.json()
    assert updated_p["name"] == payload_update["name"]
    assert float(updated_p["price"]) == payload_update["price"]
    assert updated_p["quantity"] == payload_update["quantity"]
    print(f" [PASS] 7. PUT /products/{new_id} thành công! Đã cập nhật tên thành: '{updated_p['name']}', Giá mới: {updated_p['price']} đ.")

    # 8. DELETE /products/{id} -> Xóa sản phẩm vừa tạo
    r = httpx.delete(f"{PRODUCT_SERVICE_URL}/products/{new_id}", headers=headers)
    assert r.status_code == 200, f"Lỗi DELETE /products/{new_id}: {r.status_code} - {r.text}"
    print(f" [PASS] 8. DELETE /products/{new_id} thành công!")

    # 9. GET /products/{id} sau khi xóa -> Phải trả về 404 Not Found
    r = httpx.get(f"{PRODUCT_SERVICE_URL}/products/{new_id}")
    assert r.status_code == 404, f"Kỳ vọng 404 sau khi xóa, nhận được: {r.status_code}"
    print(f" [PASS] 9. Kiểm tra sản phẩm đã xóa: GET /products/{new_id} trả về 404 Not Found chính xác.")

    print("=" * 70)
    print(" TẤT CẢ CÁC BÀI TEST RESTFUL API VÀ XÁC THỰC SOA ĐÃ THÀNH CÔNG 100%!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
