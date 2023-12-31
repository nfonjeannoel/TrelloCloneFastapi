import datetime as _dt
import pydantic as _pydantic

from api.users.user_schemas import User as _User


class _BaseCard(_pydantic.BaseModel):
    title: str
    description: str


class CardCreate(_BaseCard):
    pass


class CardUpdate(_BaseCard):
    list_id: int
    is_active: bool
    due_date: _dt.date
    reminder_datetime: _dt.datetime | None


class CardUpdateTitle(_pydantic.BaseModel):
    title: str | None
    description: str | None


class Card(_BaseCard):
    id: int
    list_id: int
    created_date: _dt.date
    is_active: bool
    due_date: _dt.date | None
    reminder_datetime: _dt.datetime | None

    class Config:
        orm_mode = True


class CardDueDate(_pydantic.BaseModel):
    due_date: _dt.date


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


class FullComment(Comment):
    user: _User | None


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
    user: _User | None

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


class FullCardActivity(CardActivity):
    user: _User | None


class CardActivityCreate(_pydantic.BaseModel):
    activity: str

    class Config:
        orm_mode = True


class CardLabel(_pydantic.BaseModel):
    id: int
    card_id: int
    label_id: int

    class Config:
        orm_mode = True


class FullCardLabel(CardLabel):
    from api.boards.board_schemas import BoardLabel
    board_label: BoardLabel | None


class CardAttachment(_pydantic.BaseModel):
    id: int
    card_id: int
    uploaded_date: _dt.date
    file_name: str
    location: str

    class Config:
        orm_mode = True


class FullCardMember(Card):
    card_members: list[CardMember] | None


class FullCard(Card):
    comments: list[FullComment] | None
    check_lists: list[CheckList] | None
    card_members: list[CardMember] | None
    card_activities: list[FullCardActivity] | None
    labels: list[FullCardLabel] | None
    attachments: list[CardAttachment] | None
