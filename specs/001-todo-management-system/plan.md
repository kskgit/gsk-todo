# Implementation Plan: Todo管理システム

**Branch**: `001-todo-management-system` | **Date**: 2025-09-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-todo-management-system/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path ✓
   → Feature spec loaded successfully
2. Fill Technical Context (scan for NEEDS CLARIFICATION) ✓
   → Detected Project Type: single (Rust CLI application)
   → Set Structure Decision: Option 1 (single project)
3. Evaluate Constitution Check section below ✓
   → No violations detected in initial approach
   → Update Progress Tracking: Initial Constitution Check ✓
4. Execute Phase 0 → research.md ✓
   → Research tasks generated for Rust storage options
5. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md ✓
6. Re-evaluate Constitution Check section ✓
   → Design follows constitutional principles
   → Update Progress Tracking: Post-Design Constitution Check ✓
7. Plan Phase 2 → Task generation approach described ✓
8. STOP - Ready for /tasks command ✓
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Todo管理システムの基本的なCRUD操作を提供するFastAPI Webアプリケーション。REST API経由でのTodo管理機能、SQLAlchemyによるインメモリデータベース、完全な型安全性（mypy）、コード品質管理（ruff）を含む現代的なPython Webサービス。

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: fastapi, sqlalchemy, uvicorn, pydantic  
**Storage**: SQLite インメモリデータベース (sqlite:///:memory:)  
**Testing**: pytest + httpx (FastAPI test client)  
**Target Platform**: Web API (Linux server, Docker対応)
**Project Type**: web - FastAPI backend  
**Performance Goals**: 1000 req/s, <100ms レスポンス時間  
**Constraints**: インメモリDB（再起動でデータ消失）、型安全性必須  
**Scale/Scope**: 単一ユーザー、REST API、基本的なCRUD操作
**Code Quality**: ruff (linter/formatter), mypy (型チェック)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (FastAPI Web API)
- Using framework directly? Yes (FastAPI, SQLAlchemy直接使用)
- Single data model? Yes (Todo Pydanticモデル + SQLAlchemyモデル)
- Avoiding patterns? Yes (直接SQLAlchemy使用、Repository pattern避ける)

**Architecture**:
- EVERY feature as library? Yes (todo-lib)
- Libraries listed: todo-lib (Todo CRUD操作、データベース管理)
- API per library: REST API (/todos endpoint group)
- Library docs: llms.txt format planned? Yes

**Testing (NON-NEGOTIABLE)**:
- RED-GREEN-Refactor cycle enforced? Yes
- Git commits show tests before implementation? Yes
- Order: Contract→Integration→E2E→Unit strictly followed? Yes
- Real dependencies used? Yes (実際のSQLiteインメモリDB)
- Integration tests for: API endpoints, データベース操作, エラーレスポンス
- FORBIDDEN: Implementation before test, skipping RED phase

**Observability**:
- Structured logging included? Yes (uvicorn + Python logging)
- Frontend logs → backend? N/A (API単体)
- Error context sufficient? Yes (FastAPI exception handling)

**Versioning**:
- Version number assigned? 0.1.0
- BUILD increments on every change? Yes
- Breaking changes handled? N/A (初期実装)

## Project Structure

### Documentation (this feature)
```
specs/001-todo-management-system/
├── plan.md              # This file (/plan command output) ✓
├── research.md          # Phase 0 output (/plan command) ✓
├── data-model.md        # Phase 1 output (/plan command) ✓
├── quickstart.md        # Phase 1 output (/plan command) ✓
├── contracts/           # Phase 1 output (/plan command) ✓
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
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

**Structure Decision**: Single FastAPI application with clear separation of concerns

## Phase 0: Outline & Research

研究タスクと決定事項をresearch.mdに統合：

1. **Rust永続化オプション**:
   - Decision: serde_json + std::fs
   - Rationale: シンプル、依存関係最小、人間可読
   - Alternatives considered: bincode, SQLite, toml

2. **ファイルロック戦略**:  
   - Decision: Advisory locking with fs2 crate
   - Rationale: クロスプラットフォーム、競合状態防止
   - Alternatives considered: 原子的書き込み、PID files

3. **エラーハンドリング**:
   - Decision: anyhow (main) + thiserror (library errors)
   - Rationale: 標準的なRustエラーハンドリング、豊富なコンテキスト
   - Alternatives considered: std::error単体、eyre

**Output**: research.md with all NEEDS CLARIFICATION resolved ✓

## Phase 1: Design & Contracts

1. **データモデル** (data-model.md):
   ```rust
   #[derive(Serialize, Deserialize, Debug, Clone)]
   pub struct Todo {
       pub id: u64,
       pub text: String,
       pub completed: bool,
       pub created_at: DateTime<Utc>,
       pub updated_at: DateTime<Utc>,
   }
   ```

2. **API contracts** (contracts/):
   - CLI commands: create, list, complete, delete
   - JSON output format specification
   - Error response schemas

3. **契約テスト**: 
   - CLI実行結果の検証
   - JSONスキーマ検証
   - エラーケースの検証

4. **CLAUDE.mdの更新**:
   - Rust/cargo context追加
   - Todo管理プロジェクト情報追加
   - 最新技術選択の記録

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, CLAUDE.md ✓

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- 保存処理優先でタスク生成
- TDD順序: テスト → 実装
- Rust特有のタスク（型定義、トレイト実装）

**Ordering Strategy**:
1. Todo構造体定義とシリアライゼーションテスト [P]
2. ファイル保存・読み込み機能テスト [P] 
3. CLIコマンド契約テスト
4. 統合テスト（E2E）
5. 実装タスク（テストを通すため）

**Estimated Output**: 20-25のタスク、保存処理重点

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Constitution Checkで違反がない場合は空*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| なし | なし | なし |

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) ✓
- [x] Phase 1: Design complete (/plan command) ✓
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✓
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✓
- [x] Post-Design Constitution Check: PASS ✓
- [x] All NEEDS CLARIFICATION resolved ✓
- [x] Complexity deviations documented (なし) ✓

**Generated Artifacts**:
- [x] research.md - 技術選択とFastAPI/SQLAlchemy決定 ✓
- [x] data-model.md - Pydantic + SQLAlchemyモデル定義 ✓
- [x] contracts/openapi.yaml - REST API仕様 ✓
- [x] contracts/contract_tests.md - 契約テスト仕様 ✓
- [x] quickstart.md - 実装・動作確認ガイド ✓
- [x] CLAUDE.md - AI開発コンテキスト ✓

---
*Based on Constitution v2.1.1 - See `/memory/constitution.md`*