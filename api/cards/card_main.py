from fastapi import APIRouter as _APIRouter, Depends as _Depends, HTTPException as _HTTPException, status as _status, \
    security as _security
from . import card_services as _card_services
from ..users.user_services import get_current_user as _get_current_user
from ..boards.board_services import get_current_board as _get_current_board
from ..boards.board_services import get_member_board as _get_member_board
from ..lists.list_services import get_current_list as _get_current_list
from ..lists.list_services import get_member_list as _get_member_list
from ..users import user_schemas as _user_schemas
from ..database import get_db as _get_db
from . import card_schemas as _card_schemas
from sqlalchemy.orm import Session as _Session
from ..boards import board_schemas as _board_schemas
from ..lists import list_schemas as _list_schemas

router = _APIRouter(
    prefix="/cards",
    tags=["cards"],
)

current_user_dependency = _Depends(_get_current_user)
board_dependency = _Depends(_get_current_board)
member_board_dependency = _Depends(_get_member_board)
list_dependency = _Depends(_get_current_list)
member_list_dependency = _Depends(_get_member_list)


@router.post("/{board_id}/{list_id}/create_card", response_model=_card_schemas.Card)
async def create_card(card_data: _card_schemas.CardCreate, db: _Session = _Depends(_get_db),
                      list_data: _list_schemas.List = member_list_dependency):
    db_card = await _card_services.create_card(db=db, card_data=card_data, list_id=list_data.id)
    return _card_schemas.Card.from_orm(db_card)


@router.get("/{board_id}/{list_id}/get_cards", response_model=list[_card_schemas.Card])
async def get_cards(db: _Session = _Depends(_get_db), list_data: _list_schemas.List = list_dependency):
    db_cards = await _card_services.get_cards_by_list(db=db, list_id=list_data.id)
    return [_card_schemas.Card.from_orm(db_card) for db_card in db_cards]


@router.get("/{board_id}/{list_id}/{card_id}/get_card", response_model=_card_schemas.Card)
async def get_card(card_id: int, list_data: _list_schemas.List = list_dependency, db: _Session = _Depends(_get_db), ):
    db_card = await _card_services.get_card_by_id(db=db, card_id=card_id, list_id=list_data.id)
    return _card_schemas.Card.from_orm(db_card)


@router.put("/{board_id}/{list_id}/{card_id}/update_card", response_model=_card_schemas.Card)
async def update_card(card_data: _card_schemas.CardUpdate, card_id: int,
                      list_data: _list_schemas.List = member_list_dependency,
                      db: _Session = _Depends(_get_db)):
    db_card = await _card_services.get_card_by_id(db=db, card_id=card_id, list_id=list_data.id)
    if not db_card:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Card not found")
    db_card = await _card_services.update_card(db=db, card_data=card_data, db_card=db_card)
    return _card_schemas.Card.from_orm(db_card)


@router.delete("/{board_id}/{list_id}/{card_id}/delete_card", status_code=_status.HTTP_204_NO_CONTENT)
async def delete_card(card_id: int, list_data: _list_schemas.List = member_list_dependency,
                      db: _Session = _Depends(_get_db)):
    db_card = await _card_services.get_card_by_id(db=db, card_id=card_id, list_id=list_data.id)
    if not db_card:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Card not found")
    db_card = await _card_services.delete_card(db=db, db_card=db_card)


# comments

@router.post("/{board_id}/{list_id}/{card_id}/create_comment", response_model=_card_schemas.Comment,
             dependencies=[member_list_dependency])
async def create_comment(comment_data: _card_schemas.CommentCreate, card_id: int,
                         current_user: _user_schemas.User = current_user_dependency,
                         db: _Session = _Depends(_get_db)):
    db_comment = await _card_services.create_comment(db=db, comment_data=comment_data, card_id=card_id,
                                                     user_id=current_user.id)
    return _card_schemas.Comment.from_orm(db_comment)


@router.get("/{board_id}/{list_id}/{card_id}/get_comments", response_model=list[_card_schemas.Comment],
            dependencies=[list_dependency])
async def get_comments(card_id: int, db: _Session = _Depends(_get_db)):
    db_comments = await _card_services.get_comments_by_card(db=db, card_id=card_id)
    return [_card_schemas.Comment.from_orm(db_comment) for db_comment in db_comments]


@router.get("/{board_id}/{list_id}/{card_id}/{comment_id}/get_comment", response_model=_card_schemas.Comment,
            dependencies=[list_dependency, current_user_dependency])
async def get_comment(comment_id: int, card_id: int, db: _Session = _Depends(_get_db),
                      ):
    db_comment = await _card_services.get_comment_by_id(db=db, comment_id=comment_id, card_id=card_id)
    return _card_schemas.Comment.from_orm(db_comment)


@router.put("/{board_id}/{list_id}/{card_id}/{comment_id}/update_comment", response_model=_card_schemas.Comment,
            dependencies=[member_list_dependency])
async def update_comment(comment_data: _card_schemas.CommentUpdate, comment_id: int, card_id: int,
                         current_user: _user_schemas.User = current_user_dependency,
                         db: _Session = _Depends(_get_db)):
    db_comment = await _card_services.get_comment_by_id(db=db, comment_id=comment_id, card_id=card_id)
    if not db_comment:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise _HTTPException(status_code=_status.HTTP_403_FORBIDDEN, detail="You can't update this comment")
    db_comment = await _card_services.update_comment(db=db, comment_data=comment_data, db_comment=db_comment)
    return _card_schemas.Comment.from_orm(db_comment)


@router.delete("/{board_id}/{list_id}/{card_id}/{comment_id}/delete_comment", status_code=_status.HTTP_204_NO_CONTENT,
               dependencies=[member_list_dependency])
async def delete_comment(comment_id: int, card_id: int, current_user: _user_schemas.User = current_user_dependency,
                         db: _Session = _Depends(_get_db)):
    db_comment = await _card_services.get_comment_by_id(db=db, comment_id=comment_id, card_id=card_id)
    if not db_comment:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise _HTTPException(status_code=_status.HTTP_403_FORBIDDEN, detail="You can't delete this comment")
    db_comment = await _card_services.delete_comment(db=db, db_comment=db_comment)
