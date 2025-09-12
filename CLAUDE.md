# Claude Code Context: GSK-Todo

## Project Overview
Todo管理システムのFastAPI実装 - モダンなPython Web APIによる基本的なCRUD操作

## Current Tech Stack
- **Backend**: FastAPI 0.104+, Python 3.11+
- **Database**: SQLite インメモリDB, SQLAlchemy 2.0+  
- **Validation**: Pydantic 2.5+
- **Testing**: pytest, httpx
- **Code Quality**: ruff (lint/format), mypy (types)
- **Server**: uvicorn

## Architecture
```
src/
├── models/          # SQLAlchemy + Pydantic models
├── api/             # FastAPI router endpoints  
├── services/        # Business logic layer
├── database/        # DB config & connection
└── main.py          # Application entry point
```

## Key Components

### Models (src/models/todo.py)
- `TodoDB` - SQLAlchemy ORM model
- `TodoCreate/Update/Response` - Pydantic API models
- Validation: 1-1000 chars, required text field

### API Endpoints (src/api/todos.py)
```
GET    /todos          # List todos (pagination)
POST   /todos          # Create todo
GET    /todos/{id}     # Get specific todo
PUT    /todos/{id}     # Update todo (partial)
DELETE /todos/{id}     # Delete todo
GET    /health         # Health check
```

### Services (src/services/todo_service.py)
- `TodoService` - CRUD operations
- Database session management
- Error handling for not found cases

## Development Workflow

### Constitution Compliance ✓
- TDD: Tests before implementation (RED-GREEN-Refactor)
- Simplicity: Direct FastAPI/SQLAlchemy usage
- No unnecessary patterns (Repository avoided)
- Real dependencies in tests (actual SQLite DB)

### Code Quality Tools
```bash
ruff format src/ tests/     # Format code
ruff check src/ tests/      # Lint check  
mypy src/                   # Type checking
pytest tests/ -v            # Run tests
```

### Development Server
```bash
uvicorn src.main:app --reload --port 8000
# API docs: http://localhost:8000/docs
```

## Testing Strategy
- Contract tests validate API schemas
- Integration tests use TestClient + real DB
- All tests isolated (fresh DB per test)
- FastAPI automatic OpenAPI validation

## Recent Changes (Last 3)
1. **2025-09-13**: Initial project setup with FastAPI + SQLAlchemy
2. **2025-09-13**: Complete API contract definition (OpenAPI spec)
3. **2025-09-13**: Quickstart guide with full implementation example

## Common Commands
```bash
# Start development
uvicorn src.main:app --reload

# Test everything  
pytest tests/ -v

# Quality checks
ruff check --fix src/ tests/
mypy src/

# API testing
curl -X POST "http://localhost:8000/todos/" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test todo", "completed": false}'
```

## Current Status: Phase 1 Complete
- ✅ Research & tech stack decisions
- ✅ Data models (SQLAlchemy + Pydantic)
- ✅ API contracts (OpenAPI spec)
- ✅ Contract test specifications
- ✅ Complete quickstart guide
- ⏳ Next: `/tasks` command for implementation tasks

## Key Files to Know
- `specs/001-todo-management-system/plan.md` - Complete implementation plan
- `specs/001-todo-management-system/contracts/openapi.yaml` - API specification
- `specs/001-todo-management-system/quickstart.md` - Setup & testing guide
- `pyproject.toml` - Dependencies & tool config

## Database Schema
```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text VARCHAR(1000) NOT NULL,
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

## Performance Targets
- 1000 req/s throughput
- <100ms response time (95th percentile)
- <200MB memory usage
- In-memory DB eliminates I/O overhead

---
*Auto-updated by Spec-Driven Development workflow - v0.1.0*