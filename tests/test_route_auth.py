from unittest.mock import MagicMock

from src.database.models import User
from src.services.logger import logger
from src.services.auth import auth_service

def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201, "Created"
    data = response.json()
    assert data["email"] == user.get("email")
    assert "id" in data

def test_repeat_create_user_email(client, user):
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
    assert response.status_code == 409, "Conflict"
    data = response.json()
    assert data["detail"] == "An account with this email exists"

def test_repeat_create_user_username(client, user):
    user_copy = user.copy()
    user_copy["email"] = "deadpool1@example.com"
    response = client.post(
        "/api/auth/signup",
        json=user_copy,
    )
    assert response.status_code == 409, "Conflict"
    data = response.json()
    assert data["detail"] == "An account with this username exists"

def test_login_user_no_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, "Unauthorized"
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
    assert response.status_code == 200, "OK"
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
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, "Unauthorized"
    data = response.json()
    assert data["detail"] == "Invalid password"

def test_login_wrong_email(client, user):
    user_c = user.copy()
    user_c["email"] = "deadpool1@example.com"
    response = client.post(
        "/api/auth/login",
        data={"username": user_c.get('email'), "password": user_c.get("password")},
    )
    assert response.status_code == 401, "Unauthorized"
    data = response.json()
    assert data["detail"] == "Invalid email"

def test_login_wrong_username(client, user):
    user_c = user.copy()
    user_c["username"] = "DEADPOOL"
    response = client.post(
        "/api/auth/login",
        data={"username": user_c.get('username'), "password": user_c.get("password")},
    )
    assert response.status_code == 401, "Unauthorized"
    data = response.json()
    assert data["detail"] == "Invalid email"

def test_refresh_token_invalid(client, user, session):
    users = session.query(User).filter(User.email==user["email"]).first()
    old_refresh_t = users.refresh_token
    users.refresh_token = "refresh_token"
    session.commit()
    response = client.get(
        "/api/auth/refresh_token",
        headers={"Authorization": f"Bearer {old_refresh_t}"})
    assert response.status_code == 401, "Unauthorized"
    data = response.json()  
    assert data["detail"] == "Invalid refresh token"

    test_login_user_email(client, session, user)

def test_refresh_token(client, user, session):
    users = session.query(User).filter(User.email==user["email"]).first()
    old_refresh_t = users.refresh_token
    response = client.get(
        "/api/auth/refresh_token",
        headers={"Authorization": f"Bearer {users.refresh_token}"})
    
    assert response.status_code == 200, "OK"
    data = response.json()  
    assert data["access_token"] != None
    users = session.query(User).filter(User.email==user["email"]).first()
    assert data["refresh_token"] == users.refresh_token
    assert data["refresh_token"] == old_refresh_t
    assert data["token_type"] == 'bearer'

def test_reset_password(client, user, session, monkeypatch):
    mock_send_resets_password = MagicMock(return_value={"message": "Email has been sent successfully!"})
    monkeypatch.setattr("src.routes.auth.send_resets_password", mock_send_resets_password)
    users = session.query(User).filter(User.email==user["email"]).first()
    response = client.post(
        "/api/auth/reset_password",
        json={"email": users.email})
    assert response.status_code == 200, "OK"
    data = response.json()  
    assert data["message"] == "Check your email for confirmation."

def test_reset_password_no_email(client):
    response = client.post(
        "/api/auth/reset_password",
        json={"email": "users.email@fake.ua"})
    assert response.status_code == 400, "Bad Request"
    data = response.json()  
    assert data["detail"] == "Email address not found"

def test_reset_password_incorrect_type_email(client):
    response = client.post(
        "/api/auth/reset_password",
        json={"email": None})
    assert response.status_code == 422, "Bad Request"

def test_reset_password_token(client, user, session):
    users = session.query(User).filter(User.email==user["email"]).first()
    old_password = users.password
    token_reset_password = auth_service.create_email_reset_password_token({"sub": user["email"]})
    response = client.post(
        f"/api/auth/reset_password/{token_reset_password}",
        json={"new_password": user["new_password"]})
    assert response.status_code == 200, "OK"
    data = response.json()
    users = session.query(User).filter(User.email==user["email"]).first()
    assert users.password != old_password
    assert data["message"] == "Password has been changed"

def test_reset_password_token_incorrect_email(client, user):
    token_reset_password = auth_service.create_email_reset_password_token({"sub": "deadpool1@example.com"})
    response = client.post(
        f"/api/auth/reset_password/{token_reset_password}",
        json={"new_password": user["new_password"]})
    assert response.status_code == 400, "Bad Request"
    data = response.json()
    assert data["detail"] == "Reset password error"

def test_reset_password_token_incorrect_token(client, user):
    token_reset_password = "incorrect token"
    response = client.post(
        f"/api/auth/reset_password/{token_reset_password}",
        json={"new_password": user["new_password"]})
    assert response.status_code == 422, "Unprocessable Entity"
    data = response.json()
    assert data["detail"] == "Invalid token for email verification"

def test_request_email(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/request_email",
        json={"email": user["email"]})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["message"] == "Your email is already confirmed"

def test_request_email_incorrect_email(client):
    response = client.post(
        "/api/auth/request_email",
        json={"email": "deadpool1@example.com"})
    assert response.status_code == 400, "Bad Request"
    data = response.json()
    assert data["detail"] == "User is emails, was not found."

def test_request_email_confirmed_false(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    users = session.query(User).filter(User.email==user["email"]).first()
    users.confirmed = False
    session.commit()
    response = client.post(
        "/api/auth/request_email",
        json={"email": user["email"]})
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["message"] == "Check your email for confirmation."

def test_confirmed_email(client, user):
    token_verification = auth_service.create_email_token({"sub": user["email"]})
    response = client.get(
        f"/api/auth/confirmed_email/{token_verification}")
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["message"] == "Email confirmed"

def test_confirmed_email_confirmed_false(client, user, session):
    token_verification = auth_service.create_email_token({"sub": user["email"]})
    users = session.query(User).filter(User.email==user["email"]).first()
    users.confirmed = True
    session.commit()
    response = client.get(
        f"/api/auth/confirmed_email/{token_verification}")
    assert response.status_code == 200, "OK"
    data = response.json()
    assert data["message"] == "Your email is already confirmed"

def test_confirmed_email(client):
    token_verification = auth_service.create_email_token({"sub": "deadpool1@example.com"})
    response = client.get(
        f"/api/auth/confirmed_email/{token_verification}")
    assert response.status_code == 400, "Bad Request"
    data = response.json()
    assert data["detail"] == "Verification error"

