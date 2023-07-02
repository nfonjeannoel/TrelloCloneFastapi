import shutil

from fastapi import APIRouter as _APIRouter, Depends as _Depends, HTTPException as _HTTPException, status as _status, \
    security as _security, UploadFile as _UploadFile
from . import card_services as _card_services
from ..users.user_services import get_current_user as _get_current_user
from ..boards.board_services import get_current_board as _get_current_board
from ..boards.board_services import get_member_board as _get_member_board
from ..boards import board_services as _board_services
from ..lists.list_services import get_current_list as _get_current_list
from ..lists.list_services import get_member_list as _get_member_list
from ..lists import list_services as _list_services
from ..users import user_schemas as _user_schemas
from ..users import user_services as _user_services
from ..database import get_db as _get_db
from . import card_schemas as _card_schemas
from sqlalchemy.orm import Session as _Session
from ..boards import board_schemas as _board_schemas
from ..lists import list_schemas as _list_schemas
import datetime as _dt

card_router = _APIRouter(
    prefix="/cards",
    tags=["cards"],
)

comments_router = _APIRouter(
    prefix="/comments",
    tags=["comments"],
)

checklists_router = _APIRouter(
    prefix="/checklists",
    tags=["checklists"],
)

card_member_router = _APIRouter(
    prefix="/card_members",
    tags=["card_members"],
)

card_activity_router = _APIRouter(
    prefix="/card_activity",
    tags=["card_activity"],
)

card_label_router = _APIRouter(
    prefix="/card_labels",
    tags=["card_labels"],
)

card_attachment_router = _APIRouter(
    prefix="/card_attachments",
    tags=["card_attachments"],
)

current_user_dependency = _Depends(_get_current_user)
board_dependency = _Depends(_get_current_board)
member_board_dependency = _Depends(_get_member_board)
list_dependency = _Depends(_get_current_list)
member_list_dependency = _Depends(_get_member_list)

card_activities = {
    "create_card": "{} created this card",
    "update_card": "{} updated this card",
    "add_member": "{} added {} to this card",
    "remove_member": "{} removed {} from this card",
    "archive_card": "{} archived this card",
    "unarchive_card": "{} unarchived this card",
    "set_due_date": "{} set the due date for this card to {}",
    "add_attachment": "{} attached file '{}' to this card",
}


@card_router.post("/{board_id}/{list_id}/create_card", response_model=_card_schemas.Card)
async def create_card(card_data: _card_schemas.CardCreate, db: _Session = _Depends(_get_db),
                      current_user: _user_schemas.User = current_user_dependency,
                      list_data: _list_schemas.List = member_list_dependency):
    db_card = await _card_services.create_card(db=db, card_data=card_data, list_id=list_data.id)
    # add card activity
    activity = card_activities["create_card"].format(current_user.username)
    await _card_services.add_card_activity(db=db, card_id=db_card.id, user_id=current_user.id,
                                           activity=activity)
    return _card_schemas.Card.from_orm(db_card)


@card_router.get("/{board_id}/{list_id}/get_cards", response_model=list[_card_schemas.Card])
async def get_cards(db: _Session = _Depends(_get_db), list_data: _list_schemas.List = list_dependency):
    db_cards = await _card_services.get_cards_by_list(db=db, list_id=list_data.id)
    return [_card_schemas.Card.from_orm(db_card) for db_card in db_cards]


@card_router.get("/{board_id}/{list_id}/{card_id}/get_card", response_model=_card_schemas.Card)
async def get_card(card_id: int, list_data: _list_schemas.List = list_dependency, db: _Session = _Depends(_get_db), ):
    db_card = await _card_services.get_card_by_id(db=db, card_id=card_id, list_id=list_data.id)
    return _card_schemas.Card.from_orm(db_card)


