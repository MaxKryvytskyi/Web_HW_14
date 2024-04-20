from unittest.mock import MagicMock

from src.database.models import User
from src.services.logger import logger

def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    logger.critical(response)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == user.get("email")
    assert "id" in data

def test_repeat_create_user_email(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    logger.critical(response)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "An account with this email exists"

def test_repeat_create_user_username(client, user):
    user_copy = user.copy()
    user_copy["email"] = "deadpool1@example.com"
    response = client.post(
        "/api/auth/signup",
        json=user_copy,
    )
    logger.critical(response)
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "An account with this username exists"

def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    logger.critical(response)
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"

def test_login_user_email(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    logger.critical(response)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"

def test_login_user_username(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('username'), "password": user.get('password')},
    )
    logger.critical(response)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    logger.critical(response)
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"

def test_login_wrong_email(client, user):
    user_c = user.copy()
    user_c["email"] = "deadpool1@example.com"
    response = client.post(
        "/api/auth/login",
        data={"username": user_c.get('email'), "password": user_c.get("password")},
    )
    logger.critical(response)
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"

def test_login_wrong_username(client, user):
    user_c = user.copy()
    user_c["username"] = "DEADPOOL"
    response = client.post(
        "/api/auth/login",
        data={"username": user_c.get('username'), "password": user_c.get("password")},
    )
    logger.critical(response)
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"




def test_():
    pass