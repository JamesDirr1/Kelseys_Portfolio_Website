import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch, MagicMock
from app import app
from datetime import date
from app import database_setup, category_list


def test_login_not_authed(test_login_client_and_mocks):
    client, _ = test_login_client_and_mocks
    response = client.get("/admin/login")
    assert response.request.path == "/admin/login"
    assert response.status_code == 200
    assert b"""<h1>Login</h1>""" in response.data

def test_login_authed(test_login_client_and_mocks):
    client, _ = test_login_client_and_mocks

    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.get("/admin/dashboard", follow_redirects=True)
    assert response.request.path == "/admin/dashboard"
    assert response.status_code == 200
    assert b"""<h2>Admin Dashboard</h2>""" in response.data

def test_require_login_success(test_login_client_and_mocks):
    client, mock_view_user= test_login_client_and_mocks

    mock_view_user.check_user_exist_and_password.return_value = (True, True)

    response = client.post("/admin/login", data={
        "username": "testuser",
        "password": "testpass"
    }, follow_redirects=True)

    assert response.request.path == "/admin/dashboard"
    assert response.status_code == 200
    assert b"""<h2>Admin Dashboard</h2>""" in response.data
    assert b"Login successful!" in response.data

def test_require_login_bad_username(test_login_client_and_mocks):
    client, mock_view_user= test_login_client_and_mocks

    mock_view_user.check_user_exist_and_password.return_value = (False, True)

    response = client.post("/admin/login", data={
        "username": "baduser",
        "password": "testpass"
    }, follow_redirects=True)

    assert response.request.path == "/admin/login"
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data

def test_require_login_bad_password(test_login_client_and_mocks):
    client, mock_view_user= test_login_client_and_mocks

    mock_view_user.check_user_exist_and_password.return_value = (True, False)

    response = client.post("/admin/login", data={
        "username": "testuser",
        "password": "badpass"
    }, follow_redirects=True)

    assert response.request.path == "/admin/login"
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data

def test_require_login_bad_password(test_login_client_and_mocks):
    client, mock_view_user= test_login_client_and_mocks

    mock_view_user.check_user_exist_and_password.return_value = (False, False)

    response = client.post("/admin/login", data={
        "username": "baduser",
        "password": "badpass"
    }, follow_redirects=True)

    assert response.request.path == "/admin/login"
    assert response.status_code == 200
    assert b"Invalid credentials" in response.data