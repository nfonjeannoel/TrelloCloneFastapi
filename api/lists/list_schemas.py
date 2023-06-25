import pydantic as _pydantic


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

    class Config:
        orm_mode = True
