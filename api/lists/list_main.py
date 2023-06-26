from fastapi import APIRouter as _APIRouter, Depends as _Depends, HTTPException as _HTTPException, status as _status, \
    security as _security
from . import list_services as _list_services
from ..users.user_services import get_current_user as _get_current_user
from ..boards.board_services import get_current_board as _get_current_board
from ..users import user_schemas as _user_schemas
from ..database import get_db as _get_db
from . import list_schemas as _list_schemas
from sqlalchemy.orm import Session as _Session
from ..boards import board_schemas as _board_schemas

router = _APIRouter(
    prefix="/lists",
    tags=["lists"],
)

current_user_dependency = _Depends(_get_current_user)
board_dependency = _Depends(_get_current_board)


@router.post("/{board_id}/create_list", response_model=_list_schemas.List)
async def create_list(list_data: _list_schemas.ListCreate, db: _Session = _Depends(_get_db),
                      board: _board_schemas.Board = board_dependency):
    db_list = await _list_services.create_list(db=db, list_data=list_data, board_id=board.id)
    return _list_schemas.List.from_orm(db_list)


@router.get("/{board_id}", response_model=list[_list_schemas.List])
async def get_board_lists(db: _Session = _Depends(_get_db),
                          board: _board_schemas.Board = board_dependency,
                          current_user: _user_schemas.User = current_user_dependency):
    if not board.is_public:
        if current_user.id != board.owner_id:
            raise _HTTPException(status_code=_status.HTTP_403_FORBIDDEN, detail="You are not the owner of this board")
    db_lists = await _list_services.get_board_lists(db=db, board_id=board.id)
    return [_list_schemas.List.from_orm(db_list) for db_list in db_lists]


@router.get("/{list_id}/{board_id}", response_model=_list_schemas.List, dependencies=[board_dependency])
async def get_board_list(list_id: int, db: _Session = _Depends(_get_db)):
    db_list = await _list_services.get_list_by_id(db=db, list_id=list_id)
    if db_list is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="List not found")
    return _list_schemas.List.from_orm(db_list)


@router.put("/{list_id}/{board_id}", response_model=_list_schemas.List, dependencies=[board_dependency])
async def update_board_list(list_id: int, list_data: _list_schemas.ListUpdate, db: _Session = _Depends(_get_db)):
    db_list = await _list_services.get_list_by_id(db=db, list_id=list_id)
    if db_list is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="List not found")
    db_list = await _list_services.update_list(db=db, list_data=list_data, db_list=db_list)
    return _list_schemas.List.from_orm(db_list)


@router.delete("/{list_id}/{board_id}", dependencies=[board_dependency],
               status_code=_status.HTTP_204_NO_CONTENT)
async def delete_board_list(list_id: int, db: _Session = _Depends(_get_db)):
    db_list = await _list_services.get_list_by_id(db=db, list_id=list_id)
    if db_list is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="List not found")
    await _list_services.delete_list(db=db, db_list=db_list)
