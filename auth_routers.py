from signal import raise_signal

from fastapi import APIRouter, Query, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer
from schemas import ProductModel, SignUpModel, LoginModel,OrderModel
from database import session, engine
from models import Product, User,Order
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt, JWTError
from datetime import datetime, timedelta

auth_routers = APIRouter(prefix='/auth')


# session = session(bind=engine)




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = '735435a0caa6940f0c40d310bfc468698bb499cab5ed173639f73cc04a2ad487'
ALGORITHM = 'HS256'


def create_access_token(subject: str):
    expire = datetime.utcnow() + timedelta(minutes=30)
    return jwt.encode(
        {"sub": subject, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def create_refresh_token(subject: str):
    expire = datetime.utcnow() + timedelta(days=7)
    return jwt.encode(
        {"sub": subject, "exp": expire},
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token ichida username topilmadi!"
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token yaroqsiz yoki eskirgan!"
        )


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

@auth_routers.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        raise HTTPException(status_code=400, detail='Bu email allaqachon mavjud!')

    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        raise HTTPException(status_code=400, detail='Bu username allaqachon mavjud!')

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_staff=user.is_staff,
        is_active=user.is_active
    )
    session.add(new_user)
    session.commit()
    return {"message": "Foydalanuvchi muvaffaqiyatli yaratildi"}


@auth_routers.post('/login', status_code=200)
async def login(user: LoginModel):
    if "@" in user.username_or_email:
        db_user = session.query(User).filter(
            User.email == user.username_or_email
        ).first()
    else:
        db_user = session.query(User).filter(
            User.username == user.username_or_email
        ).first()

    if db_user and check_password_hash(db_user.password, user.password):
        access_token = create_access_token(subject=db_user.username)
        refresh_token = create_refresh_token(subject=db_user.username)
        return jsonable_encoder({
            "access": access_token,
            "refresh": refresh_token
        })

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail='Username, email yoki parol noto\'g\'ri!'
    )


@auth_routers.post('/refresh', status_code=200)
async def refresh(token: str = Depends(oauth2_scheme)):
    username = decode_token(token)

    db_user = session.query(User).filter(
        User.username == username
    ).first()

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi!"
        )

    new_access_token = create_access_token(subject=db_user.username)

    return jsonable_encoder({
        "access": new_access_token
    })


