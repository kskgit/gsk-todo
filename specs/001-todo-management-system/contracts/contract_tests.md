# API Contract Tests Specification

## Overview

このドキュメントは、Todo管理APIの契約テストの仕様を定義します。すべてのテストは実装前に作成され、テスト駆動開発（TDD）のRED-GREEN-Refactorサイクルに従います。

## Test Framework Setup

```python
import pytest
from fastapi.testclient import TestClient
from httpx import Response
from typing import Dict, Any
import json

from src.main import app
from src.database import get_db, engine, Base

@pytest.fixture(scope="function")
def test_client():
    """各テストで独立したテストクライアントを提供"""
    # インメモリDBテーブル作成
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as client:
        yield client
    
    # テーブルクリーンアップ
    Base.metadata.drop_all(bind=engine)
```

## Contract Test Cases

### 1. POST /todos - Todo作成

#### TC-001: 正常なTodo作成
```python
def test_create_todo_success(test_client: TestClient):
    """正常なTodo作成のコントラクトテスト"""
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
    from datetime import datetime
    datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
    datetime.fromisoformat(data["updated_at"].replace('Z', '+00:00'))
```

#### TC-002: バリデーションエラー - 空テキスト
```python
def test_create_todo_empty_text_validation_error(test_client: TestClient):
    """空テキストでのバリデーションエラー"""
    # Given
    request_data = {"text": "", "completed": False}
    
    # When
    response = test_client.post("/todos", json=request_data)
    
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
```

#### TC-003: バリデーションエラー - テキスト長制限
```python
def test_create_todo_text_too_long_validation_error(test_client: TestClient):
    """1000文字超過でのバリデーションエラー"""
    # Given
    long_text = "a" * 1001
    request_data = {"text": long_text, "completed": False}
    
    # When
    response = test_client.post("/todos", json=request_data)
    
    # Then
    assert response.status_code == 422
    error_data = response.json()
    assert "detail" in error_data
    
    error = error_data["detail"][0]
    assert error["loc"] == ["body", "text"]
    assert "1000" in error["msg"]  # Max length mentioned in error
```

#### TC-004: 必須フィールド不足
```python
def test_create_todo_missing_required_field(test_client: TestClient):
    """必須フィールド（text）不足エラー"""
    # Given
    request_data = {"completed": False}  # text field missing
    
    # When
    response = test_client.post("/todos", json=request_data)
    
    # Then
    assert response.status_code == 422
    error_data = response.json()
    
    error = error_data["detail"][0]
    assert error["loc"] == ["body", "text"]
    assert "required" in error["type"] or "missing" in error["msg"]
```

### 2. GET /todos - Todo一覧取得

#### TC-005: 空リストの正常取得
```python
def test_get_todos_empty_list_success(test_client: TestClient):
    """空のTodo一覧取得"""
    # When
    response = test_client.get("/todos")
    
    # Then
    assert response.status_code == 200
    data = response.json()
    
    # Response schema validation
    assert "todos" in data
    assert "total" in data
    assert isinstance(data["todos"], list)
    assert isinstance(data["total"], int)
    assert len(data["todos"]) == 0
    assert data["total"] == 0
```

#### TC-006: Todo項目ありの一覧取得
```python
def test_get_todos_with_items_success(test_client: TestClient):
    """Todo項目がある場合の一覧取得"""
    # Given - Create test todos
    todo1_data = {"text": "最初のTodo", "completed": False}
    todo2_data = {"text": "二番目のTodo", "completed": True}
    
    response1 = test_client.post("/todos", json=todo1_data)
    response2 = test_client.post("/todos", json=todo2_data)
    assert response1.status_code == 201
    assert response2.status_code == 201
    
    # When
    response = test_client.get("/todos")
    
    # Then
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 2
    assert len(data["todos"]) == 2
    
    # Validate todo item structure
    for todo in data["todos"]:
        assert "id" in todo
        assert "text" in todo
        assert "completed" in todo
        assert "created_at" in todo
        assert "updated_at" in todo
        assert isinstance(todo["id"], int)
        assert isinstance(todo["text"], str)
        assert isinstance(todo["completed"], bool)
```

