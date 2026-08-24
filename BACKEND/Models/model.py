from sqlalchemy import Column,Integer,String,ForeignKey,Text,Float,Boolean,DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from BACKEND.Database.database import Base


# ============================================================
# USERS
# ============================================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)

    chat_history = relationship(
        "ChatHistory",
        cascade="all, delete-orphan",
        back_populates="user",
    )

    context_chunks = relationship(
        "ContextChunks",
        cascade="all, delete-orphan",
        back_populates="user",
    )


# ============================================================
# CHAT HISTORY
# ============================================================

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        index=True,
        nullable=False,
    )

    user_query = Column(Text, nullable=False)
    bot_response = Column(Text, nullable=False)

    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship(
        "User",
        back_populates="chat_history",
    )


# ============================================================
# CONTEXT CHUNKS
# PostgreSQL metadata/source of truth for PDF chunks
# ============================================================

class ContextChunks(Base):
    __tablename__ = "context_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String, index=True)
    chunk_id = Column(String, unique=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        index=True,
        nullable=True,
    )

    chunk_text = Column(Text, nullable=False)
    source = Column(String)
    file_name = Column(String)
    file_type = Column(String)
    page_number = Column(Integer)
    row_number = Column(Integer)
    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )
    user = relationship(
        "User",
        back_populates="context_chunks",
    )