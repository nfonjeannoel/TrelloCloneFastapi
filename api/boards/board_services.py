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
    board = await get_board_by_id(db=db, board_id=board_id)
    if not board:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Board not found")

    if board.is_public:
        return board

    # return board if user is member of board
    if await get_board_members_by_user_id_board_id(db=db, user_id=current_user.id, board_id=board_id):
        return board
    else:
        raise _HTTPException(status_code=_status.HTTP_401_UNAUTHORIZED, detail="User is authorized to view this board")


async def get_member_board(board_id: int, db: _Session = _Depends(_get_db),
                           current_user: _user_schemas.User = _Depends(_get_current_user)):
    """
    Get board by id, but only if user is a member of the board
    :param board_id:
    :param db:
    :return:
    """
    board = await get_board_by_id(db=db, board_id=board_id)
    if not board:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Board not found")

    if await get_board_members_by_user_id_board_id(db=db, user_id=current_user.id, board_id=board_id):
        return board
    else:
        raise _HTTPException(status_code=_status.HTTP_403_FORBIDDEN, detail="User is not a member of this board")



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


async def get_public_boards(db: _Session):
    return db.query(_board_models.Board).filter(_board_models.Board.is_public == True).all()


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


async def get_board_members_by_user_id_board_id(db: _Session, user_id: int, board_id: int):
    """
    Get board member by user id and board id
    :param db:
    :param user_id:
    :param board_id:
    :return:  BoardMember or None
    """
    return db.query(_board_models.BoardMember).filter(_board_models.BoardMember.user_id == user_id).filter(
        _board_models.BoardMember.board_id == board_id).first()


async def delete_all_members_from_board(db: _Session, board_id: int):
    db.query(_board_models.BoardMember).filter(_board_models.BoardMember.board_id == board_id).delete()
    db.commit()
    return True


async def create_board_label(db: _Session, board_id: int, board_label: _board_schemas.BoardLabelCreate):
    db_label = _board_models.BoardLabel(**board_label.dict(), board_id=board_id)
    db.add(db_label)
    db.commit()
    db.refresh(db_label)
    return db_label


async def get_board_labels(db: _Session, board_id: int):
    return db.query(_board_models.BoardLabel).filter(_board_models.BoardLabel.board_id == board_id).all()


async def get_board_label(db: _Session, board_id: int, label_id: int):
    return db.query(_board_models.BoardLabel).filter(_board_models.BoardLabel.board_id == board_id).filter(
        _board_models.BoardLabel.id == label_id).first()


async def update_board_label(db: _Session, db_board_label: _board_models.BoardLabel,
                             board_label: _board_schemas.BoardLabelUpdate):
    update_data = board_label.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_board_label, key, value)
    db.add(db_board_label)
    db.commit()
    db.refresh(db_board_label)
    return db_board_label


async def delete_board_label(db: _Session, db_board_label: _board_models.BoardLabel):
    db.delete(db_board_label)
    db.commit()
    return True
