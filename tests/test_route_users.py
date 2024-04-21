from unittest.mock import MagicMock 
import pytest
from src.database.models import User

@pytest.fixture()
def token(client, user, session, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)

    mock_redis = MagicMock(return_value=None)
    monkeypatch.setattr("src.services.client_redis.client_redis.redis_get", mock_redis)
    monkeypatch.setattr("src.services.client_redis.client_redis.redis_set", mock_redis)
    monkeypatch.setattr("src.services.client_redis.client_redis.redis_expire", mock_redis)
    
    mock_send_resets_password = MagicMock(return_value=None)
    mock_send_resets_password.setattr("src.routes.auth.send_resets_password", mock_send_resets_password)

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


def test_read_users_me(client, token):
    response = client.get(
            "/api/users/me",
            headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["username"] == "deadpool"
    assert data["email"] == "deadpool@example.com"
    assert data["avatar"] == "https://www.rpnation.com/gallery/250-x-250-placeholder.30091/full?d=1504582354"
    assert data["confirmed"] == True


def test_update_avatar_user(client, token, monkeypatch):
    file = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR7Scg1gkR27z1fV6jZphvIpKlRTU408Wz8uYS7dWxn8g&s"
    mock_cloud_inary = MagicMock(return_value=file)
    monkeypatch.setattr("src.services.auth.auth_service.cloud_inary", mock_cloud_inary)
    response = client.patch(
                "/api/users/avatar",
                files={"file": file},
                headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["avatar"] == file

    