@card_router.put("/{board_id}/{list_id}/{card_id}/update_card", response_model=_card_schemas.Card)
async def update_card(card_data: _card_schemas.CardUpdate, card_id: int,
                      list_data: _list_schemas.List = member_list_dependency,
                      db: _Session = _Depends(_get_db)):
    db_card = await _card_services.get_card_by_id(db=db, card_id=card_id, list_id=list_data.id)
    if not db_card:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Card not found")
    # check if list_id exists in db
    db_list = await _list_services.get_list_by_id(db=db, list_id=card_data.list_id)
    if not db_list:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="List not found")
    db_card = await _card_services.update_card(db=db, card_data=card_data, db_card=db_card)

    # add card activity
    activity = card_activities["update_card"].format(db_card.user.username)
    return _card_schemas.Card.from_orm(db_card)


@card_router.delete("/{board_id}/{list_id}/{card_id}/delete_card", status_code=_status.HTTP_204_NO_CONTENT)
async def delete_card(card_id: int, list_data: _list_schemas.List = member_list_dependency,
                      db: _Session = _Depends(_get_db)):
    db_card = await _card_services.get_card_by_id(db=db, card_id=card_id, list_id=list_data.id)
    if not db_card:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Card not found")
    db_card = await _card_services.delete_card(db=db, db_card=db_card)


# set due date
@card_router.put("/{board_id}/{list_id}/{card_id}/set_due_date", response_model=_card_schemas.Card)
async def set_due_date(card_id: int, card_data: _card_schemas.CardDueDate,
                       list_data: _list_schemas.List = member_list_dependency,
                       current_user: _user_schemas.User = current_user_dependency,
                       db: _Session = _Depends(_get_db)):
    db_card = await _card_services.get_card_by_id(db=db, card_id=card_id, list_id=list_data.id)
    if not db_card:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Card not found")
    db_card = await _card_services.set_due_date(db=db, db_card=db_card, card_data=card_data)

    # add card activity
    activity = card_activities["set_due_date"].format(current_user.username, card_data.due_date)

    await _card_services.add_card_activity(db=db, card_id=db_card.id, user_id=current_user.id,
                                           activity=activity)

    return _card_schemas.Card.from_orm(db_card)


# archive card
@card_router.put("/{board_id}/{list_id}/{card_id}/archive_card", response_model=_card_schemas.Card)
async def archive_card(card_id: int, list_data: _list_schemas.List = member_list_dependency,
                       db: _Session = _Depends(_get_db)):
    db_card = await _card_services.get_card_by_id(db=db, card_id=card_id, list_id=list_data.id)
    if not db_card:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Card not found")
    db_card = await _card_services.archive_card(db=db, db_card=db_card)

    # add card activity
    activity = card_activities["archive_card"].format(db_card.user.username)
    await _card_services.add_card_activity(db=db, card_id=db_card.id, user_id=db_card.user_id,
                                           activity=activity)

    return _card_schemas.Card.from_orm(db_card)


# unarchive card
@card_router.put("/{board_id}/{list_id}/{card_id}/unarchive_card", response_model=_card_schemas.Card)
async def unarchive_card(card_id: int, list_data: _list_schemas.List = member_list_dependency,
                         db: _Session = _Depends(_get_db)):
    db_card = await _card_services.get_card_by_id(db=db, card_id=card_id, list_id=list_data.id)
    if not db_card:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Card not found")
    db_card = await _card_services.unarchive_card(db=db, db_card=db_card)

    # add card activity
    activity = card_activities["unarchive_card"].format(db_card.user.username)
    await _card_services.add_card_activity(db=db, card_id=db_card.id, user_id=db_card.user_id,
                                           activity=activity)

    return _card_schemas.Card.from_orm(db_card)


# comments


@comments_router.post("/{board_id}/{list_id}/{card_id}/create_comment", response_model=_card_schemas.Comment,
                      dependencies=[member_list_dependency])
async def create_comment(comment_data: _card_schemas.CommentCreate, card_id: int,
                         current_user: _user_schemas.User = current_user_dependency,
                         db: _Session = _Depends(_get_db)):
    db_comment = await _card_services.create_comment(db=db, comment_data=comment_data, card_id=card_id,
                                                     user_id=current_user.id)
    return _card_schemas.Comment.from_orm(db_comment)


