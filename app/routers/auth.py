from fastapi import APIRouter, Request, Depends, status, HTTPException, Response
from fastapi.responses import JSONResponse
from typing import Optional
from app.db import SessionLocal
from sqlalchemy.orm import Session
from app.config import AUTH_OPTION
from passlib.context import CryptContext
from pydantic import BaseModel
from app.models import Users
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt, JWTError

router = APIRouter(prefix="/auth", tags=["auth"])
SECRET_KEY = AUTH_OPTION["key"]
ALGORITHM = AUTH_OPTION["algotithm"]
TOKENEXPIRE = AUTH_OPTION["exp"]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2Bearer = OAuth2PasswordBearer(tokenUrl="token")


class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.id: Optional[str] = None
        self.pw: Optional[str] = None


class User(BaseModel):
    id: str
    email: Optional[str]
    password: str


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def getHash(password):
    return bcrypt_context.hash(password)


def authenticateUser(id: str, pw: str, db):
    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        return False
    if not bcrypt_context.verify(pw, user.pw):
        return False
    return user


@router.post("/register")
async def createUser(user: User, db: Session = Depends(get_db)):
    check = db.query(Users).filter(Users.id == user.id).first()
    if check:
        return JSONResponse(status_code=400, content=dict(msg="ID already in use"))
    userModel = Users(id=user.id, email=user.email)
    userModel.pw = getHash(user.password)
    db.add(userModel)
    db.commit()
    return JSONResponse(status_code=200, content=dict(msg="ID created"))


def createToken(id, expireDelta):
    encode = {"id": id}
    expire = datetime.utcnow() + timedelta(minutes=expireDelta)
    encode["exp"] = expire
    return jwt.encode(encode, SECRET_KEY, ALGORITHM)


async def get_current_user(token: str = Depends(oauth2Bearer)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id = payload.get("id")
        if id is None:
            raise HTTPException(status_code=404, detail="Id not found")
        return id
    except JWTError:
        raise HTTPException(status_code=404, detail="token expired")


# async def get_current_user(request: Request):
#     try:
#         token = request.cookies.get("access_token")
#         if token is None:
#             return None
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         id = payload.get("id")
#         if id is None:
#             raise HTTPException(status_code=404, detail="Id not found")
#         return id
#     except JWTError:
#         raise HTTPException(status_code=404, detail="Not found")


@router.post("/token")
async def loginUser(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticateUser(form_data.username, form_data.password, db)
    if not user:
        return JSONResponse(status_code=400, content=dict(msg="Login Failed"))
    token = createToken(user.id, expireDelta=TOKENEXPIRE)
    return {"access_token": token, "token_type": "bearer"}


def get_user_exception():
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return credentials_exception


@router.post("/login")
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticateUser(form_data.username, form_data.password, db)
    if not user:
        return False
    token = createToken(user.id, 60)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return True
