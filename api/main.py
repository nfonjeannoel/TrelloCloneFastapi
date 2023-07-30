from fastapi import FastAPI
from api.users.user_main import router as _users_router
from api.boards.board_main import router as _boards_router, board_labels_router as _board_labels_router
from api.lists.list_main import router as _lists_router
from api.cards.card_main import card_router as _cards_router, comments_router as _comments_router, \
    checklists_router as _check_lists_router, card_member_router as _card_member_router, card_activity_router as \
    _card_activity_router, card_label_router as _card_label_router, card_attachment_router as _card_attachment_router
from fastapi.middleware.cors import CORSMiddleware as _CORSMiddleware

app = FastAPI()

origins = [
    # "http://localhost",
    # "http://localhost:8080",
    # "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    _CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(_users_router)
app.include_router(_boards_router)
app.include_router(_board_labels_router)
app.include_router(_lists_router)
app.include_router(_cards_router)
app.include_router(_comments_router)
app.include_router(_check_lists_router)
app.include_router(_card_member_router)
app.include_router(_card_activity_router)
app.include_router(_card_label_router)
app.include_router(_card_attachment_router)


# TODO: UPDATE MODELS TO USE RELATIONSHIPS. ALSO UPDATE ENDPOINTS TO USE RELATIONSHIPS


@app.get("/")
async def root():
    return {"message": "Hello World"}
