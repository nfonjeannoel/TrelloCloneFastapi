from api.database import Base as _Base
from sqlalchemy import Column as _Column, Integer as _Integer, String as _String, ForeignKey as _ForeignKey, \
    ForeignKeyConstraint, Boolean as _Boolean
import datetime as _dt
from sqlalchemy.orm import relationship as _relationship


class Card(_Base):
    __tablename__ = "cards"
    id = _Column(_Integer, primary_key=True, index=True)
    list_id = _Column(_Integer, _ForeignKey("lists.id"))
    title = _Column(_String, index=True)
    description = _Column(_String)
    created_date = _Column(_String, default=str(_dt.date.today()))

    is_active = _Column(_Boolean, default=True)
    due_date = _Column(_String, nullable=True)
    reminder_datetime = _Column(_String, nullable=True)

    list = _relationship("List", back_populates="cards")
    comments = _relationship("Comment", back_populates="card")
    check_lists = _relationship("CheckList", back_populates="card")
    card_members = _relationship("CardMember", back_populates="card")
    card_activities = _relationship("CardActivity", back_populates="card")
    labels = _relationship("CardLabel", back_populates="card")
    attachments = _relationship("CardAttachment", back_populates="card")


class Comment(_Base):
    __tablename__ = "comments"
    id = _Column(_Integer, primary_key=True, index=True)
    card_id = _Column(_Integer, _ForeignKey("cards.id"))
    user_id = _Column(_Integer, _ForeignKey("site_users.id"))
    comment = _Column(_String)
    created_datetime = _Column(_String, default=str(_dt.datetime.now()))
    # TODO: UPDATE DATE FIELDS TO USE DATE IN ALL MODELS AND SCHEMAS

    card = _relationship("Card", back_populates="comments")


class CheckList(_Base):
    __tablename__ = "check_lists"
    id = _Column(_Integer, primary_key=True, index=True)
    card_id = _Column(_Integer, _ForeignKey("cards.id"))
    title = _Column(_String)
    is_checked = _Column(_Integer, default=False)
    position = _Column(_Integer, default=0)

    card = _relationship("Card", back_populates="check_lists")


class CardMember(_Base):
    __tablename__ = "card_members"
    id = _Column(_Integer, primary_key=True, index=True)
    card_id = _Column(_Integer, _ForeignKey("cards.id"))
    user_id = _Column(_Integer, _ForeignKey("site_users.id"))

    # TODO: ADD SOME DATA ABOUT THE USER

    card = _relationship("Card", back_populates="card_members")


class CardActivity(_Base):
    __tablename__ = "card_activities"
    id = _Column(_Integer, primary_key=True, index=True)
    card_id = _Column(_Integer, _ForeignKey("cards.id"))
    user_id = _Column(_Integer, _ForeignKey("site_users.id"))
    activity = _Column(_String)
    created_datetime = _Column(_String, default=str(_dt.datetime.now()))

    card = _relationship("Card", back_populates="card_activities")


class CardLabel(_Base):
    __tablename__ = "card_labels"
    id = _Column(_Integer, primary_key=True, index=True)
    card_id = _Column(_Integer, _ForeignKey("cards.id"))
    label_id = _Column(_Integer, _ForeignKey("core_labels.id"))

    card = _relationship("Card", back_populates="labels")


class CardAttachment(_Base):
    __tablename__ = "card_attachments"
    id = _Column(_Integer, primary_key=True, index=True)
    card_id = _Column(_Integer, _ForeignKey("cards.id"))
    uploaded_date = _Column(_String, default=str(_dt.date.today()))
    file_name = _Column(_String)
    location = _Column(_String)

    card = _relationship("Card", back_populates="attachments")
