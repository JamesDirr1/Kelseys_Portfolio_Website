import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from flask.testing import FlaskClient
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, ANY
from app import app
import time
from app import database_setup, category_list
from data_classes.category import Category
from mysql_connections.mysql_Root import Root
from pymysql.err import OperationalError, MySQLError


# --------------------------------------------------------------------------
# Test root mysql class init
# ---------------------------------------------------------------------------
@patch("mysql_connections.mysql_base.log")
@patch("mysql_connections.mysql_Root.os.getenv")
def test_root_init(
    mock_getenv,
    mock_logger,
):

    env_values = {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3307",
        "MYSQL_ROOT": "root_user",
        "MYSQL_ROOT_PASSWORD": "secret123",
        "MYSQL_DB": "portfolio_db",
    }

    mock_getenv.side_effect = lambda key, default=None: env_values.get(key, default)

    mock_logger_instance = mock_logger.return_value

    real_root = Root()

    assert real_root.host == "localhost"
    assert real_root.port == 3307
    assert real_root.user == "root_user"
    assert real_root.password == "secret123"
    assert real_root.db == "portfolio_db"
    assert real_root.logger == mock_logger_instance
    mock_logger.assert_called_once_with("ROOT")


# --------------------------------------------------------------------------
# Test database connection testing
# --------------------------------------------------------------------------
def test_root_try_connection():
    with app.app_context():
        mock_tables = [
            {"Tables_in_Portfolio": "VV.category"},
            {"Tables_in_Portfolio": "VV.image"},
            {"Tables_in_Portfolio": "VV.project"},
            {"Tables_in_Portfolio": "VV.users"},
            {"Tables_in_Portfolio": "category"},
            {"Tables_in_Portfolio": "image"},
            {"Tables_in_Portfolio": "project"},
            {"Tables_in_Portfolio": "users"},
            {"Tables_in_Portfolio": "site_meta"},
            {"Tables_in_Portfolio": "VV.site_meta"},
        ]

        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(return_value=mock_tables)

        result = root.try_connection()

        assert result == True


def test_root_try_connection_missing_table():
    with app.app_context():
        root = Root()

        mock_tables = [
            {"Tables_in_Portfolio": "VV.category"},
            {"Tables_in_Portfolio": "VV.image"},
            {"Tables_in_Portfolio": "VV.project"},
            {"Tables_in_Portfolio": "VV.users"},
            {"Tables_in_Portfolio": "category"},
            {"Tables_in_Portfolio": "image"},
            {"Tables_in_Portfolio": "project"},
            {"Tables_in_Portfolio": "site_meta"},
            {"Tables_in_Portfolio": "VV.site_meta"},
        ]

        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(return_value=mock_tables)

        result = root.try_connection()

        assert result == False


def test_root_try_connection_mysql_error():
    with app.app_context():
        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(side_effect=MySQLError)

        result = root.try_connection()

        assert result == False


def test_root_try_connection_exception():
    with app.app_context():
        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(side_effect=Exception)

        result = root.try_connection()

        assert result == False


# --------------------------------------------------------------------------
# create_db_user testing.
# --------------------------------------------------------------------------
@patch.dict(
    os.environ,
    {"MYSQL_VIEW_USER": "view_user", "MYSQL_VIEW_USER_PASSWORD": "view_password"},
    clear=True,
)
def test_root_create_db_users():
    with app.app_context():
        mock_results = []

        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(return_value=mock_results)
        root.execute_sensitive = MagicMock()
        root.execute = MagicMock()

        root.create_db_users()

        root.execute_sensitive.assert_any_call(
            "CREATE USER IF NOT EXISTS %s IDENTIFIED BY %s;",
            ["view_user", "view_password"],
        )

        expected_grants = [
            "GRANT SELECT ON `VV.category` TO %s;",
            "GRANT SELECT ON `VV.project` TO %s;",
            "GRANT SELECT ON `VV.image` TO %s;",
            "GRANT SELECT ON `VV.users` TO %s;",
            "GRANT SELECT ON `VV.site_meta` TO %s;",
        ]
        for grant_query in expected_grants:
            root.execute.assert_any_call(grant_query, ["view_user"])

        root.execute.assert_any_call("FLUSH PRIVILEGES")


