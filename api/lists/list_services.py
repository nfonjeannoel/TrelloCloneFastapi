from sqlalchemy.orm import Session as _Session
from . import list_models as _list_models
import email_validator as _email_check
import passlib.hash as _hash
from fastapi import HTTPException as _HTTPException, status as _status, Depends as _Depends
import fastapi.security as _security
import jwt as _jwt
from . import list_schemas as _list_schemas
from api.database import get_db as _get_db
from ..users.user_services import get_current_user as _get_current_user
from ..users import user_schemas as _user_schemas
from ..boards import board_schemas as _board_schemas
from ..boards.board_services import get_current_board as _get_current_board
from ..boards.board_services import get_member_board as _get_member_board


async def get_current_list(list_id: int, board=_Depends(_get_current_board),
                           db: _Session = _Depends(_get_db)):
    db_list = await get_board_list_by_id(db=db, list_id=list_id, board_id=board.id)
    if not db_list:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="List not found")
    return db_list


async def get_member_list(list_id: int, board=_Depends(_get_member_board),
                          db: _Session = _Depends(_get_db)):
    db_list = await get_board_list_by_id(db=db, list_id=list_id, board_id=board.id)
    if not db_list:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="List not found")
    return db_list


async def get_board_list_by_id(db: _Session, list_id: int, board_id: int):
    return db.query(_list_models.List).filter(_list_models.List.board_id == board_id).filter(
        _list_models.List.id == list_id).first()


async def create_list(db: _Session, list_data: _list_schemas.ListCreate, board_id: int):
    db_list = _list_models.List(**list_data.dict(), board_id=board_id)
    db.add(db_list)
    db.commit()
    db.refresh(db_list)
    return db_list


async def get_board_lists(db: _Session, board_id: int):
    return db.query(_list_models.List).filter(_list_models.List.board_id == board_id).all()


async def get_list_by_id(db: _Session, list_id: int):
    """
    Get lists by id
    :param db:
    :param list_id:
    :return:
    """
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
