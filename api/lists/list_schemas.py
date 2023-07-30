import pydantic as _pydantic
from ..cards.card_schemas import FullCardMember as _FullCardMember


class _BaseList(_pydantic.BaseModel):
    name: str


class ListCreate(_BaseList):
    position: int


class ListUpdate(_BaseList):
    position: int


class List(_BaseList):
    id: int
    position: int
    board_id: int

    cards: list[_FullCardMember] | None

    class Config:
        orm_mode = True


