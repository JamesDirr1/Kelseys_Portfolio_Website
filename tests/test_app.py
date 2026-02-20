import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import patch, MagicMock
from app import app
import time
from app import database_setup, category_list
from data_classes.category import Category


def test_database_setup_success(test_app_client_and_mocks, caplog):
    _, mock_root, _, mock_logger = test_app_client_and_mocks
    # Ensure try_connection returns True
    mock_root.try_connection.return_value = True

    with patch("time.sleep", return_value=None) as mock_sleep:
        result = database_setup()

    # Verify the correct calls were made
    mock_root.try_connection.assert_called_once()
    assert result == True


def test_database_setup_failed_connection(test_app_client_and_mocks):
    _, mock_root, _, mock_logger = test_app_client_and_mocks
    mock_root.try_connection.side_effect = [False, True]

    with patch("time.sleep", return_value=None) as mock_sleep:
        result = database_setup()

    # Verify the correct calls were made
    assert mock_root.try_connection.call_count == 2
    assert result == True


def test_database_setup_failed_connection_exception(test_app_client_and_mocks):
    _, mock_root, _, mock_logger = test_app_client_and_mocks
    mock_root.try_connection.side_effect = [Exception("Connection Failed"), True]

    with patch("time.sleep", return_value=None) as mock_sleep:
        result = database_setup()

    # Verify the correct calls were made

    assert mock_root.try_connection.call_count == 2
    assert result == True


def test_database_setup_create_users(test_app_client_and_mocks):
    _, mock_root, _, _ = test_app_client_and_mocks
    mock_root.try_connection.return_value = True

    with patch("time.sleep", return_value=None) as mock_sleep:
        result = database_setup()

    # Verify the correct calls were made
    assert mock_root.create_db_users.call_once()
    assert result == True


def test_database_setup_create_users_failed(test_app_client_and_mocks):
    _, mock_root, _, mock_logger = test_app_client_and_mocks
    mock_root.try_connection.return_value = True
    mock_root.create_db_users.side_effect = Exception("Connection Failed")

    with patch("time.sleep", return_value=None) as mock_sleep:
        result = database_setup()

    # Verify the correct calls were made
    assert mock_root.create_users.call_once()
    assert result == False



def test_database_setup_create_admin_user_failed(test_app_client_and_mocks):
    _, mock_root, _, mock_logger = test_app_client_and_mocks
    mock_root.try_connection.return_value = True
    mock_root.add_admin_user.side_effect = Exception("Connection Failed")

    with patch("time.sleep", return_value=None) as mock_sleep:
        result = database_setup()

    # Verify the correct calls were made
    assert mock_root.add_admin_user.call_once()
    assert result == False

def test_database_setup_create_test_data(test_app_client_and_mocks):
    _, mock_root, _, mock_logger = test_app_client_and_mocks
    mock_root.try_connection.return_value = True

    with patch("time.sleep", return_value=None) as mock_sleep:
        result = database_setup()

    # Verify the correct calls were made
    assert mock_root.create_test_data.call_once()
    assert result == True


def test_database_setup_create_test_data_failed(test_app_client_and_mocks):
    _, mock_root, _, mock_logger = test_app_client_and_mocks
    mock_root.try_connection.return_value = True
    mock_root.create_test_data.side_effect = Exception("Connection Failed")

    with patch("time.sleep", return_value=None) as mock_sleep:
        result = database_setup()

    # Verify the correct calls were made
    assert mock_root.create_test_data.call_once()
    assert result == False


def test_category_list(test_app_client_and_mocks):
    _, _, mock_view_user, _ = test_app_client_and_mocks

    test_list = [
        Category("test", 1, 1),
        Category("test_2", 2, 2),
        Category("About", 0, 3),
    ]

    mock_view_user.get_all_categories.return_value = [
        Category("test", 1, 1),
        Category("test_2", 2, 2),
    ]

    cat_list = category_list()

    assert test_list == cat_list


def test_category_list_no_categories(test_app_client_and_mocks):
    _, _, mock_view_user, _ = test_app_client_and_mocks

    test_list = [Category("About", 0, 1)]

    mock_view_user.get_all_categories.return_value = []

    cat_list = category_list()

    assert test_list == cat_list


def test_index_redirect(test_app_client_and_mocks):
    client, _, mock_view_user, _ = test_app_client_and_mocks
    mock_view_user.get_all_categories.return_value = [Category("test", 1, 1)]

    with patch("routes.route_category.mysql_view_user.View_User") as CategoryViewUser:

        category_view_user = MagicMock()
        CategoryViewUser.return_value = category_view_user

        category_view_user.get_category_by_title.return_value = Category("test", 1, 1)

        response = client.get("/", follow_redirects=True)

        assert response.request.path == "/portfolio/test"
        assert response.status_code == 200


# UPDATE WHEN ABOUT IS NOT HARD CODED
def test_index_redirect_no_categories(test_app_client_and_mocks):
    client, _, mock_view_user, _ = test_app_client_and_mocks
    mock_view_user.get_all_categories.return_value = []

    with patch("routes.route_category.mysql_view_user.View_User") as CategoryViewUser:

        category_view_user = MagicMock()
        CategoryViewUser.return_value = category_view_user

        category_view_user.get_category_by_title.return_value = []

        response = client.get("/", follow_redirects=True)

        assert response.request.path == "/portfolio/About"
        assert response.status_code == 200


def test_404_page(test_app_client_and_mocks):
    client, _, mock_view_user, _ = test_app_client_and_mocks
    mock_view_user.get_all_categories.return_value = [Category("test", 1, 1)]

    response = client.get("/NotAPage")
    assert response.status_code == 404
    assert b"Page Not Found" in response.data


def test_500_page(test_app_client_and_mocks):
    client, _, mock_view_user, _ = test_app_client_and_mocks
    mock_view_user.get_all_categories.return_value = []
    response = client.get("/error")
    assert response.status_code == 500
    assert b"Internal Server Error" in response.data
