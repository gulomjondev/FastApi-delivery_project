from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from schemas import ProductModel
from database import session, engine
from models import Product, User, Order
from jose import jwt, JWTError
from auth_routers import oauth2_scheme, SECRET_KEY, ALGORITHM

product_routers = APIRouter(prefix='/product')

# session = session(bind=engine)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token eskirgan yoki yaroqsiz!"
        )

    db_user = session.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@product_routers.post('/create', status_code=201)
async def product_create(product: ProductModel, current_user: User = Depends(get_current_user)):
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
@product_routers.post('/{id}/update',status_code=200)

async def product_update(id: int,product: ProductModel,current_user: User=Depends(get_current_user)):

    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,detail="You are not Admin!"
        )
    db_product= session.query(Product).filter(Product.id==id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="Product not found!"
        )
    
    db_product.name=product.name
    db_product.price=product.price
    session.commit()
    session.refresh(db_product)
    return jsonable_encoder(
        {"id":db_product.id,
         "name":db_product.name,
         "price":db_product.price
         
         }
    )

@product_routers.get('/{id}/product',status_code=200)
async def product_detail(id:int, current_user: User=Depends(get_current_user)):
    db_product = session.query(Product).filter(Product.id==id).first()
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail=f"{id}-id product not found!"
        )
    return jsonable_encoder(db_product)

@product_routers.delete('/{id}/delete',status_code=200)
async def product_delete(id:int, current_user: User=Depends(get_current_user)):
    db_product=session.query(Product).filter(Product.id==id).first()

    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND
        )

    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,detail="You can not delete this product!"
        )
    session.delete(db_product)
    session.commit()
    return {"message": f"{id} - product deleted!"}
