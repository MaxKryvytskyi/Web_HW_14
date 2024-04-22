import pytest
from unittest.mock import MagicMock 
from src.database.models import User
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import server
from src.database.models import Base
from src.database.db import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    server.dependency_overrides[get_db] = override_get_db

    yield TestClient(server)


@pytest.fixture(scope="module")
def user():
    return {"username": "deadpool", "email": "deadpool@example.com", "password": "123456789", "new_password": "12345678910"}

@pytest.fixture(scope="module")
def user2():
    return {"username": "deadpool2", "email": "deadpool2@example.com", "password": "123456789", "new_password": "12345678910"}

@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_redis = MagicMock(return_value=None)
    monkeypatch.setattr("src.services.client_redis.client_redis.redis_get", mock_redis)
    monkeypatch.setattr("src.services.client_redis.client_redis.redis_set", mock_redis)
    monkeypatch.setattr("src.services.client_redis.client_redis.redis_expire", mock_redis)

    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    client.post("/api/auth/signup", json=user)
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    data = response.json()
    return data["access_token"]

@pytest.fixture()
def token2(client, user2, session, monkeypatch):
    mock_redis = MagicMock(return_value=None)
    monkeypatch.setattr("src.services.client_redis.client_redis.redis_get", mock_redis)
    monkeypatch.setattr("src.services.client_redis.client_redis.redis_set", mock_redis)
    monkeypatch.setattr("src.services.client_redis.client_redis.redis_expire", mock_redis)

    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    client.post("/api/auth/signup", json=user2)
    current_user: User = session.query(User).filter(User.email == user2.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user2.get('email'), "password": user2.get('password')},
    )
    data = response.json()
    return data["access_token"]

