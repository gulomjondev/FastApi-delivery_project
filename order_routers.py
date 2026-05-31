from fastapi.security import OAuth2, OAuth2PasswordBearer
from fastapi import APIRouter, Query, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from schemas import OrderModel,OrderStatus
from database import session, engine
from models import User,Order,Product
from jose import jwt, JWTError
from datetime import datetime, timedelta
from auth_routers import oauth2_scheme, SECRET_KEY, ALGORITHM

order_routers = APIRouter(prefix='/orders')


def get_current_user(token: str= Depends(oauth2_scheme)):

    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username: str=payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid Token")
    except JWTError:
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token eskirgan yoki yaroqsiz!"
        )
    db_user = session.query(User).filter(User.username == username).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="User not found"
        )
    return db_user

def serialize_order(order: Order):
    return {
        "id": order.id,
        "quantity": order.quantity,
        "order_status": order.order_status.code if hasattr(order.order_status, 'code') else str(order.order_status),
        "user_id": order.user_id,
        "product_id": order.product_id
    }
@order_routers.post('/create', status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderModel, current_user: User = Depends(get_current_user)):
    
    db_product = session.query(Product).filter(Product.id == order.product_id).first()  

    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not Found!"
        )

    new_order = Order(
        quantity=order.quantity,
        order_status=order.order_status.value,
        user_id=current_user.id,
        product_id=order.product_id
    )

    session.add(new_order)
    session.commit()
    session.refresh(new_order)

    return jsonable_encoder({
        "id": new_order.id,
        "quantity": new_order.quantity,
        "user_id": new_order.user_id,
        "product_id": new_order.product_id,  
        "product": {
            "id": db_product.id,
            "name": db_product.name,
            "price": db_product.price
        }
    })

@order_routers.get('/list', status_code=200)
async def list_order(current_user: User=Depends(get_current_user)):
    # if not current_user.is_staff:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You are not Admin user"
    #     )  
    
    orders = session.query(Order).all()
    return jsonable_encoder([serialize_order(o) for o in orders])

@order_routers.get('/my-orders',status_code=200)
async def my_orders(current_user: User=Depends(get_current_user)):
    orders = session.query(Order).filter(Order.user_id == current_user.id).all()
    return jsonable_encoder([serialize_order(o) for o in orders])

@order_routers.put('/{order_id}/update',status_code=200)
async def update_order(order_id:int, order: OrderModel,current_user: User=Depends(get_current_user)):
    db_order = session.query(Order).filter(Order.id==order_id).first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="Order not found !"
        )
    if db_order.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,detail="You are not owner !"
        )
    db_product = session.query(Product).filter(Product.id==order.product_id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found!"
        )
    db_order.quantity = order.quantity
    db_order.product_id=order.product_id
    db_order.order_status = order.order_status.value

    session.commit()
    session.refresh(db_order)

    return jsonable_encoder({
        "id": db_order.id,
        "quantity": db_order.quantity,
        "order_status": db_order.order_status.code if hasattr(db_order.order_status, 'code') else str(db_order.order_status),  # ✅
        "user_id": db_order.user_id,
        "product": {
            "id": db_product.id,
            "name": db_product.name,
            "price": db_product.price
        }
    })

@order_routers.put('/{order_id}/update_status',status_code=200)
async def update_order_status(order_id: int, order_status: OrderStatus=Query(...),current_user: User=Depends(get_current_user)):
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,detail="You can not change status !"
        )
    db_order = session.query(Order).filter(Order.id==order_id).first()
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="Order not found !"
        )
    db_order.order_status=order_status.value

    session.commit()
    session.refresh(db_order)

    return jsonable_encoder({
        "id": db_order.id,
        "quantity": db_order.quantity,
        "order_status": str(db_order.order_status),
        "user_id": db_order.user_id,
        "product_id": db_order.product_id
    })

@order_routers.get('/{order_id}',status_code=200)
async def get_order(order_id: int, current_user: User=Depends(get_current_user)):
    order = session.query(Order).filter(Order.id==order_id).first()

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="Order not found"
        )
    
    if current_user.is_staff:
        return jsonable_encoder(serialize_order(order))
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="You are not owner!")
    
    return jsonable_encoder(serialize_order(order))
@order_routers.delete('/{order_id}/delete',status_code=200)
async def delete_order(order_id: int,current_user: User=Depends(get_current_user)):
    order = session.query(Order).filter(Order.id==order_id).first()
    
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Order not found!")
    
    if order.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    session.delete(order)
    session.commit()
    return {"message": f"{order_id}- order is deleted!"}