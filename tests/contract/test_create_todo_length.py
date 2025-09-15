"""
Contract test for POST /todos text length validation (TC-003)
This test MUST fail before implementation.
"""
from fastapi.testclient import TestClient


def test_create_todo_text_too_long_validation_error():
    """1000文字超過でのバリデーションエラー (TC-003)"""
    from src.main import app

    with TestClient(app) as client:
        # Given
        long_text = "a" * 1001
        request_data = {"text": long_text, "completed": False}

        # When
        response = client.post("/todos", json=request_data)

        # Then
        assert response.status_code == 422
        error_data = response.json()
        assert "detail" in error_data

        error = error_data["detail"][0]
        assert error["loc"] == ["body", "text"]
        assert "1000" in error["msg"]  # Max length mentioned in error
