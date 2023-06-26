import datetime as _dt
import pydantic as _pydantic


class _BaseCard(_pydantic.BaseModel):
    title: str
    description: str


class CardCreate(_BaseCard):
    pass


class CardUpdate(_BaseCard):
    list_id: int


class Card(_BaseCard):
    id: int
    list_id: int
    created_date: _dt.date

    class Config:
        orm_mode = True