#### TC-007: ページネーション機能
```python
def test_get_todos_pagination(test_client: TestClient):
    """ページネーション機能のテスト"""
    # Given - Create 3 todos
    for i in range(3):
        todo_data = {"text": f"Todo {i+1}", "completed": False}
        response = test_client.post("/todos", json=todo_data)
        assert response.status_code == 201
    
    # When - Get first 2 todos
    response = test_client.get("/todos?skip=0&limit=2")
    
    # Then
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 3  # Total count unchanged
    assert len(data["todos"]) == 2  # Limited to 2 items
    
    # When - Get remaining todos
    response = test_client.get("/todos?skip=2&limit=2")
    
    # Then
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 3
    assert len(data["todos"]) == 1  # Only 1 remaining
```

### 3. GET /todos/{todo_id} - 特定Todo取得

#### TC-008: 存在するTodoの正常取得
```python
def test_get_todo_by_id_success(test_client: TestClient):
    """存在するTodoの正常取得"""
    # Given - Create a todo
    create_data = {"text": "取得テスト用Todo", "completed": False}
    create_response = test_client.post("/todos", json=create_data)
    assert create_response.status_code == 201
    created_todo = create_response.json()
    todo_id = created_todo["id"]
    
    # When
    response = test_client.get(f"/todos/{todo_id}")
    
    # Then
    assert response.status_code == 200
    data = response.json()
    
    # Validate response matches created todo
    assert data["id"] == todo_id
    assert data["text"] == "取得テスト用Todo"
    assert data["completed"] == False
    assert data["created_at"] == created_todo["created_at"]
    assert data["updated_at"] == created_todo["updated_at"]
```

#### TC-009: 存在しないTodoの404エラー
```python
def test_get_todo_by_id_not_found(test_client: TestClient):
    """存在しないTodoでの404エラー"""
    # Given
    non_existent_id = 999
    
    # When
    response = test_client.get(f"/todos/{non_existent_id}")
    
    # Then
    assert response.status_code == 404
    error_data = response.json()
    
    assert "detail" in error_data
    assert str(non_existent_id) in error_data["detail"]
```

### 4. PUT /todos/{todo_id} - Todo更新

#### TC-010: 全フィールド更新成功
```python
def test_update_todo_full_success(test_client: TestClient):
    """全フィールド更新の成功テスト"""
    # Given - Create a todo
    create_data = {"text": "更新前Todo", "completed": False}
    create_response = test_client.post("/todos", json=create_data)
    todo_id = create_response.json()["id"]
    
    # When
    update_data = {"text": "更新後Todo", "completed": True}
    response = test_client.put(f"/todos/{todo_id}", json=update_data)
    
    # Then
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == todo_id
    assert data["text"] == "更新後Todo"
    assert data["completed"] == True
    # updated_at should be newer than created_at
    assert data["updated_at"] >= data["created_at"]
```

#### TC-011: 部分更新成功（completedのみ）
```python
def test_update_todo_partial_completed_only(test_client: TestClient):
    """部分更新（completedのみ）の成功テスト"""
    # Given
    create_data = {"text": "部分更新テスト", "completed": False}
    create_response = test_client.post("/todos", json=create_data)
    todo_id = create_response.json()["id"]
    original_text = create_response.json()["text"]
    
    # When - Update only completed field
    update_data = {"completed": True}
    response = test_client.put(f"/todos/{todo_id}", json=update_data)
    
    # Then
    assert response.status_code == 200
    data = response.json()
    
    assert data["completed"] == True
    assert data["text"] == original_text  # Text unchanged
```

#### TC-012: 存在しないTodo更新で404エラー
```python
def test_update_todo_not_found(test_client: TestClient):
    """存在しないTodo更新での404エラー"""
    # Given
    non_existent_id = 999
    update_data = {"text": "更新データ", "completed": True}
    
    # When
    response = test_client.put(f"/todos/{non_existent_id}", json=update_data)
    
    # Then
    assert response.status_code == 404
    error_data = response.json()
    assert str(non_existent_id) in error_data["detail"]
```

### 5. DELETE /todos/{todo_id} - Todo削除

#### TC-013: 存在するTodoの正常削除
```python
def test_delete_todo_success(test_client: TestClient):
    """存在するTodoの正常削除"""
    # Given
    create_data = {"text": "削除テスト用Todo", "completed": False}
    create_response = test_client.post("/todos", json=create_data)
    todo_id = create_response.json()["id"]
    
    # When
    response = test_client.delete(f"/todos/{todo_id}")
    
    # Then
    assert response.status_code == 204
    assert response.text == ""  # No response body
    
    # Verify todo is actually deleted
    get_response = test_client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404
```

