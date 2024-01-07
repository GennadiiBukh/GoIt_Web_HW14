from unittest.mock import Mock, MagicMock
from src.database.models import User
from src.conf import messages
from src.services.auth import create_access_token


def test_register_user_api(client, user, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post("auth/auth/register", json=user)
    assert response.status_code == 201, response.text
    mock_send_email.assert_called_once()
    response_data = response.json()
    assert response_data["username"] == user["username"]
    assert response_data["email"] == user["email"]
    assert "password" not in response_data
    assert "id" in response_data

def test_repeat_register_user(client, user):
    response = client.post("auth/auth/register", json=user,)
    assert response.status_code == 409, response.text
    response_data = response.json()
    assert response_data["detail"] == messages.ACCOUNT_EXIST

def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/auth/auth/token",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    response_data = response.json()
    assert response_data["detail"] == messages.NOTCONFIRMED


def test_login_for_access_token(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post("auth/auth/token", data={"username": user.get('email'), "password": user.get('password')})
    assert response.status_code == 200, response.text
    response_data = response.json()
    assert "access_token" in response_data
    assert "refresh_token" in response_data
    assert response_data["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    # wrong password test
    response = client.post("/auth/auth/token", data={"username": user.get('email'), "password": 'password'},)
    assert response.status_code == 401, response.text
    response_data = response.json()
    assert response_data["detail"] == messages.INCORRECT_LOGIN
    # wrong email test
    response = client.post("/auth/auth/token", data={"username": 'email', "password": user.get('password')},)
    assert response.status_code == 401, response.text
    response_data = response.json()
    assert response_data["detail"] == messages.INCORRECT_LOGIN


def test_refresh_access_token(client, session, user):
    response = client.post("/auth/auth/token", data={"username": user.get('email'), "password": user.get('password')})
    login_data = response.json()
    refresh_token = login_data.get('refresh_token')
    assert refresh_token is not None
    # використовуємо отриманий refresh_token для тестування оновлення токену
    response = client.post("/auth/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200, response.text
    response_data = response.json()
    print(response_data)
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


def test_confirmed_email(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = False
    session.commit()
    test_token = create_access_token(data={"sub": current_user.email})
    response = client.get(f"/auth/auth/confirmed_email/{test_token}")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == messages.CONFIRMED


def test_confirmed_email_already(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    test_token = create_access_token(data={"sub": current_user.email})
    response = client.get(f"/auth/auth/confirmed_email/{test_token}")
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["detail"] == messages.ALREADY_CONFIRMED


def test_confirmed_email_wrong(client, session, user):
    test_token = create_access_token(data={"sub": "wrong_email"})
    response = client.get(f"/auth/auth/confirmed_email/{test_token}")
    assert response.status_code == 400
    response_data = response.json()
    assert response_data["detail"] == messages.VERIFICATION_ERROR





