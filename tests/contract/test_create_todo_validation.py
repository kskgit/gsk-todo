"""
Contract test for POST /todos validation errors (TC-002)
This test MUST fail before implementation.
"""
from fastapi.testclient import TestClient


def test_create_todo_empty_text_validation_error():
    """空テキストでのバリデーションエラー (TC-002)"""
    from src.main import app

    with TestClient(app) as client:
        # Given
        request_data = {"text": "", "completed": False}

        # When
        response = client.post("/todos", json=request_data)

        # Then
        assert response.status_code == 422
        error_data = response.json()

        assert "detail" in error_data
        assert isinstance(error_data["detail"], list)
        assert len(error_data["detail"]) > 0

        # Validation error structure
        error = error_data["detail"][0]
        assert "type" in error
        assert "loc" in error
        assert "msg" in error
        assert error["loc"] == ["body", "text"]