@comments_router.get("/{board_id}/{list_id}/{card_id}/get_comments", response_model=list[_card_schemas.Comment],
                     dependencies=[list_dependency])
async def get_comments(card_id: int, db: _Session = _Depends(_get_db)):
    db_comments = await _card_services.get_comments_by_card(db=db, card_id=card_id)
    return [_card_schemas.Comment.from_orm(db_comment) for db_comment in db_comments]


@comments_router.get("/{board_id}/{list_id}/{card_id}/{comment_id}/get_comment", response_model=_card_schemas.Comment,
                     dependencies=[list_dependency, current_user_dependency])
async def get_comment(comment_id: int, card_id: int, db: _Session = _Depends(_get_db),
                      ):
    db_comment = await _card_services.get_comment_by_id(db=db, comment_id=comment_id, card_id=card_id)
    return _card_schemas.Comment.from_orm(db_comment)


@comments_router.put("/{board_id}/{list_id}/{card_id}/{comment_id}/update_comment",
                     response_model=_card_schemas.Comment,
                     dependencies=[member_list_dependency])
async def update_comment(comment_data: _card_schemas.CommentUpdate, comment_id: int, card_id: int,
                         current_user: _user_schemas.User = current_user_dependency,
                         db: _Session = _Depends(_get_db)):
    db_comment = await _card_services.get_comment_by_id(db=db, comment_id=comment_id, card_id=card_id)
    if not db_comment:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise _HTTPException(status_code=_status.HTTP_403_FORBIDDEN, detail="You can't update this comment")
    db_comment = await _card_services.update_comment(db=db, comment_data=comment_data, db_comment=db_comment)
    return _card_schemas.Comment.from_orm(db_comment)


@comments_router.delete("/{board_id}/{list_id}/{card_id}/{comment_id}/delete_comment",
                        status_code=_status.HTTP_204_NO_CONTENT,
                        dependencies=[member_list_dependency])
async def delete_comment(comment_id: int, card_id: int, current_user: _user_schemas.User = current_user_dependency,
                         db: _Session = _Depends(_get_db)):
    db_comment = await _card_services.get_comment_by_id(db=db, comment_id=comment_id, card_id=card_id)
    if not db_comment:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise _HTTPException(status_code=_status.HTTP_403_FORBIDDEN, detail="You can't delete this comment")
    db_comment = await _card_services.delete_comment(db=db, db_comment=db_comment)


# checklists


@checklists_router.post("/{board_id}/{card_id}/create_checklist", response_model=_card_schemas.CheckList,
                        dependencies=[member_board_dependency])
async def create_checklist(checklist_data: _card_schemas.CheckListCreate, card_id: int,
                           db: _Session = _Depends(_get_db)):
    db_checklist = await _card_services.create_checklist(db=db, checklist_data=checklist_data, card_id=card_id)
    return _card_schemas.CheckList.from_orm(db_checklist)


@checklists_router.get("/{board_id}/{card_id}/get_checklists", response_model=list[_card_schemas.CheckList],
                       dependencies=[board_dependency])
async def get_checklists(card_id: int, db: _Session = _Depends(_get_db)):
    db_checklists = await _card_services.get_checklists_by_card(db=db, card_id=card_id)
    return [_card_schemas.CheckList.from_orm(db_checklist) for db_checklist in db_checklists]


@checklists_router.get("/{board_id}/{card_id}/{checklist_id}/get_checklist", response_model=_card_schemas.CheckList,
                       dependencies=[board_dependency])
async def get_checklist(checklist_id: int, card_id: int, db: _Session = _Depends(_get_db)):
    db_checklist = await _card_services.get_checklist_by_id(db=db, checklist_id=checklist_id, card_id=card_id)
    return _card_schemas.CheckList.from_orm(db_checklist)


@checklists_router.put("/{board_id}/{card_id}/{checklist_id}/update_checklist", response_model=_card_schemas.CheckList,
                       dependencies=[member_board_dependency])
