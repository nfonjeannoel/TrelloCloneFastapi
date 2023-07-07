from api.database import Base as _Base
from sqlalchemy import Column as _Column, Integer as _Integer, String as _String, ForeignKey as _ForeignKey
import datetime as _dt
from sqlalchemy.orm import relationship as _relationship


class Board(_Base):
    __tablename__ = "boards"
    id = _Column(_Integer, primary_key=True, index=True)
    owner_id = _Column(_Integer, _ForeignKey("site_users.id"))
    name = _Column(_String, index=True)
    is_public = _Column(_Integer, default=True)
    created_date = _Column(_String, default=str(_dt.date.today()))

    lists = _relationship("List", back_populates="board")


class BoardMember(_Base):
    __tablename__ = "board_members"
    id = _Column(_Integer, primary_key=True, index=True)
    user_id = _Column(_Integer, _ForeignKey("site_users.id"))
    board_id = _Column(_Integer, _ForeignKey("boards.id"))


# TODO: ADD DEFAULT LABELS TO BOARD
class CoreLabel(_Base):
    # applies to all boards
    __tablename__ = "core_labels"
    id = _Column(_Integer, primary_key=True, index=True)
    name = _Column(_String)
    color = _Column(_String)


class BoardLabel(_Base):
    # applies to a specific board
    __tablename__ = "board_labels"
    id = _Column(_Integer, primary_key=True, index=True)
    board_id = _Column(_Integer, _ForeignKey("boards.id"))
    name = _Column(_String)
    color = _Column(_String)
