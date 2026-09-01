from datetime import timezone, datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped,mapped_column

from app.database import Base


class Users(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    first_name:Mapped[str] = mapped_column(String(255), nullable=False)
    last_name:Mapped[str] = mapped_column(String(255), nullable=False)
    email:Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password:Mapped[str] = mapped_column(String(255), nullable=False)
    created_at:Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at:Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), onupdate=lambda: datetime.now(timezone.utc)
    )


class Conversations(Base):
    __tablename__ = "conversations"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    title:Mapped[str] = mapped_column(Text, nullable=False)
    created_at:Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    messages = relationship(
        "Messages",
        order_by="Messages.created_at.asc()",
        cascade="all, delete-orphan",
    )
    user_id:Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)


class Messages(Base):
    __tablename__ = "messages"
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    role:Mapped[str] = mapped_column(String(255), nullable=False)
    content:Mapped[str] = mapped_column(Text, nullable=False)
    created_at:Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    conversations_id:Mapped[int] = mapped_column(Integer, ForeignKey("conversations.id"), nullable=False)