#### TC-014: 存在しないTodo削除で404エラー
```python
def test_delete_todo_not_found(test_client: TestClient):
    """存在しないTodo削除での404エラー"""
    # Given
    non_existent_id = 999
    
    # When
    response = test_client.delete(f"/todos/{non_existent_id}")
    
    # Then
    assert response.status_code == 404
    error_data = response.json()
    assert str(non_existent_id) in error_data["detail"]
```

### 6. GET /health - ヘルスチェック

#### TC-015: ヘルスチェック正常レスポンス
```python
def test_health_check_success(test_client: TestClient):
    """ヘルスチェック正常レスポンス"""
    # When
    response = test_client.get("/health")
    
    # Then
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert data["status"] == "healthy"
    assert "timestamp" in data
    # Validate timestamp format
    from datetime import datetime
    datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
```

## Test Execution Strategy

### Red Phase (テスト失敗)
1. 全契約テストを実装
2. テスト実行で期待される失敗を確認
3. 失敗原因が正しい（実装未完了）ことを確認

### Green Phase (最小実装)
1. テストを通すための最小実装を作成
2. 全テストがパスすることを確認
3. 過剰実装を避け、テスト要件のみ満たす

### Refactor Phase (リファクタリング)
1. コードの重複除去
2. 可読性向上
3. パフォーマンス最適化
4. テストが継続してパスすることを確認

## Contract Validation Tools

### OpenAPI Schema Validation
```python
def test_openapi_schema_generation():
    """生成されたOpenAPIスキーマが仕様と一致することを確認"""
    from src.main import app
    
    openapi_schema = app.openapi()
    
    # Validate basic structure
    assert "openapi" in openapi_schema
    assert "info" in openapi_schema
    assert "paths" in openapi_schema
    
    # Validate endpoints exist
    paths = openapi_schema["paths"]
    assert "/todos" in paths
    assert "/todos/{todo_id}" in paths
    assert "/health" in paths
    
    # Validate HTTP methods
    assert "get" in paths["/todos"]
    assert "post" in paths["/todos"]
    assert "get" in paths["/todos/{todo_id}"]
    assert "put" in paths["/todos/{todo_id}"]
    assert "delete" in paths["/todos/{todo_id}"]
```

## Performance Contract Tests

### Response Time Contracts
```python
import time

def test_response_time_contract(test_client: TestClient):
    """レスポンス時間の契約テスト（100ms以内）"""
    # Given
    create_data = {"text": "パフォーマンステスト", "completed": False}
    
    # When
    start_time = time.time()
    response = test_client.post("/todos", json=create_data)
    end_time = time.time()
    
    # Then
    assert response.status_code == 201
    response_time = (end_time - start_time) * 1000  # Convert to ms
    assert response_time < 100, f"Response time {response_time}ms exceeds 100ms limit"
```

## Error Handling Contracts

### HTTP Status Code Contracts
```python
def test_http_status_codes_contract(test_client: TestClient):
    """HTTPステータスコードの契約確認"""
    # 201 Created
    response = test_client.post("/todos", json={"text": "test", "completed": False})
    assert response.status_code == 201
    
    # 200 OK
    response = test_client.get("/todos")
    assert response.status_code == 200
    
    # 404 Not Found
    response = test_client.get("/todos/999")
    assert response.status_code == 404
    
    # 422 Validation Error
    response = test_client.post("/todos", json={"text": ""})
    assert response.status_code == 422
```

## Test Data Management

### Test Isolation
各テストは独立して実行可能であり、他のテストの状態に依存しません。

### Clean State
各テスト前にデータベースを初期化し、テスト後にクリーンアップします。

### Deterministic Results
テスト結果は実行順序や環境に依存せず、常に同じ結果となります。

## Coverage Requirements

すべての契約テストは以下をカバーします：
- 正常系パス（Happy Path）
- エラー処理（Error Cases）
- バリデーション（Input Validation）
- レスポンス形式（Response Format）
- HTTPステータスコード（Status Codes）
- パフォーマンス要件（Performance Requirements）