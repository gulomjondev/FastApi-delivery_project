from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from schemas import ProductModel
from database import session
from models import Product, User
from dependencies import get_current_user

product_routers = APIRouter(prefix='/product')


@product_routers.post('/create', status_code=201)
async def product_create(product: ProductModel, current_user: User = Depends(get_current_user)):
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faqat adminlar mahsulot qo'sha oladi!"
        )
    new_product = Product(
        name=product.name,
        price=product.price
    )
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return jsonable_encoder({
        "id": new_product.id,
        "name": new_product.name,
        "price": new_product.price
    })


@product_routers.get('/list', status_code=200)
async def list_products():
    products = session.query(Product).all()
    return jsonable_encoder(products)


@product_routers.get('/{id}/product', status_code=200)
async def product_detail(id: int, current_user: User = Depends(get_current_user)):
    db_product = session.query(Product).filter(Product.id == id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{id} - id product not found!"
        )
    return jsonable_encoder(db_product)


@product_routers.put('/{id}/update', status_code=200)
async def product_update(id: int, product: ProductModel, current_user: User = Depends(get_current_user)):
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faqat adminlar mahsulot yangilay oladi!"
        )
    db_product = session.query(Product).filter(Product.id == id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found!"
        )
    db_product.name = product.name
    db_product.price = product.price
    session.commit()
    session.refresh(db_product)
    return jsonable_encoder({
        "id": db_product.id,
        "name": db_product.name,
        "price": db_product.price
    })


@product_routers.delete('/{id}/delete', status_code=200)
async def product_delete(id: int, current_user: User = Depends(get_current_user)):
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Faqat adminlar mahsulot o'chira oladi!"
        )
    db_product = session.query(Product).filter(Product.id == id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found!"
        )
    session.delete(db_product)
    session.commit()
    return {"message": f"{id} - product deleted!"}