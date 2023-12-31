from fastapi import APIRouter as _APIRouter, Depends as _Depends, HTTPException as _HTTPException, status as _status, \
    security as _security
from . import board_services as _board_services
from ..users.user_services import get_current_user as _get_current_user
from ..users import user_services as _user_services
from ..cards import card_services as _card_services
from ..users import user_schemas as _user_schemas
from ..boards.board_services import get_member_board as _get_member_board, get_current_board as _get_current_board

from ..database import get_db as _get_db
from . import board_schemas as _board_schemas
from sqlalchemy.orm import Session as _Session

router = _APIRouter(
    prefix="/boards",
    tags=["boards"],
)

board_labels_router = _APIRouter(
    prefix="/boards/{board_id}/labels",
    tags=["board_labels"],
)

current_user_dependency = _Depends(_get_current_user)
board_dependency = _Depends(_get_current_board)
member_board_dependency = _Depends(_get_member_board)


# TODO: UPDATE BOARD ENDPOINTS TO USE MEMBER BOARD DEPENDENCY

@router.get("/get_full_board", response_model=_board_schemas.FullBoard)
async def get_full_board(board: _board_schemas.FullBoard = board_dependency):
    board_lists = board.lists
    _ = [lists.cards for lists in board_lists]
    return board


# endpoint to add member to board
@router.post("/add_member/{board_id}", response_model=_board_schemas.Board)
async def add_member_to_board(board_add: _board_schemas.BoardAddMember, db: _Session = _Depends(_get_db),
                              board: _board_schemas.Board = _Depends(_board_services.get_current_board),
                              current_user: _user_schemas.User = current_user_dependency):
    # get user by email
    user_to_add = await _user_services.get_user_by_email(db=db, email=board_add.email)
    if not user_to_add:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    # # check if user is owner
    # if board.owner_id == current_user.id:
    #     raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail="You are the owner of this board")
    # check if user is already a member
    if await _board_services.user_is_board_member(db=db, board_id=board.id, user_id=user_to_add.id):
        raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail="User is already a member")

    # add user to board
    await _board_services.add_member_to_board(db=db, board_id=board.id, member_id=user_to_add.id)
    return _board_schemas.Board.from_orm(board)


# endpoint to remove member from board
@router.post("/remove_member/{board_id}", status_code=_status.HTTP_204_NO_CONTENT)
async def remove_member_from_board(board_remove: _board_schemas.BoardRemoveMember, db: _Session = _Depends(_get_db),
                                   board: _board_schemas.Board = _Depends(_board_services.get_current_board),
                                   current_user: _user_schemas.User = current_user_dependency):
    # get user by email
    user_to_remove = await _user_services.get_user_by_email(db=db, email=board_remove.email)
    if not user_to_remove:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    # # check if user is owner
    # if current_user.id == board.owner_id:
    #     raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail="You are the owner of this board")
    # check if user is already a member
    if not await _board_services.user_is_board_member(db=db, board_id=board.id, user_id=user_to_remove.id):
        raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST, detail="User is not a member")
    # if user is owner, raise error
    if user_to_remove.id == board.owner_id:
        raise _HTTPException(status_code=_status.HTTP_400_BAD_REQUEST,
                             detail="You cannot remove the owner of the board")

    # remove user from board
    await _board_services.remove_member_from_board(db=db, board_id=board.id, member_id=user_to_remove.id)

    # remove user from all cards in board
    # TODO: IMPLEMENT THIS
    # await _card_services.remove_member_from_all_cards_in_board(db=db, board_id=board.id, user_id=user_to_remove.id)


# list all members of a board
@router.get("/members/{board_id}", response_model=list[_user_schemas.User])
async def get_board_members(board: _board_schemas.Board = _Depends(_board_services.get_current_board),
                            db: _Session = _Depends(_get_db),
                            current_user: _user_schemas.User = current_user_dependency):
    if not await _board_services.user_is_board_member(db=db, board_id=board.id, user_id=current_user.id):
        raise _HTTPException(status_code=_status.HTTP_401_UNAUTHORIZED, detail="You are not a member of this board")
    members = await _board_services.get_board_members(db=db, board_id=board.id)

    # using the user_id from the members, get the user object and return the list of users. make sure to convert to user schema
    return [_user_schemas.User.from_orm(await _user_services.get_user_by_id(db=db, user_id=member.user_id)) for member
            in members]


@router.post("/create_board", response_model=_board_schemas.Board)
async def create_board(board: _board_schemas.BoardCreate, db: _Session = _Depends(_get_db),
                       current_user: _user_schemas.User = current_user_dependency):
    board = await _board_services.create_board(db=db, board=board, owner_id=current_user.id)
    # add owner as member
    await _board_services.add_member_to_board(db=db, board_id=board.id, member_id=current_user.id)
    return _board_schemas.Board.from_orm(board)


