"""
Integration test for Todo creation workflow (T008)
This test MUST fail before implementation.
"""
from fastapi.testclient import TestClient


def test_todo_creation_workflow():
    """Todo作成ワークフローの統合テスト"""
    from src.main import app

    with TestClient(app) as client:
        # Given - Empty todo list
        initial_response = client.get("/todos")
        assert initial_response.status_code == 200
        initial_data = initial_response.json()
        assert initial_data["total"] == 0

        # When - Create a new todo
        create_data = {"text": "統合テストTodo", "completed": False}
        create_response = client.post("/todos", json=create_data)

        # Then - Todo is created successfully
        assert create_response.status_code == 201
        created_todo = create_response.json()
        assert created_todo["text"] == "統合テストTodo"
        assert created_todo["completed"] == False
        todo_id = created_todo["id"]

        # And - Todo appears in the list
        list_response = client.get("/todos")
        assert list_response.status_code == 200
        list_data = list_response.json()
        assert list_data["total"] == 1
        assert len(list_data["todos"]) == 1
        assert list_data["todos"][0]["id"] == todo_id

        # And - Todo can be retrieved individually
        get_response = client.get(f"/todos/{todo_id}")
        assert get_response.status_code == 200
        retrieved_todo = get_response.json()
        assert retrieved_todo["id"] == todo_id
        assert retrieved_todo["text"] == "統合テストTodo"
