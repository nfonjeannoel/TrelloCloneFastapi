from api.database import Base as _Base
from sqlalchemy import Column as _Column, Integer as _Integer, String as _String, ForeignKey as _ForeignKey
from passlib.hash import bcrypt as _bcrypt
import datetime as _dt
from sqlalchemy.orm import relationship as _relationship


class User(_Base):
    __tablename__ = "site_users"
    id = _Column(_Integer, primary_key=True, index=True)
    username = _Column(_String, index=True)
    hashed_password = _Column(_String)
    email = _Column(_String, unique=True, index=True)
    signup_date = _Column(_String, default=str(_dt.date.today()))

    cards = _relationship("CardMember", back_populates="user")
    comments = _relationship("Comment", back_populates="user")
    board_members = _relationship("BoardMember", back_populates="user")
    card_activities = _relationship("CardActivity", back_populates="user")

    def verify_password(self, password: str):
        return _bcrypt.verify(password, self.hashed_password)
