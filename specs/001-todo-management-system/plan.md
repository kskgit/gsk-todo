# 実装計画: Todo管理システム

**Branch**: `001-todo-management-system` | **Date**: 2025-09-13 | **Spec**: [spec.md](spec.md)
**入力**: `/specs/001-todo-management-system/spec.md`からの機能仕様

## 実行フロー (/planコマンドの範囲)
```
1. 入力パスから機能仕様を読み込み ✓
   → 機能仕様の読み込み成功
2. 技術コンテキストを記入 (NEEDS CLARIFICATIONをスキャン) ✓
   → 検出されたプロジェクトタイプ: web (FastAPIバックエンドアプリケーション)
   → 構造決定を設定: オプション1 (単一プロジェクト)
3. 以下のConstitution Checkセクションを評価 ✓
   → 初期アプローチで違反なし
   → Progress Trackingを更新: 初期Constitution Check ✓
4. Phase 0を実行 → research.md ✓
   → FastAPI技術選択の研究タスクを生成
5. Phase 1を実行 → contracts, data-model.md, quickstart.md, CLAUDE.md ✓
6. Constitution Checkセクションを再評価 ✓
   → 設計はConstitution原則に従っている
   → Progress Trackingを更新: 設計後Constitution Check ✓
7. Phase 2を計画 → タスク生成アプローチを記述 ✓
8. 停止 - /tasksコマンドの準備完了 ✓
```

**重要**: /planコマンドはステップ7で停止します。フェーズ2-4は他のコマンドで実行されます:
- フェーズ2: /tasksコマンドがtasks.mdを作成
- フェーズ3-4: 実装実行 (手動またはツール経由)

## 概要
Todo管理システムの基本的なCRUD操作を提供するFastAPI Webアプリケーション。REST API経由でのTodo管理機能、SQLAlchemyによるインメモリデータベース、完全な型安全性（mypy）、コード品質管理（ruff）を含む現代的なPython Webサービス。

