import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from unittest.mock import patch, MagicMock, ANY
from app import app
import time
from app import database_setup, category_list
from data_classes.category import Category
from mysql_connections.mysql_Root import Root
from pymysql import MySQLError


@patch("mysql_connections.mysql_Root.utility_classes.custom_logger.log")
@patch("mysql_connections.mysql_Root.os.getenv")
def test_root_init(mock_getenv, mock_logger, test_mysql_root_client_and_mocks):
    _, _, _, _ = test_mysql_root_client_and_mocks

    env_values = {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3307",
        "MYSQL_ROOT": "root_user",
        "MYSQL_ROOT_PASSWORD": "secret123",
        "MYSQL_DB": "portfolio_db",
        "MYSQL_VIEW_USER": "readonly_user",
        "MYSQL_VIEW_USER_PASSWORD": "readonly_pass"
    }

    mock_getenv.side_effect = lambda key, default=None: env_values.get(key, default)

    mock_logger_instance = mock_logger.return_value

    real_root = Root()

    assert real_root.host == "localhost"
    assert real_root.port == 3307
    assert real_root.user == "root_user"
    assert real_root.password == "secret123"
    assert real_root.db == "portfolio_db"
    assert real_root.view_user == "readonly_user"
    assert real_root.view_user_password == "readonly_pass"
    assert real_root.logger == mock_logger_instance
    mock_logger.assert_called_once_with("ROOT")

def test_root_create_connection_success():
    with app.app_context(): 
        root = Root()

        mock_connection = MagicMock()
        with patch('mysql_connections.mysql_Root.pymysql.connect', return_value=mock_connection) as mock_connect, \
            patch.object(root.logger, 'info') as mock_info_logger, \
            patch.object(root.logger, 'error') as mock_error_logger:
        
            connection = root.create_connection()

            mock_connect.assert_called_once_with(
                host=root.host,
                port=root.port,
                user=root.user,
                password=root.password,
                database=root.db,
                cursorclass=ANY
            )

            assert connection == mock_connection
            mock_info_logger.assert_any_call(f"Creating connection to: {root.host}")
            mock_info_logger.assert_any_call("Connection created")
            mock_error_logger.assert_not_called()

def test_root_create_connection_mysql_error():
    with app.app_context():
        root = Root()

        with patch('mysql_connections.mysql_Root.pymysql.connect', side_effect=MySQLError("Mocked MySQL failure")), \
            patch.object(root.logger, 'error') as mock_error:

            with pytest.raises(MySQLError):
                root.create_connection()

            mock_error.assert_called_with("Connection failed, could not create connection: Mocked MySQL failure")

def test_root_create_connection_general_error():
    with app.app_context():
        root = Root()

        with patch('mysql_connections.mysql_Root.pymysql.connect', side_effect=RuntimeError("Mocked failure")), \
            patch.object(root.logger, 'error') as mock_error:

            with pytest.raises(RuntimeError):
                root.create_connection()

            mock_error.assert_called_with("Unexpected error, could not create connection:: Mocked failure")

def test_root_try_connection():
    with app.app_context():
        root = Root()

        mock_tables = [
            {'Tables_in_Portfolio': 'VV.category'},
            {'Tables_in_Portfolio': 'VV.image'},
            {'Tables_in_Portfolio': 'VV.project'},
            {'Tables_in_Portfolio': 'VV.users'},
            {'Tables_in_Portfolio': 'category'},
            {'Tables_in_Portfolio': 'image'},
            {'Tables_in_Portfolio': 'project'},
            {'Tables_in_Portfolio': 'users'},
        ]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_tables

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        with patch.object(root, 'create_connection', return_value=mock_connection), \
            patch.object(root.logger, 'info') as mock_info, \
            patch.object(root.logger, 'error') as mock_error, \
            patch.object(root.logger, 'debug') as mock_debug, \
            patch.object(root.logger, 'query') as mock_query, \
            patch.object(root.logger, 'con_open'), \
            patch.object(root.logger, 'con_close'):

            result = root.try_connection()

            assert result is True
            mock_cursor.execute.assert_called_with("Show tables;")
            mock_query.assert_called()
            mock_info.assert_any_call("All tables have been created - Database is ready")
            mock_error.assert_not_called()

