"""
Pydantic Schemas cho ProductService
Validate dữ liệu đầu vào và định dạng JSON trả về cho các API RESTful.
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field

class ProductBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Tên sản phẩm",
        examples=["Bàn phím cơ không dây Keychron K2"]
    )
    description: Optional[str] = Field(
        None,
        description="Mô tả sản phẩm",
        examples=["Bàn phím cơ layout 75%, kết nối Bluetooth hoặc cáp Type-C"]
    )
    price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Giá sản phẩm (DECIMAL 10,2)",
        examples=[1850000.00]
    )
    quantity: int = Field(
        ...,
        ge=0,
        description="Số lượng sản phẩm trong kho",
        examples=[25]
    )

class ProductCreate(ProductBase):
    """Schema khi thêm sản phẩm mới (POST /products)."""
    pass

class ProductUpdate(BaseModel):
    """Schema khi cập nhật sản phẩm (PUT /products/{id}). Các trường không bắt buộc."""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Tên sản phẩm",
        examples=["Bàn phím cơ Keychron K2 Pro"]
    )
    description: Optional[str] = Field(
        None,
        description="Mô tả chi tiết sản phẩm",
        examples=["Bản nâng cấp hỗ trợ QMK/VIA"]
    )
    price: Optional[Decimal] = Field(
        None,
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Giá sản phẩm",
        examples=[2150000.00]
    )
    quantity: Optional[int] = Field(
        None,
        ge=0,
        description="Số lượng tồn kho",
        examples=[30]
    )

class ProductResponse(ProductBase):
    """Schema trả về chi tiết sản phẩm bao gồm id và timestamp."""
    id: int = Field(..., description="ID duy nhất của sản phẩm")
    created_at: datetime = Field(..., description="Thời gian tạo")
    updated_at: datetime = Field(..., description="Thời gian cập nhật gần nhất")

    model_config = ConfigDict(from_attributes=True)
