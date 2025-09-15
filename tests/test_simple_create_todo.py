"""
Simple test for FR-001: Todo creation functionality
This bypasses the complex dependency injection issues.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database.config import Base
from src.models.todo import TodoCreate, TodoDB
from src.services.todo_service import TodoService


def test_simple_create_todo():
    """FR-001: Todo作成機能の直接テスト"""
    # Create test database
    test_engine = create_engine("sqlite:///:memory:")
    TestSessionLocal = sessionmaker(bind=test_engine)

    # Create tables
    Base.metadata.create_all(bind=test_engine)

    # Test the service directly
    db = TestSessionLocal()
    try:
        service = TodoService(db)

        # Create a todo
        todo_data = TodoCreate(text="テストTodo", completed=False)
        result = service.create_todo(todo_data)

        # Verify the result
        assert result.id > 0
        assert result.text == "テストTodo"
        assert result.completed == False
        assert result.created_at is not None
        assert result.updated_at is not None

        # Verify it was saved to database
        saved_todo = db.query(TodoDB).filter(TodoDB.id == result.id).first()
        assert saved_todo is not None
        assert saved_todo.text == "テストTodo"
        assert saved_todo.completed == False

        print(f"✅ FR-001 Success: Created todo with ID {result.id}")

    finally:
        db.close()


if __name__ == "__main__":
    test_simple_create_todo()
    print("🎉 FR-001 Todo creation works!")
