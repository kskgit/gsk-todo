# Phase 0: Research & Technology Decisions

## FastAPI Framework選択

**Decision**: FastAPI
**Rationale**: 
- 高性能な非同期Webフレームワーク
- 自動OpenAPI/Swagger生成
- Pydantic統合による型安全性
- 現代的なPython開発標準

**Alternatives considered**:
- Django REST Framework: 機能豊富だが複雑、今回の要件には過剰
- Flask: シンプルだが型安全性・自動ドキュメント生成なし
- Starlette: FastAPIのベースだが高レベル機能不足

## データベース＆ORM選択

**Decision**: SQLAlchemy + SQLite インメモリDB
**Rationale**:
- SQLAlchemy: Python標準的なORM、型安全性
- インメモリDB: 開発・テスト簡便性、要件適合
- SQLite: 軽量、外部依存なし

**Alternatives considered**:
- PostgreSQL: 高機能だが今回は過剰、セットアップ複雑
- async SQLAlchemy: 高性能だが複雑性増加
- 単純辞書: 永続化なし、リレーション管理困難

## コード品質ツール

**Decision**: ruff (linter/formatter) + mypy (型チェック)
**Rationale**:
- ruff: 高速、多機能（black, flake8, isort統合）
- mypy: Python標準的型チェッカー
- 現代的なPython開発エコシステム

**Alternatives considered**:
- black + flake8 + isort: 複数ツールで設定複雑
- pylint: 機能豊富だが重い、設定複雑
- bandit: セキュリティ重視、今回の要件外

## テスト戦略

**Decision**: pytest + httpx (FastAPI test client)
**Rationale**:
- pytest: Python標準的テストフレームワーク
- httpx: FastAPI推奨、非同期対応
- TestClient: FastAPI統合テスト機能

**Alternatives considered**:
- unittest: 標準ライブラリだが機能不足
- requests: 同期のみ、FastAPI統合なし
- aiohttp: 別フレームワーク用

## バリデーション＆シリアライゼーション

**Decision**: Pydantic v2
**Rationale**:
- FastAPI標準、自動統合
- 型安全性・バリデーション
- 高性能（Rust実装）
- OpenAPI schema自動生成

**Alternatives considered**:
- marshmallow: 機能豊富だがFastAPI統合劣る
- dataclasses: バリデーション機能不足
- attrs: 軽量だがWebアプリ向け機能不足

## API設計パターン

**Decision**: RESTful API
**Rationale**:
- 標準的、理解しやすい
- FastAPIの強みを活用
- OpenAPIドキュメント自動生成

**API Endpoints**:
```
GET    /todos          # Todo一覧取得
POST   /todos          # Todo作成
GET    /todos/{id}     # 特定Todo取得
PUT    /todos/{id}     # Todo更新
DELETE /todos/{id}     # Todo削除
```

**Alternatives considered**:
- GraphQL: 複雑性増加、今回は不要
- RPC style: REST標準から逸脱
- 単一endpoint: RESTful原則に反する

## エラーハンドリング

**Decision**: FastAPI HTTPException + カスタム例外
**Rationale**:
- FastAPI標準パターン
- 適切なHTTPステータスコード
- JSONエラーレスポンス

```python
from fastapi import HTTPException

class TodoNotFound(HTTPException):
    def __init__(self, todo_id: int):
        super().__init__(status_code=404, detail=f"Todo {todo_id} not found")
```

## 開発環境設定

**Decision**: pyproject.toml中心の設定管理
**Rationale**:
- PEP 518準拠
- 単一設定ファイル
- 現代的Pythonプロジェクト標準

### pyproject.toml 主要設定:
```toml
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
]

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

## パフォーマンス考慮事項

**Target Metrics**:
- 1000 req/s (単純CRUD)
- <100ms レスポンス時間（95パーセンタイル）
- メモリ使用量: <200MB

**最適化戦略**:
1. 非同期処理（FastAPI標準）
2. インメモリDB（I/Oオーバーヘッドなし）
3. Pydantic最適化（exclude_unset等）

## セキュリティ考慮事項

**Current Scope** (認証なし):
- 入力バリデーション（Pydantic）
- SQLインジェクション防止（SQLAlchemy）
- CORS設定（開発時のみ）

**Future Extensions** (スコープ外):
- JWT認証
- レート制限
- HTTPS

## 依存関係最終決定

```toml
[project]
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
    "types-requests",  # mypy用型定義
]
```

## 全NEEDS CLARIFICATION解決済み

✅ Language/Version: Python 3.11+
✅ Primary Dependencies: fastapi, sqlalchemy, uvicorn, pydantic
✅ Storage: SQLite インメモリデータベース (sqlite:///:memory:)
✅ Testing: pytest + httpx (FastAPI test client)
✅ Target Platform: Web API (Linux server, Docker対応)
✅ Performance Goals: 1000 req/s, <100ms レスポンス時間
✅ Constraints: インメモリDB、型安全性必須
✅ Scale/Scope: 単一ユーザー、REST API、基本的なCRUD操作
✅ Code Quality: ruff (linter/formatter), mypy (型チェック)