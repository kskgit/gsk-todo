"""
Pytest configuration and shared fixtures.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.todos import router as todos_router
from src.database.config import Base
from src.models.todo import TodoDB  # Ensure model is imported


@pytest.fixture(scope="function")
def test_client():
    """テスト用クライアントを提供（各テストで独立したDB）"""
    # Create a test database engine using a temporary file
    test_engine = create_engine("sqlite:///./test_temp.db", connect_args={"check_same_thread": False})
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Make sure all models are imported before creating tables
    TodoDB  # Ensure model is referenced

    # Create tables
    Base.metadata.create_all(bind=test_engine)

    # Create a fresh FastAPI app for testing
    test_app = FastAPI(
        title="Test Todo Management API",
        description="Test instance",
        version="0.1.0"
    )

    # Override get_db for testing
    def get_test_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Import get_db from original location for dependency override
    from src.database.config import get_db

    # Override the database dependency
    test_app.dependency_overrides[get_db] = get_test_db

    # Include router
    test_app.include_router(todos_router)

    @test_app.get("/health")
    def health_check():
        return {"status": "healthy"}

    with TestClient(test_app) as client:
        yield client

    Base.metadata.drop_all(bind=test_engine)

    # Clean up test database file
    import os
    if os.path.exists("./test_temp.db"):
        os.remove("./test_temp.db")
