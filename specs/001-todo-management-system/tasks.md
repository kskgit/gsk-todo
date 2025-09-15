# Tasks: Todo管理システム - FR-001 Todo作成機能

**Input**: Design documents from `/specs/001-todo-management-system/`
**Prerequisites**: plan.md (FastAPI + SQLAlchemy), data-model.md, contracts/, research.md, quickstart.md
**Focus**: FR-001 - システムはユーザーが新しいtodoアイテムを作成できるようにする必要がある

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Tech stack: FastAPI + SQLAlchemy + SQLite in-memory
   → Structure: Single project (src/, tests/)
2. Load design documents ✓
   → data-model.md: TodoDB, TodoCreate, TodoResponse models
   → contracts/openapi.yaml: POST /todos endpoint specification
   → contracts/contract_tests.md: TC-001, TC-002, TC-003, TC-004 test cases
3. Generate tasks by category ✓
   → Setup: project structure, dependencies, tooling
   → Tests: contract tests for POST /todos (TDD required)
   → Core: TodoDB model, TodoService.create_todo, POST endpoint
   → Integration: database setup, error handling
   → Polish: validation, performance, documentation
4. Apply task rules ✓
   → [P] = parallel execution (different files)
   → Tests before implementation (TDD enforced)
   → Dependencies: Setup → Tests → Models → Services → Endpoints
5. Numbered tasks T001-T020 ✓
6. Focus on FR-001: Todo creation functionality only
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- FR-001 specific: POST /todos endpoint and supporting infrastructure

## Phase 3.1: Setup (プロジェクト初期化)
- [ ] T001 Create project structure: src/{models,api,services,database}, tests/{contract,integration,unit}
- [ ] T002 Initialize pyproject.toml with FastAPI dependencies (fastapi>=0.104.0, sqlalchemy>=2.0.0, uvicorn, pydantic>=2.5.0)
- [ ] T003 [P] Configure development tools: ruff (linter/formatter), mypy (type checker) in pyproject.toml

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Contract test POST /todos success (TC-001) in tests/contract/test_create_todo_success.py
- [ ] T005 [P] Contract test POST /todos empty text validation (TC-002) in tests/contract/test_create_todo_validation.py
- [ ] T006 [P] Contract test POST /todos text too long validation (TC-003) in tests/contract/test_create_todo_length.py
- [ ] T007 [P] Contract test POST /todos missing field validation (TC-004) in tests/contract/test_create_todo_required.py
- [ ] T008 [P] Integration test Todo creation workflow in tests/integration/test_todo_creation_flow.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T009 [P] Database configuration in src/database/config.py (SQLite in-memory, SQLAlchemy setup)
- [ ] T010 [P] TodoDB SQLAlchemy model in src/models/todo.py (id, text, completed, timestamps)
- [ ] T011 [P] TodoCreate, TodoResponse Pydantic models in src/models/todo.py
- [ ] T012 TodoService.create_todo method in src/services/todo_service.py (depends on T010, T011)
- [ ] T013 POST /todos FastAPI endpoint in src/api/todos.py (depends on T012)
- [ ] T014 Main FastAPI application setup in src/main.py (depends on T009, T013)

## Phase 3.4: Integration (統合・エラーハンドリング)
- [ ] T015 Database table creation and session management (depends on T009, T010)
- [ ] T016 Input validation and error handling for POST /todos (422 Unprocessable Entity)
- [ ] T017 Database error handling (500 Internal Server Error)
- [ ] T018 Request/response logging for debugging

## Phase 3.5: Polish (品質向上)
- [ ] T019 [P] Unit tests for TodoService.create_todo in tests/unit/test_todo_service.py
- [ ] T020 [P] Performance validation: POST /todos response time <100ms (per requirements)

## Dependencies
```
Setup phase (T001-T003) → Tests phase (T004-T008) → Core phase (T009-T014) → Integration phase (T015-T018) → Polish phase (T019-T020)

Specific dependencies:
- T004-T008 must complete and FAIL before T009-T014
- T009 (database) blocks T010 (models), T015 (tables)
- T010, T011 (models) block T012 (service)
- T012 (service) blocks T013 (endpoint)
- T009, T013 block T014 (main app)
- T014 blocks T015-T018 (integration)
```

## Parallel Execution Examples

### Phase 3.2: Contract Tests (Run in parallel)
```bash
# All contract tests can run simultaneously (different files)
Task: "Contract test POST /todos success (TC-001) in tests/contract/test_create_todo_success.py"
Task: "Contract test POST /todos validation errors in tests/contract/test_create_todo_validation.py"
Task: "Contract test POST /todos text length in tests/contract/test_create_todo_length.py"
Task: "Contract test POST /todos required fields in tests/contract/test_create_todo_required.py"
Task: "Integration test Todo creation workflow in tests/integration/test_todo_creation_flow.py"
```

### Phase 3.3: Initial Models (Run in parallel)
```bash
# Database config and models can be created simultaneously
Task: "Database configuration in src/database/config.py"
Task: "TodoDB SQLAlchemy model in src/models/todo.py"
Task: "TodoCreate, TodoResponse Pydantic models in src/models/todo.py"  # Note: same file as TodoDB, so sequential within file
```

## FR-001 Specific Requirements

### POST /todos Endpoint Specification
- **URL**: POST /todos
- **Request**: TodoCreate (text: str, completed: bool = False)
- **Response**: 201 Created with TodoResponse (id, text, completed, created_at, updated_at)
- **Validation**:
  - text: 1-1000 characters, required
  - completed: boolean, default false
- **Error Cases**:
  - 422: Validation errors (empty text, text too long, missing fields)
  - 500: Database errors

### Test Coverage Requirements
- TC-001: Normal Todo creation with valid data
- TC-002: Validation error for empty text
- TC-003: Validation error for text > 1000 characters
- TC-004: Validation error for missing required field
- Integration test: End-to-end Todo creation workflow

### Performance Requirements
- Response time: <100ms (95th percentile)
- Memory usage: Minimal (in-memory SQLite)
- Concurrent requests: Support multiple simultaneous creation requests

## Validation Checklist
*GATE: Checked before task execution*

- [x] All contracts have corresponding tests (TC-001 through TC-004)
- [x] TodoDB entity has model creation task (T010)
- [x] All tests come before implementation (T004-T008 before T009-T014)
- [x] Parallel tasks truly independent (different files marked [P])
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] TDD workflow enforced (tests must fail before implementation)
- [x] FR-001 requirements fully covered by tasks

## Notes
- Focus only on FR-001 (Todo creation) - other CRUD operations (FR-002, FR-003, FR-004) will be separate task sets
- SQLite in-memory database means no persistence between restarts (per requirements)
- Follow FastAPI best practices: Pydantic models, dependency injection, automatic OpenAPI generation
- Maintain type safety with mypy throughout implementation
- Use ruff for consistent code formatting
- All tests must be written first and must fail before any implementation (TDD)

## Task Execution Commands

### Start with Setup
```bash
# T001-T003: Project initialization
mkdir -p src/{models,api,services,database} tests/{contract,integration,unit}
# Configure pyproject.toml and development tools
```

### TDD Phase (Critical)
```bash
# T004-T008: Write failing tests first
pytest tests/contract/ tests/integration/ -v  # Should show failures
```

### Implementation Phase
```bash
# T009-T014: Implement to make tests pass
pytest tests/contract/ tests/integration/ -v  # Should show passing
```

### Quality Assurance
```bash
# T015-T020: Integration and polish
ruff format src/ tests/  # Code formatting
mypy src/  # Type checking
pytest tests/ -v  # All tests passing
```