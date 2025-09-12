# Quickstart Guide: Todo管理システム

## 概要

このガイドでは、Todo管理システムのFastAPI実装を素早く立ち上げて動作確認する手順を説明します。

## 前提条件

- Python 3.11 以上
- pip または uv (推奨)

## セットアップ手順

### 1. 依存関係のインストール

```bash
# pyproject.toml を作成
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "gsk-todo"
version = "0.1.0"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "httpx>=0.25.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
    "types-requests",
]

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]
ignore = []

[tool.ruff.format]
quote-style = "double"
indent-style = "space"

[tool.mypy]
python_version = "3.11"
strict = true
ignore_missing_imports = true
EOF

# 依存関係インストール
pip install -e ".[dev]"
# または uv を使用する場合
# uv pip install -e ".[dev]"
```

### 2. プロジェクト構造の作成

```bash
mkdir -p src/{models,api,services,database}
mkdir -p tests/{contract,integration,unit}

# __init__.py files
touch src/__init__.py
touch src/models/__init__.py
touch src/api/__init__.py
touch src/services/__init__.py
touch src/database/__init__.py
```

### 3. 基本ファイルの作成

#### データベース設定 (`src/database/config.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### モデル定義 (`src/models/todo.py`)
```python
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from pydantic import BaseModel, Field, ConfigDict

from src.database.config import Base

# SQLAlchemy Model
class TodoDB(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(String(1000), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# Pydantic Models
class TodoBase(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    completed: bool = Field(default=False)

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    text: Optional[str] = Field(None, min_length=1, max_length=1000)
    completed: Optional[bool] = None

class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TodoListResponse(BaseModel):
    todos: list[TodoResponse]
    total: int
```

#### サービス層 (`src/services/todo_service.py`)
```python
from typing import Optional
from sqlalchemy.orm import Session
from src.models.todo import TodoDB, TodoCreate, TodoUpdate, TodoResponse, TodoListResponse

class TodoService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_todo(self, todo_data: TodoCreate) -> TodoResponse:
        db_todo = TodoDB(**todo_data.model_dump())
        self.db.add(db_todo)
        self.db.commit()
        self.db.refresh(db_todo)
        return TodoResponse.model_validate(db_todo)
    
    def get_todo(self, todo_id: int) -> Optional[TodoResponse]:
        db_todo = self.db.query(TodoDB).filter(TodoDB.id == todo_id).first()
        if db_todo:
            return TodoResponse.model_validate(db_todo)
        return None
    
    def get_todos(self, skip: int = 0, limit: int = 100) -> TodoListResponse:
        todos = self.db.query(TodoDB).offset(skip).limit(limit).all()
        total = self.db.query(TodoDB).count()
        return TodoListResponse(
            todos=[TodoResponse.model_validate(todo) for todo in todos],
            total=total
        )
    
    def update_todo(self, todo_id: int, todo_update: TodoUpdate) -> Optional[TodoResponse]:
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
        db_todo = self.db.query(TodoDB).filter(TodoDB.id == todo_id).first()
        if not db_todo:
            return False
        
        self.db.delete(db_todo)
        self.db.commit()
        return True
```

#### API エンドポイント (`src/api/todos.py`)
```python
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from src.database.config import get_db
from src.services.todo_service import TodoService
from src.models.todo import TodoCreate, TodoUpdate, TodoResponse, TodoListResponse

router = APIRouter(prefix="/todos", tags=["todos"])

@router.get("/", response_model=TodoListResponse)
def get_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    service = TodoService(db)
    return service.get_todos(skip, limit)

@router.post("/", response_model=TodoResponse, status_code=201)
def create_todo(todo_data: TodoCreate, db: Session = Depends(get_db)):
    service = TodoService(db)
    return service.create_todo(todo_data)

@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    service = TodoService(db)
    todo = service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo

@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    service = TodoService(db)
    todo = service.update_todo(todo_id, todo_update)
    if not todo:
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
    return todo

@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    service = TodoService(db)
    if not service.delete_todo(todo_id):
        raise HTTPException(status_code=404, detail=f"Todo with id {todo_id} not found")
```

