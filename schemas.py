from pydantic import BaseModel
from typing import Optional
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class SignUpModel(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    password: str
    is_staff: Optional[bool] = False
    is_active: Optional[bool] = False

    model_config = {"from_attributes": True}

class LoginModel(BaseModel):
    username_or_email: str
    password: str

class ProductModel(BaseModel):
    id: Optional[int] = None
    name: str
    price: int

    model_config = {"from_attributes": True}

class OrderModel(BaseModel):
    id: Optional[int] = None
    quantity: int
    order_status: Optional[OrderStatus] = OrderStatus.PENDING
    user_id: Optional[int] = None
    product_id: int

    model_config = {"from_attributes": True}