async def update_checklist(checklist_data: _card_schemas.CheckListUpdate, checklist_id: int, card_id: int,
                           db: _Session = _Depends(_get_db)):
    db_checklist = await _card_services.get_checklist_by_id(db=db, checklist_id=checklist_id, card_id=card_id)
    if not db_checklist:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    db_checklist = await _card_services.update_checklist(db=db, checklist_data=checklist_data,
                                                         db_checklist=db_checklist)
    return _card_schemas.CheckList.from_orm(db_checklist)


@checklists_router.delete("/{board_id}/{card_id}/{checklist_id}/delete_checklist",
                          status_code=_status.HTTP_204_NO_CONTENT,
                          dependencies=[member_board_dependency])
async def delete_checklist(checklist_id: int, card_id: int, db: _Session = _Depends(_get_db)):
    db_checklist = await _card_services.get_checklist_by_id(db=db, checklist_id=checklist_id, card_id=card_id)
    if not db_checklist:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Checklist not found")
    db_checklist = await _card_services.delete_checklist(db=db, db_checklist=db_checklist)


# card members

@card_member_router.post("/{board_id}/{card_id}/add_member", response_model=_card_schemas.CardMember)
async def add_card_member(card_id: int, card_member_data: _card_schemas.CardMemberCreate,
                          db: _Session = _Depends(_get_db),
                          current_user: _user_schemas.User = current_user_dependency,
                          board=member_board_dependency):
    db_user = await _user_services.get_user_by_email(db=db, email=card_member_data.email)
    if not db_user:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    # check if user is the member of the board
    if not await _board_services.user_is_board_member(db=db, user_id=db_user.id, board_id=board.id):
        raise _HTTPException(status_code=_status.HTTP_401_UNAUTHORIZED, detail="User is not a member of the board")
    db_card_member = await _card_services.get_card_member_by_user(db=db, user_id=db_user.id, card_id=card_id)
    if db_card_member:
        raise _HTTPException(status_code=_status.HTTP_409_CONFLICT, detail="User already added")

    db_card_member = await _card_services.add_card_member(db=db, card_id=card_id,
                                                          user_id=db_user.id)

    # add card activity
    activity = card_activities['add_member'].format(current_user.username, db_user.username)
    await _card_services.add_card_activity(db=db, card_id=card_id, user_id=current_user.id, activity=activity)

    return _card_schemas.CardMember.from_orm(db_card_member)


@card_member_router.get("/{board_id}/{card_id}/get_card_members", response_model=list[_card_schemas.CardMember],
                        dependencies=[board_dependency])
async def get_card_members(card_id: int, db: _Session = _Depends(_get_db)):
    db_card_members = await _card_services.get_card_members_by_card(db=db, card_id=card_id)
    return [_card_schemas.CardMember.from_orm(db_card_member) for db_card_member in db_card_members]


@card_member_router.get("/{board_id}/{card_id}/{card_member_id}/get_card_member",
                        response_model=_card_schemas.CardMember, dependencies=[board_dependency])
async def get_card_member(card_id: int, db: _Session = _Depends(_get_db),
                          current_user: _user_schemas.User = current_user_dependency):
    db_card_member = await _card_services.get_card_member_by_id(db=db, card_id=card_id, user_id=current_user.id)
    return _card_schemas.CardMember.from_orm(db_card_member)


@card_member_router.delete("/{board_id}/{card_id}/{card_member_id}/delete_card_member",
                           status_code=_status.HTTP_204_NO_CONTENT,
                           dependencies=[member_board_dependency])
async def delete_card_member(card_id: int, card_member: _card_schemas.CardMemberRemove,
                             current_user: _user_schemas.User = current_user_dependency,
                             db: _Session = _Depends(_get_db)):
    db_user = await _user_services.get_user_by_email(db=db, email=card_member.email)
    if not db_user:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    db_card_member = await _card_services.get_card_member_by_user(db=db, user_id=db_user.id, card_id=card_id)
    if not db_card_member:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="User not found")
    db_card_member = await _card_services.delete_card_member(db=db, db_card_member=db_card_member)

    # TODO: MAKE AN UPDATE. IDEALLY, SAVE THE USER ID INSTEAD OF NAME SO IT CAN BE DYANMIC. ie, if user changes name
    # add card activity
    activity = card_activities['remove_member'].format(current_user.username, db_user.username)
    await _card_services.add_card_activity(db=db, card_id=card_id, user_id=current_user.id, activity=activity)


