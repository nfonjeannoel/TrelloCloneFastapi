import datetime as _dt
import pydantic as _pydantic


class AccessToken(_pydantic.BaseModel):
    access_token: str
    token_type: str


class _UserBase(_pydantic.BaseModel):
    email: str


class UserCreate(_UserBase):
    password: str
    username: str

    class Config:
        orm_mode = True


class User(_UserBase):
    id: int
    username: str
    signup_date: _dt.date

    class Config:
        orm_mode = True
