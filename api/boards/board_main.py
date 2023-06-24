from fastapi import APIRouter as _APIRouter, Depends as _Depends, HTTPException as _HTTPException, status as _status, \
    security as _security
from . import board_services as _board_services
from ..users.user_services import get_current_user as _get_current_user
from ..users import user_schemas as _user_schemas
from ..database import get_db as _get_db
from . import board_schemas as _board_schemas
from sqlalchemy.orm import Session as _Session

router = _APIRouter(
    prefix="/boards",
    tags=["boards"],
)

current_user_dependency = _Depends(_get_current_user)


@router.post("/create_board", response_model=_board_schemas.Board)
async def create_board(board: _board_schemas.BoardCreate, db: _Session = _Depends(_get_db),
                       current_user: _user_schemas.User = current_user_dependency):
    board = await _board_services.create_board(db=db, board=board, owner_id=current_user.id)
    return _board_schemas.Board.from_orm(board)


@router.get("", response_model=list[_board_schemas.Board])
async def read_boards_by_user(skip: int = 0, limit: int = 100, db: _Session = _Depends(_get_db),
                              current_user: _user_schemas.User = current_user_dependency):
    boards = await _board_services.get_boards_by_user(db=db, skip=skip, limit=limit, owner_id=current_user.id)
    return [_board_schemas.Board.from_orm(board) for board in boards]


@router.get("/{board_id}", response_model=_board_schemas.Board)
async def read_user_board(board_id: int, db: _Session = _Depends(_get_db),
                          current_user: _user_schemas.User = current_user_dependency):
    db_board = await _board_services.get_user_board_by_id(db=db, board_id=board_id, owner_id=current_user.id)
    if db_board is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Board not found")
    return _board_schemas.Board.from_orm(db_board)


@router.put("/{board_id}", response_model=_board_schemas.Board)
async def update_user_board(board_id: int, board: _board_schemas.BoardUpdate, db: _Session = _Depends(_get_db),
                            current_user: _user_schemas.User = current_user_dependency):
    db_board = await _board_services.get_user_board_by_id(db=db, board_id=board_id, owner_id=current_user.id)
    if db_board is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Board not found")
    board = await _board_services.update_board(db=db, board=board, db_board=db_board)
    return _board_schemas.Board.from_orm(board)


@router.delete("/{board_id}", status_code=_status.HTTP_204_NO_CONTENT)
async def delete_user_board(board_id: int, db: _Session = _Depends(_get_db),
                            current_user: _user_schemas.User = current_user_dependency):
    db_board = await _board_services.get_user_board_by_id(db=db, board_id=board_id, owner_id=current_user.id)
    if db_board is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Board not found")
    _ = await _board_services.delete_board(db=db, db_board=db_board)
