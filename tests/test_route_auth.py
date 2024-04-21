from unittest.mock import MagicMock

from src.database.models import User
from src.services.logger import logger
from src.services.auth import auth_service

def test_create_user(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        json=user,
    )
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

def test_reset_password(client, user, session):
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
    logger.critical(response)
    assert response.status_code == 200, response.text
    data = response.json()
    users = session.query(User).filter(User.email==user["email"]).first()
    assert users.password != old_password
    assert data["message"] == "Password has been changed"


# @router.post('/reset_password/{token}')
# @limiter.limit("10/minute")
# async def reset_password_token(body: RequestUserNewPassword, request: Request, token: str, db: Session = Depends(get_db)): #  -> dict | HTTPException
#     """
#     Resets the user's password using the reset token.

#     Args:
#         body (RequestUserNewPassword): The request body containing the new password.
#         request (Request): The request object.
#         token (str): The reset token.
#         db (Sessionl): The database session. Defaults to Depends(get_db).

#     Returns:
#         Dict, HTTPException]: A dictionary with a success message if the password reset is successful,
#         or an HTTPException with a status code and detail message if there's a reset password error.
#     """
#     email = await auth_service.get_email_from_token(token)
#     user = await repository_users.get_user_by_email(email, db)
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset password error")
#     if user:
#         user.password = auth_service.get_password_hash(body.new_password)
#         db.commit()
#         return {"message": "Password has been changed"}
