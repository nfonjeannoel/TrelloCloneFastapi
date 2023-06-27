from sqlalchemy.orm import Session as _Session
from . import card_models as _card_models
import email_validator as _email_check
import passlib.hash as _hash
from fastapi import HTTPException as _HTTPException, status as _status, Depends as _Depends
import fastapi.security as _security
import jwt as _jwt
from . import card_schemas as _card_schemas
from api.database import get_db as _get_db
from ..users.user_services import get_current_user as _get_current_user
from ..users import user_schemas as _user_schemas


async def create_card(db: _Session, card_data: _card_schemas.CardCreate, list_id: int):
    db_card = _card_models.Card(**card_data.dict(), list_id=list_id)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


async def get_cards_by_list(db: _Session, list_id: int):
    return db.query(_card_models.Card).filter(_card_models.Card.list_id == list_id).all()


async def get_card_by_id(db: _Session, card_id: int, list_id: int):
    return db.query(_card_models.Card).filter(_card_models.Card.list_id == list_id).filter(
        _card_models.Card.id == card_id).first()


async def update_card(db: _Session, card_data: _card_schemas.CardUpdate, db_card: _card_models.Card):
    update_data = card_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_card, key, value)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)
    return db_card


async def delete_card(db: _Session, db_card: _card_models.Card):
    db.delete(db_card)
    db.commit()


# comments

async def create_comment(db: _Session, comment_data: _card_schemas.CommentCreate, card_id: int, user_id: int):
    db_comment = _card_models.Comment(**comment_data.dict(), card_id=card_id, user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


async def get_comments_by_card(db: _Session, card_id: int):
    return db.query(_card_models.Comment).filter(_card_models.Comment.card_id == card_id).all()


async def get_comment_by_id(db: _Session, comment_id: int, card_id: int):
    return db.query(_card_models.Comment).filter(_card_models.Comment.card_id == card_id).filter(
        _card_models.Comment.id == comment_id).first()


async def update_comment(db: _Session, comment_data: _card_schemas.CommentUpdate, db_comment: _card_models.Comment):
    update_data = comment_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_comment, key, value)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


async def delete_comment(db: _Session, db_comment: _card_models.Comment):
    db.delete(db_comment)
    db.commit()