from sqlalchemy.orm import Session as _Session
from . import board_models as _board_models
import email_validator as _email_check
import passlib.hash as _hash
from fastapi import HTTPException as _HTTPException, status as _status, Depends as _Depends
import fastapi.security as _security
import jwt as _jwt
from . import board_schemas as _board_schemas
from api.database import get_db as _get_db
from ..users.user_services import get_current_user as _get_current_user
from ..users import user_schemas as _user_schemas


async def get_current_board(board_id: int, db: _Session = _Depends(_get_db),
                            current_user: _user_schemas.User = _Depends(_get_current_user)):
    board = await get_user_board_by_id(db=db, board_id=board_id, owner_id=current_user.id)
    if not board:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board


async def create_board(db: _Session, board: _board_schemas.BoardCreate, owner_id: int):
    db_board = _board_models.Board(**board.dict(), owner_id=owner_id)
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


async def get_boards_by_user(db: _Session, skip: int = 0, limit: int = 100, owner_id: int = None):
    return db.query(_board_models.Board).filter(_board_models.Board.owner_id == owner_id).offset(skip).limit(
        limit).all()


async def get_user_board_by_id(db: _Session, board_id: int, owner_id: int = None):
    return db.query(_board_models.Board).filter(_board_models.Board.owner_id == owner_id).filter(
        _board_models.Board.id == board_id).first()


async def get_board_by_id(db: _Session, board_id: int) -> _board_models.Board:
    return db.query(_board_models.Board).filter(_board_models.Board.id == board_id).first()


async def update_board(db: _Session, board: _board_schemas.BoardUpdate, db_board: _board_models.Board):
    update_data = board.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_board, key, value)
    db.add(db_board)
    db.commit()
    db.refresh(db_board)
    return db_board


async def delete_board(db: _Session, db_board: _board_models.Board):
    db.delete(db_board)
    db.commit()
    return True
