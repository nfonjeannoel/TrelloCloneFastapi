from api.database import Base as _Base
from sqlalchemy import Column as _Column, Integer as _Integer, String as _String, ForeignKey as _ForeignKey, \
    ForeignKeyConstraint
import datetime as _dt


class Card(_Base):
    __tablename__ = "cards"
    id = _Column(_Integer, primary_key=True, index=True)
    list_id = _Column(_Integer, _ForeignKey("lists.id"))
    title = _Column(_String, index=True)
    description = _Column(_String)
    created_date = _Column(_String, default=str(_dt.date.today()))

    # is_active = _Column(_Integer, default=True)
    # due_date = _Column(_String)
    # completed_date = _Column(_String)