## 技術コンテキスト
**言語/バージョン**: Python 3.11+
**主要依存関係**: fastapi, sqlalchemy, uvicorn, pydantic
**ストレージ**: SQLite インメモリデータベース (sqlite:///:memory:)
**テスト**: pytest + httpx (FastAPI test client)
**対象プラットフォーム**: Web API (Linux server, Docker対応)
**プロジェクトタイプ**: web - FastAPI backend
**パフォーマンス目標**: 1000 req/s, <100ms レスポンス時間
**制約**: インメモリDB（再起動でデータ消失）、型安全性必須
**規模/範囲**: 単一ユーザー、REST API、基本的なCRUD操作
**コード品質**: ruff (linter/formatter), mypy (型チェック)

## Constitution Check
*ゲート: Phase 0研究前に通過必要。Phase 1設計後に再チェック。*

**シンプルさ**:
- プロジェクト数: 1 (FastAPI Web API)
- フレームワークを直接使用? はい (FastAPI, SQLAlchemy直接使用)
- 単一データモデル? はい (Todo Pydanticモデル + SQLAlchemyモデル)
- パターンを避ける? はい (直接SQLAlchemy使用、Repository pattern避ける)

**アーキテクチャ**:
- すべての機能をライブラリとして? はい (todo-lib)
- ライブラリ一覧: todo-lib (Todo CRUD操作、データベース管理)
- ライブラリ毎のAPI: REST API (/todos endpoint group)
- ライブラリドキュメント: llms.txt形式を計画? はい

**テスト (譲れない)**:
- RED-GREEN-Refactorサイクルを強制? はい
- Gitコミットで実装前にテストを表示? はい
- 順序: Contract→Integration→E2E→Unitを厳密に従う? はい
- 実際の依存関係を使用? はい (実際のSQLiteインメモリDB)
- 統合テスト対象: API endpoints, データベース操作, エラーレスポンス
- 禁止事項: テスト前の実装、REDフェーズのスキップ

**可観測性**:
- 構造化ログを含む? はい (uvicorn + Python logging)
- フロントエンドログ → バックエンド? N/A (API単体)
- エラーコンテキストは十分? はい (FastAPI exception handling)

**バージョン管理**:
- バージョン番号割り当て? 0.1.0
- 変更毎にBUILDを増分? はい
- 破壊的変更の処理? N/A (初期実装)

## プロジェクト構造

### ドキュメント (この機能)
```
specs/001-todo-management-system/
├── plan.md              # This file (/plan command output) ✓
├── research.md          # Phase 0 output (/plan command) ✓
├── data-model.md        # Phase 1 output (/plan command) ✓
├── quickstart.md        # Phase 1 output (/plan command) ✓
├── contracts/           # Phase 1 output (/plan command) ✓
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### ソースコード (リポジトリルート)
```
# FastAPI Web Application
src/
├── models/          # SQLAlchemy + Pydantic models
├── api/             # FastAPI router endpoints
├── services/        # ビジネスロジック層
├── database/        # DB設定・接続管理
└── main.py          # FastAPI application entry point

tests/
├── contract/        # API contract tests (OpenAPI schema)
├── integration/     # API endpoint integration tests
└── unit/            # 単体テスト

# 開発環境設定
pyproject.toml       # 依存関係、ruff、mypy設定
.ruff.toml          # ruff詳細設定（optional）
mypy.ini            # mypy設定
requirements.txt     # pip requirements
```

**構造決定**: 関心事の明確な分離を持つ単一FastAPIアプリケーション

## Phase 0: Outline & Research

研究タスクと決定事項をresearch.mdに統合：

1. **Python Web Framework選択**:
   - 決定: FastAPI
   - 理由: 高性能、自動型検証、OpenAPI生成、現代的なasync/await
   - 検討した代替案: Flask, Django, Starlette

2. **データベース戦略**:
   - 決定: SQLite インメモリデータベース + SQLAlchemy
   - 理由: 設定不要、高速、開発・テストに適している
   - 検討した代替案: PostgreSQL, MySQL, ファイル永続化

3. **API設計パターン**:
   - 決定: 標準的なHTTPメソッドを使用するREST API
   - 理由: 標準的、シンプル、FastAPIが得意とするパターン
   - 検討した代替案: GraphQL, RPCスタイル

**出力**: すべてのNEEDS CLARIFICATIONを解決したresearch.md ✓

## フェーズ1: 設計と契約

1. **データモデル** (data-model.md):
   - SQLAlchemyモデル: TodoDB（DB永続化用）
   - Pydanticモデル: TodoCreate, TodoUpdate, TodoResponse（API用）
   - バリデーション: 1-1000文字制限、必須フィールド

2. **API契約** (contracts/):
   - RESTエンドポイント: GET/POST /todos, GET/PUT/DELETE /todos/{id}
   - OpenAPIスキーマ仕様
   - エラーレスポンススキーマ (404, 422, など)

3. **契約テスト**:
   - APIエンドポイントスキーマ検証
   - リクエスト/レスポンス形式確認
   - エラーハンドリングテストケース

4. **CLAUDE.mdの更新**:
   - FastAPI/Pythonコンテキスト追加
   - Todo管理プロジェクト情報追加
   - 最新技術選択の記録

**出力**: data-model.md, /contracts/*, 失敗テスト, quickstart.md, CLAUDE.md ✓

## フェーズ2: タスク計画アプローチ
*このセクションは/tasksコマンドが何をするかを説明します - /plan中は実行しないでください*

**タスク生成戦略**:
- API優先でタスク生成
- TDD順序: テスト → 実装
- FastAPI特有のタスク（モデル定義、エンドポイント実装）

**順序戦略**:
1. データモデル定義テスト（SQLAlchemy + Pydantic） [P]
2. データベース接続・設定テスト [P]
3. API契約テスト（OpenAPIスキーマ）
4. 統合テスト（HTTPエンドポイントE2E）
5. 実装タスク（テストを通すため）

**推定出力**: 25-30のタスク、API開発重点

**重要**: このフェーズは/tasksコマンドで実行され、/planでは実行されません

## フェーズ3+: 今後の実装
*これらのフェーズは/planコマンドの範囲外です*

**フェーズ3**: タスク実行 (/tasksコマンドがtasks.mdを作成)
**フェーズ4**: 実装 (Constitution原則に従ってtasks.mdを実行)
**フェーズ5**: 検証 (テスト実行、quickstart.md実行、パフォーマンス検証)

## 複雑さ追跡
*Constitution Checkで違反がない場合は空*

| 違反 | 必要な理由 | より単純な代替案が却下された理由 |
|------|-----------|---------------------------|
| なし | なし | なし |

## 進捗追跡
*このチェックリストは実行フロー中に更新されます*

**フェーズ状況**:
- [x] フェーズ0: 研究完了 (/planコマンド) ✓
- [x] フェーズ1: 設計完了 (/planコマンド) ✓
- [x] フェーズ2: タスク計画完了 (/planコマンド - アプローチ記述のみ) ✓
- [ ] フェーズ3: タスク生成 (/tasksコマンド)
- [ ] フェーズ4: 実装完了
- [ ] フェーズ5: 検証合格

**ゲート状況**:
- [x] 初期Constitution Check: 合格 ✓
- [x] 設計後Constitution Check: 合格 ✓
- [x] すべてのNEEDS CLARIFICATION解決 ✓
- [x] 複雑さ逸脱の文書化 (なし) ✓

**生成された成果物**:
- [x] research.md - 技術選択とFastAPI/SQLAlchemy決定 ✓
- [x] data-model.md - Pydantic + SQLAlchemyモデル定義 ✓
- [x] contracts/openapi.yaml - REST API仕様 ✓
- [x] contracts/contract_tests.md - 契約テスト仕様 ✓
- [x] quickstart.md - 実装・動作確認ガイド ✓
- [x] CLAUDE.md - AI開発コンテキスト ✓

---
*Constitution v2.1.1に基づく - `/memory/constitution.md`を参照*