def test_root_try_connection_missing_table():
    with app.app_context():
        root = Root()

        mock_tables = [
            {'Tables_in_Portfolio': 'VV.category'},
            {'Tables_in_Portfolio': 'VV.image'},
            {'Tables_in_Portfolio': 'VV.project'},
            {'Tables_in_Portfolio': 'VV.users'},
            {'Tables_in_Portfolio': 'category'},
            {'Tables_in_Portfolio': 'image'},
            {'Tables_in_Portfolio': 'project'}
        ]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_tables

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        with patch.object(root, 'create_connection', return_value=mock_connection), \
            patch.object(root.logger, 'info') as mock_info, \
            patch.object(root.logger, 'error') as mock_error, \
            patch.object(root.logger, 'debug') as mock_debug, \
            patch.object(root.logger, 'query') as mock_query, \
            patch.object(root.logger, 'con_open'), \
            patch.object(root.logger, 'con_close'):

            result = root.try_connection()

            assert result is False
            mock_cursor.execute.assert_called_with("Show tables;")
            mock_query.assert_called()
            mock_error.assert_any_call("Tables do not match. Missing tables: {'users'}")


def test_root_try_connection_mysql_error():
        with app.app_context():
            root = Root()

            with patch.object(root, 'create_connection', side_effect=MySQLError("Mocked MySQL failure")), \
                patch.object(root.logger, 'info') as mock_info, \
                patch.object(root.logger, 'error') as mock_error, \
                patch.object(root.logger, 'debug') as mock_debug, \
                patch.object(root.logger, 'query') as mock_query, \
                patch.object(root.logger, 'con_open'), \
                patch.object(root.logger, 'con_close'):

                result = root.try_connection()

                assert result is False
                mock_error.assert_called_once()
                logged_message = mock_error.call_args[0][0]
                assert "Unable to connect to server:" in logged_message

def test_root_create_users():
    with app.app_context():
        root = Root()

        mock_users = []

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_users

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        with patch.object(root, 'create_connection', return_value=mock_connection), \
            patch.object(root.logger, 'info') as mock_info, \
            patch.object(root.logger, 'error') as mock_error, \
            patch.object(root.logger, 'debug') as mock_debug, \
            patch.object(root.logger, 'query') as mock_query, \
            patch.object(root.logger, 'con_open'), \
            patch.object(root.logger, 'con_close'):

            root.create_users()

            mock_cursor.execute.assert_any_call(
                f"CREATE USER IF NOT EXISTS 'View_User'@'%' IDENTIFIED BY '{root.view_user_password}';"
            )

            expected_grants = [
                f"GRANT SELECT ON `VV.category` TO '{root.view_user}'@'%';",
                f"GRANT SELECT ON `VV.project` TO '{root.view_user}'@'%';",
                f"GRANT SELECT ON `VV.image` TO '{root.view_user}'@'%';",
                f"GRANT SELECT ON `VV.users` TO '{root.view_user}'@'%';",
                "FLUSH PRIVILEGES;"
            ]
            for grant_query in expected_grants:
                mock_cursor.execute.assert_any_call(grant_query)

            mock_connection.commit.assert_called()

def test_root_create_users_already_exist():
    with app.app_context():
        root = Root()

        mock_users = [{'user': root.view_user}]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_users

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        with patch.object(root, 'create_connection', return_value=mock_connection), \
            patch.object(root.logger, 'info') as mock_info, \
            patch.object(root.logger, 'error') as mock_error, \
            patch.object(root.logger, 'debug') as mock_debug, \
            patch.object(root.logger, 'query') as mock_query, \
            patch.object(root.logger, 'con_open'), \
            patch.object(root.logger, 'con_close'):

            root.create_users()

            create_user_call = f"CREATE USER IF NOT EXISTS 'View_User'@'%' IDENTIFIED BY '{root.view_user_password}';"
            assert create_user_call not in [args[0] for args, _ in mock_cursor.execute.call_args_list]
            mock_info.assert_any_call("Users already exist")
            mock_cursor.execute.called_once()

def test_root_create_users_pymysql_error():
    with app.app_context():
        root = Root()

        with patch.object(root, 'create_connection', side_effect=MySQLError("Mocked MySQL failure")), \
            patch.object(root.logger, 'info') as mock_info, \
            patch.object(root.logger, 'error') as mock_error, \
            patch.object(root.logger, 'debug') as mock_debug, \
            patch.object(root.logger, 'query') as mock_query, \
            patch.object(root.logger, 'con_open'), \
            patch.object(root.logger, 'con_close'):

            root.create_users()

            mock_error.assert_any_call("Was not able to create users: Mocked MySQL failure")

