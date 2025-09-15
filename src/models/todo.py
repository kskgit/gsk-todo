"""
Todo models: SQLAlchemy ORM and Pydantic API models.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from src.database.config import Base


# SQLAlchemy ORM Model
class TodoDB(Base):
    """SQLAlchemy ORM model for Todo items"""
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(String(1000), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Todo(id={self.id}, text='{self.text[:30]}...', completed={self.completed})>"


# Pydantic API Models
class TodoBase(BaseModel):
    """Common Todo fields"""
    text: str = Field(..., min_length=1, max_length=1000, description="Todo内容テキスト")
    completed: bool = Field(default=False, description="完了フラグ")


class TodoCreate(TodoBase):
    """Todo作成時のリクエストモデル"""
    pass


class TodoUpdate(BaseModel):
    """Todo更新時のリクエストモデル（部分更新対応）"""
    text: str | None = Field(None, min_length=1, max_length=1000)
    completed: bool | None = None


class TodoResponse(TodoBase):
    """Todo API レスポンスモデル"""
    id: int = Field(..., description="Todo ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)


class TodoListResponse(BaseModel):
    """Todo一覧取得のレスポンスモデル"""
    todos: list[TodoResponse]
    total: int = Field(..., description="総件数")
