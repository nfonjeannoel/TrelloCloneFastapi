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


class _BaseComment(_pydantic.BaseModel):
    comment: str


class CommentCreate(_BaseComment):
    pass


class CommentUpdate(_BaseComment):
    pass


class Comment(_BaseComment):
    id: int
    card_id: int
    user_id: int
    created_date: _dt.date

    class Config:
        orm_mode = True


class _BaseCheckList(_pydantic.BaseModel):
    title: str
    is_checked: bool
    position: int


class CheckListCreate(_BaseCheckList):
    pass


class CheckListUpdate(_BaseCheckList):
    pass


class CheckList(_BaseCheckList):
    id: int
    card_id: int

    class Config:
        orm_mode = True
