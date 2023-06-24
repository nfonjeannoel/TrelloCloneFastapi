from fastapi import FastAPI
from api.users.user_main import router as _users_router
from api.boards.board_main import router as _boards_router

app = FastAPI()

app.include_router(_users_router)
app.include_router(_boards_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
