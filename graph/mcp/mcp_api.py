import os

from jose import jwt, JWTError
from mcp.server.fastmcp import FastMCP

from app.database import SessionLocal
from app.models import Conversations

SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = os.getenv("ALGORITHM", "")
ISSUER = os.getenv("ISSUER", "")
AUDIENCE = os.getenv("AUDIENCE", "")

mcp = FastMCP("Mcp Chat Server")


@mcp.tool()
def get_chat_history(access_token: str) -> list[dict]:
    """Get all conversations for the authenticated user."""

    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=AUDIENCE,
            issuer=ISSUER,
        )
    except JWTError as e:
        raise ValueError(f"Could not validate credentials - {e}")

    user_id = payload.get("id")
    if user_id is None:
        raise ValueError("Could not validate credentials")

    db = SessionLocal()
    try:
        conversations = (
            db.query(Conversations)
            .filter(Conversations.user_id == user_id)
            .order_by(Conversations.created_at.asc())
            .all()
        )
        return [
            {
                "conversation_id": conversation.id,
                "title": conversation.title,
                "messages": [
                    {"role": message.role, "content": message.content}
                    for message in conversation.messages
                ],
            }
            for conversation in conversations
        ]
    finally:
        db.close()


if __name__ == "__main__":
    mcp.run()
