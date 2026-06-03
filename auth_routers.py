from fastapi import APIRouter, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException
from schemas import SignUpModel, LoginModel
from database import session
from models import User
from werkzeug.security import generate_password_hash, check_password_hash
from jose import jwt
from datetime import datetime, timedelta
from dependencies import oauth2_scheme, SECRET_KEY, ALGORITHM, get_current_user,decode_token

auth_routers = APIRouter(prefix='/auth')


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
    from dependencies import decode_token
    username = decode_token(token)

    db_user = session.query(User).filter(User.username == username).first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Foydalanuvchi topilmadi!"
        )

    new_access_token = create_access_token(subject=db_user.username)
    return jsonable_encoder({"access": new_access_token})