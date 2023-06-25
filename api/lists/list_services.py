from sqlalchemy.orm import Session as _Session
from . import list_models as _list_models
import email_validator as _email_check
import passlib.hash as _hash
from fastapi import HTTPException as _HTTPException, status as _status, Depends as _Depends
import fastapi.security as _security
import jwt as _jwt
from . import list_schemas as _list_schemas
from api.database import get_db as _get_db


async def create_list(db: _Session, list_data: _list_schemas.ListCreate, board_id: int):
    db_list = _list_models.List(**list_data.dict(), board_id=board_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


async def get_board_lists(db: _Session, board_id: int):
    return db.query(_list_models.List).filter(_list_models.List.board_id == board_id).all()


async def get_list_by_id(db: _Session, list_id: int):
    return db.get(_list_models.List, list_id)


async def update_list(db: _Session, list_data: _list_schemas.ListUpdate, db_list: _list_models.List):
    update_data = list_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_list, key, value)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


async def delete_list(db: _Session, db_list: _list_models.List):
    db.delete(db_list)
    db.commit()