@router.get("/me", response_model=list[_board_schemas.Board])
async def read_boards_by_user(db: _Session = _Depends(_get_db),
                              current_user: _user_schemas.User = current_user_dependency):
    # get all boards where the user is a member
    db_boards = await _board_services.get_boards_members_by_user_id(db=db, user_id=current_user.id)
    # for each board, get the board object and return the list of boards. make sure to convert to board schema
    return [_board_schemas.Board.from_orm(await _board_services.get_board_by_id(db=db, board_id=board.board_id)) for
            board in db_boards]


@router.get("/public", response_model=list[_board_schemas.Board])
async def read_boards_by_user(db: _Session = _Depends(_get_db)):
    db_boards = await _board_services.get_public_boards(db=db)
    return [_board_schemas.Board.from_orm(board) for board in db_boards]


@router.get("/me/{board_id}", response_model=_board_schemas.Board)
async def read_user_board(board_id: int, db: _Session = _Depends(_get_db),
                          current_user: _user_schemas.User = current_user_dependency):
    db_board = await _board_services.get_user_board_by_id(db=db, board_id=board_id, owner_id=current_user.id)
    if db_board is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Board not found")
    return _board_schemas.Board.from_orm(db_board)


# endpoint to get board by id. If the board is private, then only the owner can access it. else, anyone can access it.
@router.get("/{board_id}", response_model=_board_schemas.Board)
async def read_user_board(board_id: int, db: _Session = _Depends(_get_db),
                          current_user: _user_schemas.User = current_user_dependency):
    db_board = await _board_services.get_board_by_id(db=db, board_id=board_id)
    if db_board is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Board not found")
    if db_board.is_public:
        return _board_schemas.Board.from_orm(db_board)
    else:
        if db_board.owner_id == current_user.id:
            return _board_schemas.Board.from_orm(db_board)
        else:
            raise _HTTPException(status_code=_status.HTTP_401_UNAUTHORIZED,
                                 detail="You are not authorized to access this board")


@router.put("/{board_id}", response_model=_board_schemas.Board, dependencies=[current_user_dependency])
async def update_user_board(board_data: _board_schemas.BoardUpdate, db: _Session = _Depends(_get_db),
                            board=member_board_dependency):
    board = await _board_services.update_board(db=db, board=board_data, db_board=board)
    return _board_schemas.Board.from_orm(board)


@router.delete("/{board_id}", status_code=_status.HTTP_204_NO_CONTENT)
async def delete_user_board(board_id: int, db: _Session = _Depends(_get_db),
                            current_user: _user_schemas.User = current_user_dependency):
    db_board = await _board_services.get_user_board_by_id(db=db, board_id=board_id, owner_id=current_user.id)
    if db_board is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Board not found")
    await _board_services.delete_all_members_from_board(db=db, board_id=board_id)
    _ = await _board_services.delete_board(db=db, db_board=db_board)
    #     remove all members from board



# board labels
# TODO: WHEN A LABEL IS DELETED, REMOVE IT FROM ALL CARDS
@board_labels_router.post("", response_model=_board_schemas.BoardLabel, dependencies=[current_user_dependency])
async def create_board_label(board_label: _board_schemas.BoardLabelCreate, db: _Session = _Depends(_get_db),
                             board=member_board_dependency):
    db_board_label = await _board_services.create_board_label(db=db, board_label=board_label, board_id=board.id)
    return _board_schemas.BoardLabel.from_orm(db_board_label)


@board_labels_router.get("", response_model=list[_board_schemas.BoardLabel])
async def read_board_labels(db: _Session = _Depends(_get_db), board=board_dependency):
    db_board_labels = await _board_services.get_board_labels(db=db, board_id=board.id)
    return [_board_schemas.BoardLabel.from_orm(board_label) for board_label in db_board_labels]


@board_labels_router.get("/{label_id}", response_model=_board_schemas.BoardLabel)
async def read_board_label(label_id: int, db: _Session = _Depends(_get_db), board=board_dependency):
    db_board_label = await _board_services.get_board_label(db=db, board_id=board.id, label_id=label_id)
    if db_board_label is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Label not found")
    return _board_schemas.BoardLabel.from_orm(db_board_label)


@board_labels_router.put("/{label_id}", response_model=_board_schemas.BoardLabel,
                         dependencies=[current_user_dependency])
async def update_board_label(label_id: int, board_label: _board_schemas.BoardLabelUpdate,
                             db: _Session = _Depends(_get_db), board=member_board_dependency):
    db_board_label = await _board_services.get_board_label(db=db, board_id=board.id, label_id=label_id)
    if db_board_label is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Label not found")
    db_board_label = await _board_services.update_board_label(db=db, board_label=board_label,
                                                              db_board_label=db_board_label)
    return _board_schemas.BoardLabel.from_orm(db_board_label)


@board_labels_router.delete("/{label_id}", status_code=_status.HTTP_204_NO_CONTENT,
                            dependencies=[current_user_dependency])
async def delete_board_label(label_id: int, db: _Session = _Depends(_get_db), board=member_board_dependency):
    db_board_label = await _board_services.get_board_label(db=db, board_id=board.id, label_id=label_id)
    if db_board_label is None:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Label not found")
    await _board_services.delete_board_label(db=db, db_board_label=db_board_label)