# card activity

@card_activity_router.get("/{board_id}/{card_id}/get_card_activity", response_model=list[_card_schemas.CardActivity],
                          dependencies=[board_dependency])
async def get_card_activity(card_id: int, db: _Session = _Depends(_get_db)):
    db_card_activity = await _card_services.get_card_activity_by_card(db=db, card_id=card_id)
    return [_card_schemas.CardActivity.from_orm(db_card_activity) for db_card_activity in db_card_activity]


@card_activity_router.post("/{board_id}/{card_id}/add_card_activity", response_model=_card_schemas.CardActivity,
                           dependencies=[member_board_dependency])
async def add_card_activity(card_id: int, card_activity_data: _card_schemas.CardActivityCreate,
                            db: _Session = _Depends(_get_db),
                            current_user: _user_schemas.User = current_user_dependency):
    db_card_activity = await _card_services.add_card_activity(db=db, card_id=card_id,
                                                              user_id=current_user.id,
                                                              activity=card_activity_data.activity)
    return _card_schemas.CardActivity.from_orm(db_card_activity)


# card label

@card_label_router.post("/{board_id}/{card_id}/{label_id}/add_card_label", response_model=_card_schemas.CardLabel,
                        dependencies=[member_board_dependency, current_user_dependency])
async def add_card_label(card_id: int, label_id: int, db: _Session = _Depends(_get_db)):
    db_card_label = await _card_services.add_card_label(db=db, card_id=card_id,
                                                        label_id=label_id)
    if not db_card_label:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Label not found")
    return _card_schemas.CardLabel.from_orm(db_card_label)


@card_label_router.get("/{board_id}/{card_id}/get_card_labels", response_model=list[_card_schemas.CardLabel],
                       dependencies=[board_dependency])
async def get_card_labels(card_id: int, db: _Session = _Depends(_get_db)):
    db_card_labels = await _card_services.get_card_labels_by_card(db=db, card_id=card_id)
    return [_card_schemas.CardLabel.from_orm(db_card_label) for db_card_label in db_card_labels]


@card_label_router.delete("/{board_id}/{card_id}/{label_id}/delete_card_label",
                          status_code=_status.HTTP_204_NO_CONTENT,
                          dependencies=[member_board_dependency])
async def delete_card_label(card_id: int, label_id: int, db: _Session = _Depends(_get_db)):
    db_card_label = await _card_services.get_card_label_by_label(db=db, card_id=card_id, label_id=label_id)
    if not db_card_label:
        raise _HTTPException(status_code=_status.HTTP_404_NOT_FOUND, detail="Label not found")
    db_card_label = await _card_services.delete_card_label(db=db, db_card_label=db_card_label)
    return _card_schemas.CardLabel.from_orm(db_card_label)


# card attachment

# create an endpoint to upload files and pictures. use UploadFile from fastapi

@card_attachment_router.post("/{board_id}/{card_id}/add_card_attachment",
                             response_model=_card_schemas.CardAttachment,
                             dependencies=[member_board_dependency])
async def add_card_attachment(card_id: int, file: _UploadFile, db: _Session = _Depends(_get_db),
                              current_user: _user_schemas.User = current_user_dependency):
    # write file to storage and get path
    # TODO: SAVE FILE TO STORAGE
    # path = await _card_services.write_file_to_storage(file=file, folder_name='card_attachments')
    db_card_attachment = await _card_services.add_card_attachment(db=db, card_id=card_id, filename=file.filename,
                                                                  uploaded_date=str(_dt.date.today()),
                                                                  location="attachment/location")

    # add card activity
    activity = card_activities['add_attachment'].format(current_user.username, file.filename)

    await _card_services.add_card_activity(db=db, card_id=card_id, user_id=current_user.id, activity=activity)
    return _card_schemas.CardAttachment.from_orm(db_card_attachment)
