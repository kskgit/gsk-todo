# Data Model: Todo管理システム (FastAPI + SQLAlchemy)

## Core Models

### SQLAlchemy Models (Database Layer)

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

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
```

### Pydantic Models (API Layer)

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class TodoBase(BaseModel):
    """Common Todo fields"""
    text: str = Field(..., min_length=1, max_length=1000, description="Todo内容テキスト")
    completed: bool = Field(default=False, description="完了フラグ")

class TodoCreate(TodoBase):
    """Todo作成時のリクエストモデル"""
    pass

class TodoUpdate(BaseModel):
    """Todo更新時のリクエストモデル（部分更新対応）"""
    text: Optional[str] = Field(None, min_length=1, max_length=1000)
    completed: Optional[bool] = None

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
```

## Field Specifications

### TodoDB Fields (SQLAlchemy)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | PK, AUTO_INCREMENT, INDEX | 一意識別子 |
| text | String(1000) | NOT NULL | Todo内容（最大1000文字） |
| completed | Boolean | NOT NULL, DEFAULT=False | 完了状態 |
| created_at | DateTime | NOT NULL, DEFAULT=NOW() | 作成日時（UTC） |
| updated_at | DateTime | NOT NULL, DEFAULT=NOW(), ON UPDATE=NOW() | 更新日時（UTC） |

### Pydantic Validation Rules

```python
# text field validation
text: str = Field(
    ...,
    min_length=1,        # 空文字列禁止
    max_length=1000,     # 最大1000文字
    strip_whitespace=True,  # 前後の空白除去
    description="Todo内容テキスト"
)

# completed field validation  
completed: bool = Field(
    default=False,
    description="完了フラグ"
)
```

## Business Logic & Validation

### Custom Validators

```python
from pydantic import field_validator
from typing import Any

class TodoCreate(TodoBase):
    @field_validator('text')
    @classmethod
    def validate_text_not_only_whitespace(cls, v: str) -> str:
        if not v or v.strip() == "":
            raise ValueError("Todo text cannot be empty or whitespace only")
        return v.strip()
    
    @field_validator('text')
    @classmethod
    def validate_text_length(cls, v: str) -> str:
        if len(v) > 1000:
            raise ValueError("Todo text cannot exceed 1000 characters")
        return v
```

### Database Constraints

```sql
-- SQLAlchemy will generate equivalent DDL
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text VARCHAR(1000) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX ix_todos_id ON todos (id);
```

## CRUD Operations

### Service Layer Interface

```python
from typing import Optional, List
from sqlalchemy.orm import Session

class TodoService:
    """Todo operations service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_todo(self, todo_data: TodoCreate) -> TodoResponse:
        """新しいTodoを作成"""
        db_todo = TodoDB(**todo_data.model_dump())
        self.db.add(db_todo)
        self.db.commit()
        self.db.refresh(db_todo)
        return TodoResponse.model_validate(db_todo)
    
    def get_todo(self, todo_id: int) -> Optional[TodoResponse]:
        """IDでTodoを取得"""
        db_todo = self.db.query(TodoDB).filter(TodoDB.id == todo_id).first()
        if db_todo:
            return TodoResponse.model_validate(db_todo)
        return None
    
    def get_todos(self, skip: int = 0, limit: int = 100) -> TodoListResponse:
        """Todo一覧を取得（ページネーション対応）"""
        todos = self.db.query(TodoDB).offset(skip).limit(limit).all()
        total = self.db.query(TodoDB).count()
        return TodoListResponse(
            todos=[TodoResponse.model_validate(todo) for todo in todos],
            total=total
        )
    
    def update_todo(self, todo_id: int, todo_update: TodoUpdate) -> Optional[TodoResponse]:
        """Todoを更新（部分更新対応）"""
        db_todo = self.db.query(TodoDB).filter(TodoDB.id == todo_id).first()
        if not db_todo:
            return None
        
        update_data = todo_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_todo, field, value)
        
        self.db.commit()
        self.db.refresh(db_todo)
        return TodoResponse.model_validate(db_todo)
    
    def delete_todo(self, todo_id: int) -> bool:
        """Todoを削除"""
        db_todo = self.db.query(TodoDB).filter(TodoDB.id == todo_id).first()
        if not db_todo:
            return False
        
        self.db.delete(db_todo)
        self.db.commit()
        return True
```

## Database Configuration

### Connection Setup

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# インメモリSQLite database
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # SQLite用設定
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """データベーステーブル作成"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """データベースセッション依存性注入"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## Error Handling

### Custom Exceptions

```python
from fastapi import HTTPException
from typing import Optional

class TodoNotFoundError(HTTPException):
    def __init__(self, todo_id: int):
        super().__init__(
            status_code=404,
            detail=f"Todo with id {todo_id} not found"
        )

class TodoValidationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(
            status_code=422,
            detail=message
        )

class DatabaseError(HTTPException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(
            status_code=500,
            detail=message
        )
```

## API Response Formats

### Success Responses

```python
# GET /todos/{id} - 200 OK
{
    "id": 1,
    "text": "サンプルTodo",
    "completed": false,
    "created_at": "2025-09-13T10:00:00.000Z",
    "updated_at": "2025-09-13T10:00:00.000Z"
}

# GET /todos - 200 OK
{
    "todos": [
        {
            "id": 1,
            "text": "サンプルTodo",
            "completed": false,
            "created_at": "2025-09-13T10:00:00.000Z",
            "updated_at": "2025-09-13T10:00:00.000Z"
        }
    ],
    "total": 1
}

# POST /todos - 201 Created
{
    "id": 2,
    "text": "新しいTodo",
    "completed": false,
    "created_at": "2025-09-13T11:00:00.000Z",
    "updated_at": "2025-09-13T11:00:00.000Z"
}
```

### Error Responses

```python
# 404 Not Found
{
    "detail": "Todo with id 999 not found"
}

# 422 Unprocessable Entity (Validation Error)
{
    "detail": [
        {
            "type": "string_too_short",
            "loc": ["body", "text"],
            "msg": "String should have at least 1 character",
            "input": ""
        }
    ]
}

# 500 Internal Server Error
{
    "detail": "Database operation failed"
}
```

## Testing Models

### Test Data Factories

```python
import pytest
from datetime import datetime
from .models import TodoCreate, TodoUpdate, TodoResponse

class TodoFactory:
    """Test data factory for Todo models"""
    
    @staticmethod
    def create_todo_data(**kwargs) -> TodoCreate:
        defaults = {
            "text": "テストTodo",
            "completed": False
        }
        defaults.update(kwargs)
        return TodoCreate(**defaults)
    
    @staticmethod
    def update_todo_data(**kwargs) -> TodoUpdate:
        return TodoUpdate(**kwargs)
    
    @staticmethod
    def todo_response_data(**kwargs) -> dict:
        defaults = {
            "id": 1,
            "text": "テストTodo",
            "completed": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        defaults.update(kwargs)
        return defaults
```

## Performance Considerations

### Database Optimization

- **Indexing**: id フィールドに自動インデックス
- **Connection Pooling**: SQLAlchemy default pooling
- **Query Optimization**: N+1問題なし（単一テーブル）

### Memory Usage

- **Estimated**: 1000 todos ≈ 500KB in memory
- **Pagination**: デフォルト100件制限
- **Connection**: インメモリDBで接続オーバーヘッド最小

### Future Scaling

- **Persistent Storage**: SQLite file or PostgreSQL
- **Async SQLAlchemy**: 高負荷時の非同期DB操作
- **Caching**: Redis for read-heavy workloads