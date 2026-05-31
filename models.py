from database import Base
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils.types import ChoiceType


ORDER_STATUS = [
    ("PENDING", "Pending"),
    ("IN_TRANSIT", "In Transit"),
    ("DELIVERED", "Delivered"),
    ("CANCELLED", "Cancelled"),
]


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(70), unique=True)
    email = Column(String(75), unique=True)
    password = Column(Text, nullable=False)
    is_staff = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)

    orders = relationship('Order', back_populates='user')  

    def __repr__(self):
        return f"{self.username}"


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(70))
    price = Column(Integer)

    orders = relationship('Order', back_populates='product') 

    def __repr__(self):
        return f"{self.name} product {self.price}"


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    order_status = Column(ChoiceType(choices=ORDER_STATUS), default="PENDING")

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship('User', back_populates='orders') 

    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product', back_populates='orders') 

    def __repr__(self):
        return f"Order {self.id} {self.order_status}"