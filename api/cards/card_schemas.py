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
    is_active: bool

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
    created_datetime: _dt.datetime

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


class CardMemberCreate(_pydantic.BaseModel):
    email: str


class CardMemberRemove(_pydantic.BaseModel):
    email: str


class CardMember(_pydantic.BaseModel):
    id: int
    card_id: int
    user_id: int

    class Config:
        orm_mode = True


class CardActivity(_pydantic.BaseModel):
    id: int
    card_id: int
    user_id: int
    activity: str
    created_datetime: _dt.datetime

    class Config:
        orm_mode = True


class CardActivityCreate(_pydantic.BaseModel):
    activity: str

    class Config:
        orm_mode = True


# class CardLabel(_Base):
#     __tablename__ = "card_labels"
#     id = _Column(_Integer, primary_key=True, index=True)
#     card_id = _Column(_Integer, _ForeignKey("cards.id"))
#     label_id = _Column(_Integer, _ForeignKey("core_labels.id"))


class CardLabel(_pydantic.BaseModel):
    id: int
    card_id: int
    label_id: int

    class Config:
        orm_mode = True

