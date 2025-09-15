"""
Todo service layer for business logic and CRUD operations.
FR-001 focused: create_todo method only
"""
from sqlalchemy.orm import Session

from src.models.todo import TodoCreate, TodoDB, TodoResponse


class TodoService:
    """Todo operations service"""

    def __init__(self, db: Session):
        self.db = db

    def create_todo(self, todo_data: TodoCreate) -> TodoResponse:
        """新しいTodoを作成 (FR-001)"""
        db_todo = TodoDB(**todo_data.model_dump())
        self.db.add(db_todo)
        self.db.commit()
        self.db.refresh(db_todo)
        return TodoResponse.model_validate(db_todo)
