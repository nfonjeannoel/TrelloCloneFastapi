from fastapi import FastAPI
from api.users.user_main import router as _users_router
from api.boards.board_main import router as _boards_router
from api.lists.list_main import router as _lists_router
from api.cards.card_main import card_router as _cards_router, comments_router as _comments_router, \
    checklists_router as _check_lists_router, card_member_router as _card_member_router

app = FastAPI()

app.include_router(_users_router)
app.include_router(_boards_router)
app.include_router(_lists_router)
app.include_router(_cards_router)
app.include_router(_comments_router)
app.include_router(_check_lists_router)
app.include_router(_card_member_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
