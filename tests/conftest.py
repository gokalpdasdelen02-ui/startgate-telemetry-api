import os
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

TEST_API_KEY = "test-api-key"

# Uygulama modülleri yüklenmeden önce test ayarlarını tanımlıyoruz.
os.environ["TELEMETRY_API_KEY"] = TEST_API_KEY
os.environ["DATABASE_URL"] = "sqlite://"

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    test_database_path = tmp_path / "test_telemetry.db"
    test_database_url = f"sqlite:///{test_database_path}"

    test_engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    return {
        "X-API-Key": TEST_API_KEY,
    }


@pytest.fixture()
def valid_info_event() -> dict[str, object]:
    return {
        "category": "info",
        "platform": "Web",
        "os_version": "macOS 15",
        "device": "Macbook Air",
        "client_ts": 1753354000,
        "user_id": "test-user-001",
        "session_id": "test-session-001",
        "session_num": 1,
        "sdk_version": "1.0.0",
        "manufacturer": "Apple",
        "v": "1.0.0",
        "event_data": {
            "message": "Test event",
        },
    }
