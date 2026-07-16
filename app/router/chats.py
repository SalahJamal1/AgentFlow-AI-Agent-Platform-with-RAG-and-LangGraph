from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Depends
from sqlalchemy.orm import joinedload

from app.dependencies import db_dependency
from app.models import Conversations, Messages
from app.router.auth import get_current_user
from app.schema import CreateConversations, CreateMessages
from graph.graph import app
from graph.graph_deep import app_deep

router = APIRouter(
    prefix="/api/v1/chats",
    tags=["chats"],
)

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/")
def get_all_conversations(user: user_dependency, db: db_dependency):
    if not user:
        raise HTTPException(status_code=400, detail="you are not logged in")

    conversations = (
        db.query(Conversations).filter(Conversations.user_id == user.get("id")).all()
    )
    return conversations


@router.get("/{id}")
def get_conversation(user: user_dependency, db: db_dependency, id: int = Path(gt=0)):
    if not user:
        raise HTTPException(status_code=400, detail="you are not logged in")
    conversation = (
        db.query(Conversations)
        .options(joinedload(Conversations.messages))
        .filter(Conversations.id == id, Conversations.user_id == user.get("id"))
        .first()
    )
    if not conversation:
        raise HTTPException(status_code=404, detail="conversation not found")

    return conversation


@router.post("/")
def create_conversation(
        user: user_dependency,
        db: db_dependency,
        new_conversation: CreateConversations,
):
    if not user:
        raise HTTPException(status_code=400, detail="you are not logged in")
    conversation = Conversations(title=new_conversation.title)
    conversation.user_id = user.get("id")
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


@router.post("/{conversation_id}/messages")
def send_message(
        user: user_dependency,
        db: db_dependency,
        message: CreateMessages,
        conversation_id: int,
        deep: bool = Query(False),
):
    conversation = get_conversation(user, db, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    try:
        user_message = Messages(
            conversations_id=conversation.id, role="user", content=message.content
        )

        db.add(user_message)
        db.flush()
        graph = app_deep if deep else app

        response = graph.invoke({"question": message.content})

        ai_message = Messages(
            conversations_id=conversation.id,
            role="assistant",
            content=response["generation"],
        )

        db.add(ai_message)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="something went wrong")
    history = (
        db.query(Messages)
        .filter(Messages.conversations_id == conversation.id)
        .order_by(Messages.created_at)
        .all()
    )
    return history


@router.get("/{conversation_id}/messages")
def get_message(
        user: user_dependency,
        db: db_dependency,
        conversation_id: int,
):
    conversation = get_conversation(user, db, conversation_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    history = (
        db.query(Messages)
        .filter(Messages.conversations_id == conversation.id)
        .order_by(Messages.created_at)
        .all()
    )
    return history
