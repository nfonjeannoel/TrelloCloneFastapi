from sqlalchemy.orm import Session as _Session
from . import board_models as _board_models
import email_validator as _email_check
import passlib.hash as _hash
from fastapi import HTTPException as _HTTPException, status as _status, Depends as _Depends
import fastapi.security as _security
import jwt as _jwt
from . import board_schemas as _board_schemas
from api.database import get_db as _get_db


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
