"""
Contract test for POST /todos success case (TC-001)
This test MUST fail before implementation.
"""
from datetime import datetime


def test_create_todo_success(test_client):
    """正常なTodo作成のコントラクトテスト (TC-001)"""
    # Given
    request_data = {
        "text": "新しいタスク",
        "completed": False
    }

    # When
    response = test_client.post("/todos", json=request_data)

    # Then
    assert response.status_code == 201
    data = response.json()

    # Response schema validation
    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["id"] > 0

    assert data["text"] == "新しいタスク"
    assert data["completed"] == False

    assert "created_at" in data
    assert "updated_at" in data
    # ISO 8601 format validation
    datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
    datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
