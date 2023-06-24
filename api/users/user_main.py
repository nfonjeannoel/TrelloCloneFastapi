from fastapi import APIRouter as _APIRouter, Depends as _Depends, HTTPException as _HTTPException, status as _status, \
    security as _security
from . import user_services as _user_services
from ..database import get_db as _get_db
from . import user_schemas as _user_schemas
from sqlalchemy.orm import Session as _Session

router = _APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.post("/create_user", response_model=_user_schemas.AccessToken)
async def create_user(user: _user_schemas.UserCreate, db: _Session = _Depends(_get_db)):
    db_user = await _user_services.get_user_by_email(db=db, email=user.email)
    if db_user:
        raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user = await _user_services.create_user(db=db, user=user)
    return await _user_services.create_token(user=user)


@router.post("/token", response_model=_user_schemas.AccessToken)
async def login(form_data: _security.OAuth2PasswordRequestForm = _Depends(),
                db: _Session = _Depends(_get_db)):
    user = await _user_services.authenticate_user(email=form_data.username, password=form_data.password, db=db)
    if not user:
        raise _HTTPException(status_code=_status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials")

    return await _user_services.create_token(user=user)


@router.get("", response_model=list[_user_schemas.User])
async def read_users(skip: int = 0, limit: int = 100, db: _Session = _Depends(_get_db)):
    users = await _user_services.get_users(db=db, skip=skip, limit=limit)
    return [_user_schemas.User.from_orm(user) for user in users]


@router.get("/me", response_model=_user_schemas.User)
async def read_users_me(current_user: _user_schemas.User = _Depends(_user_services.get_current_user)):
    return current_user


@router.get("/{user_id}", response_model=_user_schemas.User)
async def read_user(user_id: int, db: _Session = _Depends(_get_db)):
    db_user = await _user_services.get_user_by_id(db=db, user_id=user_id)
    if db_user is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    return _user_schemas.User.from_orm(db_user)
