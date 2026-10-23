"""
Cấu hình kết nối Cơ sở dữ liệu cho ProductService (Kiến trúc SOA)
Sử dụng SQLite làm CSDL độc lập riêng biệt (products.db) theo nguyên tắc Database-per-Service.
Cho phép chuyển đổi sang MySQL thông qua biến môi trường DATABASE_URL nếu cần.
"""
import os
import sys

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, Product

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(CURRENT_DIR, "products.db").replace("\\", "/")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# Cấu hình engine kết nối (SQLite cần check_same_thread=False khi chạy với FastAPI)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

# SessionLocal factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency cung cấp Session SQLAlchemy cho từng HTTP request và tự động đóng sau khi hoàn thành."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Tạo bảng 'products' nếu chưa có và chèn dữ liệu mẫu ban đầu."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        count = db.query(Product).count()
        if count == 0:
            sample_products = [
                Product(
                    name="Laptop Dell XPS 15 9530",
                    description="Intel Core i7-13700H, RAM 32GB, SSD 1TB, RTX 4060, Màn hình OLED 3.5K",
                    price=Decimal("45990000.00"),
                    quantity=12
                ),
                Product(
                    name="Bàn phím cơ không dây Keychron K2 Pro",
                    description="Layout 75%, Switch Gateron G Pro Red, Hot-swap, Bluetooth 5.1/Type-C",
                    price=Decimal("2150000.00"),
                    quantity=35
                ),
                Product(
                    name="Chuột công thái học Logitech MX Master 3S",
                    description="Cảm biến 8000 DPI Darkfield, con lăn siêu tốc MagSpeed, sạc Type-C",
                    price=Decimal("2450000.00"),
                    quantity=50
                ),
                Product(
                    name="Màn hình Dell UltraSharp U2723QE 27 inch 4K",
                    description="Độ phân giải 4K IPS Black, độ tương phản 2000:1, cổng Type-C 90W PD",
                    price=Decimal("12890000.00"),
                    quantity=18
                ),
                Product(
                    name="Tai nghe không dây Sony WH-1000XM5",
                    description="Chống ồn chủ động hàng đầu (ANC), âm thanh Hi-Res LDAC, pin 30 giờ",
                    price=Decimal("7990000.00"),
                    quantity=22
                ),
            ]
            db.add_all(sample_products)
            db.commit()
            print(f"[ProductService] Da khoi tao CSDL va nap thanh cong {len(sample_products)} san pham mau.")
    finally:
        db.close()
