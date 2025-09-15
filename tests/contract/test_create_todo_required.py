"""
Contract test for POST /todos required field validation (TC-004)
This test MUST fail before implementation.
"""
from fastapi.testclient import TestClient


def test_create_todo_missing_required_field():
    """必須フィールド（text）不足エラー (TC-004)"""
    from src.main import app

    with TestClient(app) as client:
        # Given
        request_data = {"completed": False}  # text field missing

        # When
        response = client.post("/todos", json=request_data)

        # Then
        assert response.status_code == 422
        error_data = response.json()

        error = error_data["detail"][0]
        assert error["loc"] == ["body", "text"]
        assert "required" in error["type"] or "missing" in error["msg"] or "Field required" in error["msg"]
