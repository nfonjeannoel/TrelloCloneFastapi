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


async def get_current_board(board_id: int, db: _Session = _Depends(_get_db)):
    board = await get_board_by_id(db=db, board_id=board_id)
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


async def get_board_member_by_id(db: _Session, board_id: int, member_id: int):
    return db.query(_board_models.BoardMember).filter(_board_models.BoardMember.board_id == board_id).filter(
        _board_models.BoardMember.user_id == member_id).first()


async def user_is_board_member(db: _Session, board_id: int, user_id: int):
    return True if await get_board_member_by_id(db=db, board_id=board_id, member_id=user_id) else False


async def add_member_to_board(db: _Session, board_id: int, member_id: int):
    db_member = _board_models.BoardMember(board_id=board_id, user_id=member_id)
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member


async def remove_member_from_board(db: _Session, board_id: int, member_id: int):
    db_member = await get_board_member_by_id(db=db, board_id=board_id, member_id=member_id)
    if not db_member:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Member not found")
    db.delete(db_member)
    db.commit()
    return True


async def get_board_members(db: _Session, board_id: int):
    return db.query(_board_models.BoardMember).filter(_board_models.BoardMember.board_id == board_id).all()


async def get_boards_members_by_user_id(db: _Session, user_id: int):
    return db.query(_board_models.BoardMember).filter(_board_models.BoardMember.user_id == user_id).all()
