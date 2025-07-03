import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch, MagicMock
from app import app
from datetime import date
from app import database_setup, category_list


def test_dashboard_not_authed(test_dashboard_client_and_mocks):
    client, _ = test_dashboard_client_and_mocks
    response = client.get("/admin/dashboard", follow_redirects=True)
    assert response.request.path == "/admin/login"
    assert response.status_code == 200
    assert b"""<h1>Login</h1>""" in response.data

def test_dashboard_authed(test_dashboard_client_and_mocks):
    client, _ = test_dashboard_client_and_mocks

    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.get("/admin/dashboard", follow_redirects=True)
    assert response.request.path == "/admin/dashboard"
    assert response.status_code == 200
    assert b"""<h2>Admin Dashboard</h2>""" in response.data

def test_dashboard_admin_redirect(test_dashboard_client_and_mocks):
    client, _ = test_dashboard_client_and_mocks

    with client.session_transaction() as sess:
        sess['logged_in'] = True

    response = client.get("/admin", follow_redirects=True)
    assert response.request.path == "/admin/dashboard"
    assert response.status_code == 200
    assert b"""<h2>Admin Dashboard</h2>""" in response.data