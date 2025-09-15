"""
Todo API endpoints.
FR-001 focused: POST /todos endpoint only
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.database.config import get_db
from src.models.todo import TodoCreate, TodoResponse
from src.services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("/", response_model=TodoResponse, status_code=201)
def create_todo(todo_data: TodoCreate, db: Session = Depends(get_db)):
    """新しいTodoを作成 (FR-001)"""
    service = TodoService(db)
    return service.create_todo(todo_data)
