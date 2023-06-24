import datetime as _dt
import pydantic as _pydantic


class _BaseBoard(_pydantic.BaseModel):
    name: str
    is_public: bool


class BoardCreate(_BaseBoard):
    pass


class BoardUpdate(_BaseBoard):
    pass


class Board(_BaseBoard):
    id: int
    owner_id: int
    created_date: _dt.date

    class Config:
        orm_mode = True
