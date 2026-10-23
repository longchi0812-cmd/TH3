"""
ProductController - Xử lý nghiệp vụ và truy vấn dữ liệu sản phẩm
Tuân theo mô hình Controller xử lý logic nghiệp vụ và thao tác CSDL.
"""
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import or_
from sqlalchemy.orm import Session
from models import Product
from schemas import ProductCreate, ProductUpdate

class ProductController:
    """Controller phụ trách toàn bộ nghiệp vụ và truy vấn dữ liệu bảng products."""

    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[Product]:
        """
        Nghiệp vụ: Lấy danh sách sản phẩm với hỗ trợ phân trang và tìm kiếm theo tên hoặc mã ID.
        Tương ứng API: GET /products
        """
        query = db.query(Product)
        if search and search.strip():
            term = search.strip()
            conditions = [
                Product.name.ilike(f"%{term}%"),
                Product.description.ilike(f"%{term}%")
            ]
            # Hỗ trợ tìm kiếm theo ID (ví dụ: '1', '#1', 'id 1', 'id: 1')
            cleaned_id = term.lower().replace("id:", "").replace("id=", "").replace("id", "").strip().lstrip("#").strip()
            if cleaned_id.isdigit():
                conditions.append(Product.id == int(cleaned_id))

            query = query.filter(or_(*conditions))
        return query.order_by(Product.id.asc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Optional[Product]:
        """
        Nghiệp vụ: Lấy thông tin chi tiết một sản phẩm theo ID.
        Tương ứng API: GET /products/{id}
        """
        return db.query(Product).filter(Product.id == product_id).first()

    @staticmethod
    def create(db: Session, product_in: ProductCreate) -> Product:
        """
        Nghiệp vụ: Thêm mới một sản phẩm vào CSDL.
        Tương ứng API: POST /products
        """
        new_product = Product(
            name=product_in.name.strip(),
            description=product_in.description.strip() if product_in.description else None,
            price=product_in.price,
            quantity=product_in.quantity
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product

    @staticmethod
    def update(
        db: Session,
        product_id: int,
        product_in: ProductUpdate
    ) -> Optional[Product]:
        """
        Nghiệp vụ: Cập nhật thông tin sản phẩm và cập nhật thời gian updated_at.
        Tương ứng API: PUT /products/{id}
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return None

        update_data = product_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "name" and isinstance(value, str):
                value = value.strip()
            elif field == "description" and isinstance(value, str):
                value = value.strip()
            setattr(product, field, value)

        product.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete(db: Session, product_id: int) -> bool:
        """
        Nghiệp vụ: Xóa một sản phẩm khỏi CSDL.
        Tương ứng API: DELETE /products/{id}
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return False

        db.delete(product)
        db.commit()
        return True
