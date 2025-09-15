"""
Main FastAPI application.
FR-001 focused: Todo creation functionality
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.todos import router as todos_router
from src.database.config import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフスパン管理 - データベーステーブル作成"""
    create_tables()
    yield


app = FastAPI(
    title="Todo Management API",
    description="基本的なTodo管理機能を提供するREST API (FR-001 focused)",
    version="0.1.0",
    lifespan=lifespan
)

# ルーター登録
app.include_router(todos_router)


@app.get("/health")
def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