#### メインアプリケーション (`src/main.py`)
```python
from datetime import datetime
from fastapi import FastAPI
from src.api.todos import router as todos_router
from src.database.config import create_tables

app = FastAPI(
    title="Todo Management API",
    description="基本的なTodo管理機能を提供するREST API",
    version="0.1.0"
)

# データベーステーブル作成
create_tables()

# ルーター登録
app.include_router(todos_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 動作確認

### 1. サーバー起動

```bash
# 開発サーバー起動
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# または直接実行
python -m src.main
```

サーバーが起動すると、以下のメッセージが表示されます：
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. API ドキュメント確認

ブラウザで以下のURLにアクセス：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 3. ヘルスチェック

```bash
curl http://localhost:8000/health
```

期待される出力：
```json
{
  "status": "healthy",
  "timestamp": "2025-09-13T12:00:00.000000"
}
```

### 4. 基本的なTodo操作

#### Todo作成
```bash
curl -X POST "http://localhost:8000/todos/" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "最初のTodo",
    "completed": false
  }'
```

期待される出力：
```json
{
  "id": 1,
  "text": "最初のTodo",
  "completed": false,
  "created_at": "2025-09-13T12:00:00.000000",
  "updated_at": "2025-09-13T12:00:00.000000"
}
```

#### Todo一覧取得
```bash
curl http://localhost:8000/todos/
```

期待される出力：
```json
{
  "todos": [
    {
      "id": 1,
      "text": "最初のTodo",
      "completed": false,
      "created_at": "2025-09-13T12:00:00.000000",
      "updated_at": "2025-09-13T12:00:00.000000"
    }
  ],
  "total": 1
}
```

#### 特定Todo取得
```bash
curl http://localhost:8000/todos/1
```

#### Todo更新
```bash
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{
    "completed": true
  }'
```

#### Todo削除
```bash
curl -X DELETE http://localhost:8000/todos/1
```

## テスト実行

### 1. テストファイル作成 (`tests/test_quickstart.py`)
```python
import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.database.config import Base, engine

@pytest.fixture(scope="function")
def test_client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as client:
        yield client
    Base.metadata.drop_all(bind=engine)

def test_health_check(test_client):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_create_and_get_todo(test_client):
    # Create todo
    response = test_client.post("/todos/", json={
        "text": "テストTodo",
        "completed": False
    })
    assert response.status_code == 201
    created_todo = response.json()
    assert created_todo["text"] == "テストTodo"
    
    # Get todo
    todo_id = created_todo["id"]
    response = test_client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["text"] == "テストTodo"

def test_todo_list(test_client):
    # Initially empty
    response = test_client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert len(data["todos"]) == 0
    
    # Create todo
    test_client.post("/todos/", json={"text": "リストテスト", "completed": False})
    
    # Check list
    response = test_client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["todos"]) == 1
    assert data["todos"][0]["text"] == "リストテスト"
```

### 2. テスト実行
```bash
pytest tests/test_quickstart.py -v
```

期待される出力：
```
tests/test_quickstart.py::test_health_check PASSED
tests/test_quickstart.py::test_create_and_get_todo PASSED  
tests/test_quickstart.py::test_todo_list PASSED

======================== 3 passed in 0.15s ========================
```

## コード品質チェック

### 1. Lint & Format (ruff)
```bash
# コードフォーマット
ruff format src/ tests/

# Lint実行
ruff check src/ tests/

# Lint自動修正
ruff check --fix src/ tests/
```

### 2. 型チェック (mypy)
```bash
mypy src/
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. ImportError: No module named 'src'
```bash
# Pythonパスに現在のディレクトリを追加
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# または pip install -e . で開発モードインストール
pip install -e .
```

#### 2. SQLAlchemy関連エラー
```bash
# 依存関係の再インストール
pip install --upgrade sqlalchemy fastapi
```

#### 3. ポート8000が使用済み
```bash
# 別のポートを使用
uvicorn src.main:app --port 8001

# または使用中のプロセスを確認
lsof -i :8000
```

## 次のステップ

1. **認証機能追加**: JWT認証の実装
2. **永続化改善**: SQLiteファイル永続化またはPostgreSQL対応
3. **フロントエンド**: React/Vue.jsでUI作成
4. **Docker化**: コンテナ環境での実行
5. **CI/CD**: GitHub Actionsでの自動テスト・デプロイ

## 開発リソース

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **SQLAlchemy Documentation**: https://docs.sqlalchemy.org/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **Ruff Documentation**: https://docs.astral.sh/ruff/
- **MyPy Documentation**: https://mypy.readthedocs.io/