def test_root_add_admin_users():
    with app.app_context():

        env_values = {
            "ADMIN_USERNAME": "Admin_user",
            "ADMIN_PASSWORD": "password"
        }

        with patch('os.getenv', side_effect=lambda key, default=None: env_values.get(key, default)):

            root = Root()

            mock_users = []

            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = mock_users

            mock_connection = MagicMock()
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

            with patch.object(root, 'create_connection', return_value=mock_connection), \
                patch.object(root.logger, 'info') as mock_info, \
                patch.object(root.logger, 'error') as mock_error, \
                patch.object(root.logger, 'debug') as mock_debug, \
                patch.object(root.logger, 'query') as mock_query, \
                patch.object(root.logger, 'con_open'), \
                patch.object(root.logger, 'con_close'):

                root.add_admin_user()

                mock_cursor.execute.assert_any_call(
                f"INSERT INTO users (user_name, user_password) VALUES (%s,%s)", ('Admin_user', ANY)
                )
                mock_connection.commit.assert_called()

def test_root_add_admin_users_exist():
    with app.app_context():

        env_values = {
            "ADMIN_USERNAME": "Admin_user",
            "ADMIN_PASSWORD": "password"
        }

        with patch('os.getenv', side_effect=lambda key, default=None: env_values.get(key, default)):

            root = Root()

            
            mock_users = [{"admin_user"}]

            mock_cursor = MagicMock()
            mock_cursor.fetchall.return_value = mock_users

            mock_connection = MagicMock()
            mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

            with patch.object(root, 'create_connection', return_value=mock_connection), \
                patch.object(root.logger, 'info') as mock_info, \
                patch.object(root.logger, 'error') as mock_error, \
                patch.object(root.logger, 'debug') as mock_debug, \
                patch.object(root.logger, 'query') as mock_query, \
                patch.object(root.logger, 'con_open'), \
                patch.object(root.logger, 'con_close'):

                root.add_admin_user()

                mock_cursor.execute.called_once()
                mock_info.assert_any_call(f"Admin user Admin_user already exist")

def test_root_add_admin_users_mysql_error():
    with app.app_context():
        root = Root()


        with patch.object(root, 'create_connection', side_effect=MySQLError("Mocked MySQL failure")), \
            patch.object(root.logger, 'info') as mock_info, \
            patch.object(root.logger, 'error') as mock_error, \
            patch.object(root.logger, 'debug') as mock_debug, \
            patch.object(root.logger, 'query') as mock_query, \
            patch.object(root.logger, 'con_open'), \
            patch.object(root.logger, 'con_close'):

            root.add_admin_user()

            mock_error.assert_any_call(f"Was not able to create admin account: Mocked MySQL failure")

def test_root_create_test_data():
    with app.app_context():
        root = Root()

        mock_result = []

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_result

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        with patch.object(root, 'create_connection', return_value=mock_connection), \
            patch.object(root.logger, 'info') as mock_info, \
            patch.object(root.logger, 'error') as mock_error, \
            patch.object(root.logger, 'debug') as mock_debug, \
            patch.object(root.logger, 'query') as mock_query, \
            patch.object(root.logger, 'con_open'), \
            patch.object(root.logger, 'con_close'):
            
            root.create_test_data()

            mock_cursor.execute.assert_any_call("Call clear_data();")
            mock_cursor.execute.assert_any_call("Call test_data();")
            mock_connection.commit.assert_called()

def test_root_create_test_data_exist():
    with app.app_context():
        root = Root()

        mock_result = [{"some data"}]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_result

        mock_connection = MagicMock()
        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        with patch.object(root, 'create_connection', return_value=mock_connection), \
            patch.object(root.logger, 'info') as mock_info, \
            patch.object(root.logger, 'error') as mock_error, \
            patch.object(root.logger, 'debug') as mock_debug, \
            patch.object(root.logger, 'query') as mock_query, \
            patch.object(root.logger, 'con_open'), \
            patch.object(root.logger, 'con_close'):
            
            root.create_test_data()

            mock_info.assert_any_call("Database already has data")
            mock_cursor.execute.called_once()

def test_root_create_test_data_mysql_error():
    with app.app_context():
        root = Root()

        with patch.object(root, 'create_connection', side_effect=MySQLError("Mocked MySQL failure")), \
            patch.object(root.logger, 'info') as mock_info, \
            patch.object(root.logger, 'error') as mock_error, \
            patch.object(root.logger, 'debug') as mock_debug, \
            patch.object(root.logger, 'query') as mock_query, \
            patch.object(root.logger, 'con_open'), \
            patch.object(root.logger, 'con_close'):
            
            root.create_test_data()

            mock_error.assert_any_call(f"Was not able to add test data: Mocked MySQL failure")

