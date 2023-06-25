from api.database import Base as _Base
from sqlalchemy import Column as _Column, Integer as _Integer, String as _String, ForeignKey as _ForeignKey


class List(_Base):
    __tablename__ = "lists"
    id = _Column(_Integer, primary_key=True, index=True)
    board_id = _Column(_Integer, _ForeignKey("boards.id"))
    name = _Column(_String, index=True)
    position = _Column(_Integer, default=0)