@patch.dict(
    os.environ,
    {"MYSQL_VIEW_USER": "view_user", "MYSQL_VIEW_USER_PASSWORD": "view_password"},
    clear=True,
)
def test_root_create_db_users_already_exist():
    with app.app_context():
        mock_results = ["user"]
        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(return_value=mock_results)
        root.execute_sensitive = MagicMock()
        root.execute = MagicMock()

        root.create_db_users()
        root.execute_sensitive.assert_not_called()  # Makes sure user creation query is not executed


@patch.dict(
    os.environ,
    {"MYSQL_VIEW_USER": "view_user", "MYSQL_VIEW_USER_PASSWORD": "view_password"},
    clear=True,
)
def test_root_create_db_users_pymysql_error():
    with app.app_context():
        mock_results = []
        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(return_value=mock_results)
        root.execute_sensitive = MagicMock(side_effect=MySQLError("Database error"))
        root.execute = MagicMock()
        print(MySQLError)
        print(root.execute_sensitive.side_effect.__class__)
        with pytest.raises(MySQLError):
            root.create_db_users()


@patch.dict(
    os.environ,
    {"MYSQL_VIEW_USER": "view_user", "MYSQL_VIEW_USER_PASSWORD": "view_password"},
    clear=True,
)
def test_root_create_db_users_exception():
    with app.app_context():
        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(side_effect=Exception("Unknown error"))
        root.execute_sensitive = MagicMock()
        root.execute = MagicMock()

        with pytest.raises(Exception):
            root.create_db_users()


# --------------------------------------------------------------------------
# Added web admin user testing
# --------------------------------------------------------------------------
@patch.dict(
    os.environ,
    {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "admin_password"},
    clear=True,
)
@patch(
    "mysql_connections.mysql_Root.generate_password_hash",
    return_value="hashed-password",
)
def test_root_add_admin_users(mock_hash):
    with app.app_context():
        mock_results = []
        root = Root()
        root.logger = MagicMock()
        root.fetch_all_sensitive = MagicMock(return_value=mock_results)
        root.execute_sensitive = MagicMock()

        root.add_admin_user()

        mock_hash.assert_called_once_with("admin_password")
        root.execute_sensitive.assert_called_once_with(
            "INSERT INTO `users` (user_name, user_password) VALUES (%s,%s)",
            ["admin", "hashed-password"],
        )


@patch.dict(
    os.environ,
    {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "admin_password"},
    clear=True,
)
def test_root_add_admin_users_exist():
    with app.app_context():
        mock_results = ["user"]
        root = Root()
        root.logger = MagicMock()
        root.fetch_all_sensitive = MagicMock(return_value=mock_results)
        root.execute_sensitive = MagicMock()

        root.add_admin_user()

        root.fetch_all_sensitive.assert_called_once_with(
            "SELECT * FROM `users` WHERE user_name= %s;", ["admin"]
        )
        root.execute_sensitive.assert_not_called()


@patch.dict(
    os.environ,
    {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "admin_password"},
    clear=True,
)
def test_root_add_admin_users_mysql_error():
    with app.app_context():
        root = Root()
        root.logger = MagicMock()
        root.fetch_all_sensitive = MagicMock(side_effect=MySQLError("database error"))
        root.execute_sensitive = MagicMock()

        with pytest.raises(MySQLError):
            root.add_admin_user()


@patch.dict(
    os.environ,
    {"ADMIN_USERNAME": "admin", "ADMIN_PASSWORD": "admin_password"},
    clear=True,
)
def test_root_add_admin_users_exception():
    with app.app_context():
        root = Root()
        mock_results = []
        root.logger = MagicMock()
        root.fetch_all_sensitive = MagicMock(return_value=mock_results)
        root.execute_sensitive = MagicMock(side_effect=Exception("some error"))

        with pytest.raises(Exception):
            root.add_admin_user()


# --------------------------------------------------------------------------
# Test creating test data
# --------------------------------------------------------------------------
def test_root_create_test_data():
    with app.app_context():
        mock_results = []
        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(return_value=mock_results)
        root.execute = MagicMock()

        root.create_test_data()

        assert root.execute.call_count == 2
        root.execute.assert_any_call("Call test_data();")


def test_root_create_test_data_exist():
    with app.app_context():
        mock_results = ["data"]
        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(return_value=mock_results)
        root.execute = MagicMock()

        root.create_test_data()

        root.execute.assert_not_called()


def test_root_create_test_data_mysql_error():
    with app.app_context():
        root = Root()
        root.logger = MagicMock()
        root.fetch_all = MagicMock(side_effect=MySQLError)
        root.execute = MagicMock()

        with pytest.raises(Exception):
            root.create_test_data()
