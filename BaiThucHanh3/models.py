"""
BÀI THỰC HÀNH SỐ 3 - SERVICE QUẢN LÝ SẢN PHẨM (PRODUCT MANAGEMENT)
Mô hình dữ liệu (Model) cho bảng 'products'
Tuân thủ nguyên tắc kiến trúc SOA: Có CSDL riêng độc lập với Auth Service.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    # id: INT (PRIMARY KEY) ID duy nhất của sản phẩm
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # name: VARCHAR(255) Tên sản phẩm
    name = Column(String(255), nullable=False, index=True)

    # description: TEXT Mô tả sản phẩm
    description = Column(Text, nullable=True)

    # price: DECIMAL(10, 2) Giá sản phẩm
    price = Column(Numeric(10, 2), nullable=False)

    # quantity: INT Số lượng sản phẩm trong kho
    quantity = Column(Integer, nullable=False, default=0)

    # created_at: TIMESTAMP Ngày sản phẩm được tạo
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # updated_at: TIMESTAMP Ngày sản phẩm được cập nhật lần cuối
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def to_dict(self):
        """Chuyển đổi đối tượng Product sang dictionary JSON-serializable."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price is not None else 0.0,
            "quantity": self.quantity,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
