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


class _BaseBoardMember(_pydantic.BaseModel):
    email: str


class BoardAddMember(_BaseBoardMember):
    pass

    class Config:
        orm_mode = True


class BoardRemoveMember(_BaseBoardMember):
    pass

    class Config:
        orm_mode = True


class BoardMember(_pydantic.BaseModel):
    id: int
    board_id: int
    user_id: int

    class Config:
        orm_mode = True
