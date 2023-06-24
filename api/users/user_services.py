from sqlalchemy.orm import Session as _Session
from . import user_models as _user_models
import email_validator as _email_check
import passlib.hash as _hash
from fastapi import HTTPException as _HTTPException, status as _status, Depends as _Depends
import fastapi.security as _security
import jwt as _jwt
from . import user_schemas as _user_schemas
from api.database import get_db as _get_db

_JWT_SECRET = "supersafeandsecuresecrete"
oauth2_scheme = _security.OAuth2PasswordBearer(tokenUrl="/users/token")


async def get_current_user(db: _Session = _Depends(_get_db), token: str = _Depends(oauth2_scheme)):
    try:
        payload = _jwt.decode(token, _JWT_SECRET, algorithms=["HS256"])
        user = db.get(_user_models.User, payload["id"])
    except _HTTPException:
        raise _HTTPException(status_code=_status.HTTP_401_UNAUTHORIZED, detail="Invalid Email or Password")

    return _user_schemas.User.from_orm(user)


async def get_user_by_email(db: _Session, email: str):
    return db.query(_user_models.User).filter(_user_models.User.email == email).first()


async def create_user(db: _Session, user: _user_schemas.UserCreate):
    try:
        valid_email = _email_check.validate_email(email=user.email)
        email = valid_email.email
    except _email_check.EmailNotValidError as e:
        raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail=str(e))

    db_user = _user_models.User(email=email, hashed_password=_hash.bcrypt.hash(user.password),
                                username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


async def create_token(user: _user_models.User):
    user_obj = _user_schemas.User.from_orm(user)
    user_dict = user_obj.dict()
    del user_dict["signup_date"]
    token = _jwt.encode(user_dict, _JWT_SECRET)
    return _user_schemas.AccessToken(access_token=token, token_type="bearer")


async def authenticate_user(email: str, password: str, db: _Session):
    user = await get_user_by_email(db=db, email=email)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


async def get_users(db: _Session, skip: int = 0, limit: int = 100):
    return db.query(_user_models.User).offset(skip).limit(limit).all()


async def get_user_by_id(db: _Session, user_id: int):
    return db.get(_user_models.User, user_id)
