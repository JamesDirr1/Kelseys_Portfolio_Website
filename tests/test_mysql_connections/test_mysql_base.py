import os
import sys
from unittest.mock import ANY, MagicMock, patch
import pytest
from pymysql import MySQLError, OperationalError
from app import app
from mysql_connections.mysql_base import MySQLBase

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# --------------------------------------------------------------------------
# Test base mysql class init
# --------------------------------------------------------------------------
@patch("mysql_connections.mysql_base.log")
@patch("mysql_connections.mysql_base.os.getenv")
def test_base_init(mock_getenv, mock_logger):
    env_values = {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3307",
        "MYSQL_DB": "portfolio_db",
    }

    mock_getenv.side_effect = lambda key, default=None: env_values.get(key, default)
    mock_logger_instance = mock_logger.return_value

    base_mysql = MySQLBase("test", "password", "TEST")

    assert base_mysql.host == "localhost"
    assert base_mysql.port == 3307
    assert base_mysql.user == "test"
    assert base_mysql.password == "password"
    assert base_mysql.db == "portfolio_db"
    assert base_mysql.logger == mock_logger_instance
    mock_logger.assert_called_once_with("TEST")


@patch("mysql_connections.mysql_base.log")
@patch("mysql_connections.mysql_base.os.getenv")
def test_base_init_with_defaults(mock_getenv, mock_logger):
    env_values = {
        "MYSQL_HOST": "localhost",
        "MYSQL_DB": "portfolio_db",
    }

    mock_getenv.side_effect = lambda key, default=None: env_values.get(key, default)
    mock_logger_instance = mock_logger.return_value

    base_mysql = MySQLBase("default", "password", "TEST")

    assert base_mysql.host == "localhost"
    assert base_mysql.port == 3306
    assert base_mysql.user == "default"
    assert base_mysql.password == "password"
    assert base_mysql.db == "portfolio_db"
    assert base_mysql.logger == mock_logger_instance
    mock_logger.assert_called_once_with("TEST")


# --------------------------------------------------------------------------
# Test connection creation
# --------------------------------------------------------------------------
def test_mysql_base_create_connection_success():
    with app.app_context():
        base_mysql = MySQLBase("test_user", "test_password", "test_db")

        mock_connection = MagicMock()

        with patch(
            "mysql_connections.mysql_base.pymysql.connect",
            return_value=mock_connection,
        ) as mock_connect, patch.object(
            base_mysql.logger, "debug"
        ) as mock_debug_logger, patch.object(
            base_mysql.logger, "error"
        ) as mock_error_logger:

            connection = base_mysql.create_connection()

            mock_connect.assert_called_once_with(
                host=base_mysql.host,
                port=base_mysql.port,
                user=base_mysql.user,
                password=base_mysql.password,
                database=base_mysql.db,
                cursorclass=ANY,
            )

            assert connection == mock_connection
            mock_debug_logger.assert_any_call(
                f"Creating connection to: {base_mysql.host}"
            )
            mock_debug_logger.assert_any_call("Connection created")
            mock_error_logger.assert_not_called()


def test_mysql_base_create_connection_mysql_error():
    with app.app_context():
        base_mysql = MySQLBase("test_user", "test_password", "test_db")

        with patch(
            "mysql_connections.mysql_base.pymysql.connect",
            side_effect=MySQLError("Mocked MySQL failure"),
        ), patch.object(base_mysql.logger, "error") as mock_error_logger:

            with pytest.raises(MySQLError):
                base_mysql.create_connection()

            mock_error_logger.assert_called_with(
                "Connection failed, could not create connection: Mocked MySQL failure"
            )

def test_mysql_base_create_connection_operational_error():
    with app.app_context():
        base_mysql = MySQLBase("test_user", "test_password", "test_db")

        with patch(
            "mysql_connections.mysql_base.pymysql.connect",
            side_effect=OperationalError("Mocked MySQL failure"),
        ), patch.object(base_mysql.logger, "error") as mock_error_logger:

            with pytest.raises(OperationalError):
                base_mysql.create_connection()

            mock_error_logger.assert_called_with(
                "Operational error when connecting to the database: Mocked MySQL failure"
            )


def test_mysql_base_create_connection_exception():
    with app.app_context():
        base_mysql = MySQLBase("test_user", "test_password", "test_db")

        with patch(
            "mysql_connections.mysql_base.pymysql.connect",
            side_effect=RuntimeError("Mocked failure"),
        ), patch.object(base_mysql.logger, "error") as mock_error_logger:

            with pytest.raises(Exception):
                base_mysql.create_connection()

            mock_error_logger.assert_called_with(
                "Unexpected error, could not create connection: Mocked failure"
            )


# --------------------------------------------------------------------------
# Test run query
# --------------------------------------------------------------------------


def test_mysql_base_run_query_fetch_none_args_none(mock_db):
    with app.app_context():
        mock_connection, mock_cursor = mock_db
        mock_cursor.rowcount = 4
        query = "Call someFunction;"
        args = None
        fetch = None

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(return_value=mock_connection)

        results = base_mysql._run_query(query, args, fetch)

        assert results == 4
        mock_cursor.execute.assert_called_once_with(query)
        mock_connection.commit.assert_called_once()


def test_mysql_base_run_query_fetch_none_with_args(mock_db):
    with app.app_context():
        mock_connection, mock_cursor = mock_db
        mock_cursor.rowcount = 1
        query = "INSERT INTO `someTable` (id, value) VALUES (%s,%s)"
        args = ["1", "test"]
        fetch = None

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(return_value=mock_connection)

        results = base_mysql._run_query(query, args, fetch)

        assert results == 1
        mock_cursor.execute.assert_called_once_with(query, args)
        mock_connection.commit.assert_called_once()


def test_mysql_base_run_query_fetch_one_with_args(mock_db):
    with app.app_context():
        mock_connection, mock_cursor = mock_db
        mock_cursor.fetchone.return_value = {"user_name": "TestUser"}
        query = "Select user_name FROM `users` WHERE user_name = %s;"
        args = ["TestUser"]
        fetch = "one"

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(return_value=mock_connection)

        results = base_mysql._run_query(query, args, fetch)

        assert results == {"user_name": "TestUser"}
        mock_cursor.execute.assert_called_once_with(query, args)
        mock_connection.commit.assert_not_called()


def test_mysql_base_run_query_fetch_one_args_none(mock_db):
    with app.app_context():
        mock_connection, mock_cursor = mock_db
        mock_cursor.fetchone.return_value = {"user_name": "TestUser"}
        query = "Select user_name FROM `users`"
        args = None
        fetch = "one"

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(return_value=mock_connection)

        results = base_mysql._run_query(query, args, fetch)

        assert results == {"user_name": "TestUser"}
        mock_cursor.execute.assert_called_once_with(query)
        mock_connection.commit.assert_not_called()


def test_mysql_base_run_query_fetch_all_args_none(mock_db):
    with app.app_context():
        mock_connection, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = {
            "user_name": "TestUser",
            "user_name": "TestUser2",
        }
        query = "Select user_name FROM `users`"
        args = None
        fetch = "all"

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(return_value=mock_connection)

        results = base_mysql._run_query(query, args, fetch)

        assert results == {"user_name": "TestUser", "user_name": "TestUser2"}
        mock_cursor.execute.assert_called_once_with(query)
        mock_connection.commit.assert_not_called()


def test_mysql_base_run_query_fetch_all_with_args(mock_db):
    with app.app_context():
        mock_connection, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = {
            "user_name": "TestUser",
            "user_name": "TestUser2",
        }
        query = "Select user_name FROM `users` WHERE user_name like %s;"
        args = "%Test%"
        fetch = "all"

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(return_value=mock_connection)

        results = base_mysql._run_query(query, args, fetch)

        assert results == {"user_name": "TestUser", "user_name": "TestUser2"}
        mock_cursor.execute.assert_called_once_with(query, args)
        mock_connection.commit.assert_not_called()


def test_mysql_base_run_query_value_error(mock_db):
    with app.app_context():
        mock_connection, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = {
            "user_name": "TestUser",
            "user_name": "TestUser2",
        }
        query = "Select user_name FROM `users` WHERE user_name like %s;"
        args = "%Test%"
        fetch = "not_valid"

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(return_value=mock_connection)

        with pytest.raises(ValueError):
            base_mysql._run_query(query, args, fetch)
        mock_cursor.execute.assert_not_called()
        mock_connection.commit.assert_not_called()


def test_mysql_base_run_query_operational_error(mock_db):
    with app.app_context():
        _, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = {
            "user_name": "TestUser",
            "user_name": "TestUser2",
        }
        query = "Select user_name FROM `users` WHERE user_name like %s;"
        args = "%Test%"
        fetch = "all"

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(side_effect=OperationalError)
        base_mysql.logger.error = MagicMock()

        with pytest.raises(OperationalError):
            base_mysql._run_query(query, args, fetch)
        base_mysql.logger.error.assert_called_once()


def test_mysql_base_run_query_mysql_error(mock_db):
    with app.app_context():
        _, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = {
            "user_name": "TestUser",
            "user_name": "TestUser2",
        }
        query = "Select user_name FROM `users` WHERE user_name like %s;"
        args = "%Test%"
        fetch = "all"

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(side_effect=MySQLError)
        base_mysql.logger.error = MagicMock()

        with pytest.raises(MySQLError):
            base_mysql._run_query(query, args, fetch)
        base_mysql.logger.error.assert_called_once()


def test_mysql_base_run_query_Exception(mock_db):
    with app.app_context():
        _, mock_cursor = mock_db
        mock_cursor.fetchall.return_value = {
            "user_name": "TestUser",
            "user_name": "TestUser2",
        }
        query = "Select user_name FROM `users` WHERE user_name like %s;"
        args = "%Test%"
        fetch = "all"

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(side_effect=KeyError)
        base_mysql.logger.error = MagicMock()

        with pytest.raises(Exception):
            base_mysql._run_query(query, args, fetch)
        base_mysql.logger.error.assert_called_once()


def test_mysql_base_run_query_connection_always_closes(mock_db):
    with app.app_context():
        mock_connection, mock_cursor = mock_db
        mock_cursor.fetchall.side_effect = MySQLError()
        query = "Select user_name FROM `users` WHERE user_name like %s;"
        args = "%Test%"
        fetch = "all"

        base_mysql = MySQLBase("user", "password", "TEST")
        base_mysql.create_connection = MagicMock(return_value=mock_connection)
        base_mysql.logger.error = MagicMock()

        with pytest.raises(MySQLError):
            base_mysql._run_query(query, args, fetch)
        base_mysql.logger.error.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()


# --------------------------------------------------------------------------
# Test fetch all
# --------------------------------------------------------------------------
def test_mysql_base_fetch_all_success():
    with app.app_context():
        query = "SELECT * FROM test_table;"
        expected_results = [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        results = base_mysql.fetch_all(query)

        assert results == [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
        base_mysql._run_query.assert_called_once_with(query, None, "all")


def test_base_mysql_fetch_all_success_with_args():
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = [{"id": 1, "name": "foo"}, {"id": 2, "name": "foobar"}]
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        results = base_mysql.fetch_all(query, ["foo"])

        assert results == [{"id": 1, "name": "foo"}, {"id": 2, "name": "foobar"}]
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "all")


def test_base_mysql_fetch_all_empty_result():
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = []
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        results = base_mysql.fetch_all(query, ["foo"])

        assert results is None
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "all")


def test_base_mysql_fetch_all_mysql_error():
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger.error = MagicMock()

        base_mysql._run_query = MagicMock(side_effect=OperationalError)

        with pytest.raises(MySQLError):
            base_mysql.fetch_all(query, ["foo"])

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "all")


def test_base_mysql_fetch_all_general_error():
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger.error = MagicMock()

        base_mysql._run_query = MagicMock(side_effect=RuntimeError)

        with pytest.raises(Exception):
            base_mysql.fetch_all(query, ["foo"])

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "all")


# --------------------------------------------------------------------------
# Test fetch all sensitive
# ---------------------------------------------------------------------------
def test_mysql_base_fetch_all_sensitive_success_with_args(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = [{"id": 1, "name": "foo"}, {"id": 2, "name": "foobar"}]
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        with caplog.at_level("DEBUG"):
            results = base_mysql.fetch_all_sensitive(query, ["foo"])

        logs = " ".join(r.message for r in caplog.records)

        assert results == [{"id": 1, "name": "foo"}, {"id": 2, "name": "foobar"}]
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "all")
        assert "[REDACTED]" in logs
        assert "[foo]" not in logs
        assert str(expected_results) not in logs


def test_base_mysql_fetch_all_sensitive_success(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table;"
        expected_results = [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        with caplog.at_level("DEBUG"):
            results = base_mysql.fetch_all_sensitive(query)

        logs = " ".join(r.message for r in caplog.records)

        assert results == [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
        base_mysql._run_query.assert_called_once_with(query, None, "all")
        assert "[REDACTED]" in logs
        assert str(expected_results) not in logs


def test_base_mysql_fetch_all_sensitive_empty_result(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = []
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        with caplog.at_level("DEBUG"):
            results = base_mysql.fetch_all_sensitive(query, ["foo"])

        logs = " ".join(r.message for r in caplog.records)
        assert results == None
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "all")
        assert "[REDACTED]" in logs
        assert "[foo]" not in logs
        assert str(expected_results) not in logs


def test_base_mysql_fetch_all_sensitive_mysql_error(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(side_effect=OperationalError)

        with caplog.at_level("DEBUG"):
            with pytest.raises(MySQLError):
                base_mysql.fetch_all_sensitive(query, ["foo"])

        logs = " ".join(r.message for r in caplog.records)

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "all")
        assert "[foo]" not in logs
        assert str(expected_results) not in logs


def test_base_mysql_fetch_all_sensitive_general_error(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(side_effect=RuntimeError)

        with caplog.at_level("DEBUG"):
            with pytest.raises(Exception):
                base_mysql.fetch_all_sensitive(query, ["foo"])

        logs = " ".join(r.message for r in caplog.records)

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "all")
        assert "[foo]" not in logs
        assert str(expected_results) not in logs


# --------------------------------------------------------------------------
# Test fetch one
# ---------------------------------------------------------------------------
def test_mysql_base_fetch_one_success():
    with app.app_context():
        query = "SELECT * FROM test_table;"
        expected_results = {"id": 1, "name": "foo"}
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        results = base_mysql.fetch_one(query)

        assert results == {"id": 1, "name": "foo"}
        base_mysql._run_query.assert_called_once_with(query, None, "one")


def test_mysql_base_fetch_one_success_with_args():
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name = %s;"
        expected_results = {"id": 1, "name": "foo"}
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        results = base_mysql.fetch_one(query, ["foo"])

        assert results == {"id": 1, "name": "foo"}
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "one")


def test_mysql_base_fetch_one_success_empty_result():
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name = %s;"
        expected_results = {}
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        results = base_mysql.fetch_one(query, ["foo"])

        assert results is None
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "one")


def test_mysql_base_fetch_one_mysql_error():
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger.error = MagicMock()

        base_mysql._run_query = MagicMock(side_effect=OperationalError)

        with pytest.raises(MySQLError):
            base_mysql.fetch_one(query, ["foo"])

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "one")

def test_base_mysql_fetch_one_general_error():
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger.error = MagicMock()

        base_mysql._run_query = MagicMock(side_effect=RuntimeError)

        with pytest.raises(Exception):
            base_mysql.fetch_one(query, ["foo"])

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "one")

# --------------------------------------------------------------------------
# Test fetch one sensitive
# ---------------------------------------------------------------------------
def test_mysql_base_fetch_one_sensitive_success_with_args(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = {"id": 1, "name": "foo"}
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        with caplog.at_level("DEBUG"):
            results = base_mysql.fetch_one_sensitive(query, ["foo"])

        logs = " ".join(r.message for r in caplog.records)

        assert results == {"id": 1, "name": "foo"}
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "one")
        assert "[REDACTED]" in logs
        assert "[foo]" not in logs
        assert str(expected_results) not in logs


def test_base_mysql_fetch_one_sensitive_success(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table;"
        expected_results = {"id": 1, "name": "foo"}
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        with caplog.at_level("DEBUG"):
            results = base_mysql.fetch_one_sensitive(query)

        logs = " ".join(r.message for r in caplog.records)

        assert results == {"id": 1, "name": "foo"}
        base_mysql._run_query.assert_called_once_with(query, None, "one")
        assert "[REDACTED]" in logs
        assert str(expected_results) not in logs


def test_base_mysql_fetch_one_sensitive_empty_result(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = {}
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value=expected_results)

        with caplog.at_level("DEBUG"):
            results = base_mysql.fetch_one_sensitive(query, ["foo"])

        logs = " ".join(r.message for r in caplog.records)
        assert results == None
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "one")
        assert "[REDACTED]" in logs
        assert "[foo]" not in logs
        assert str(expected_results) not in logs


def test_base_mysql_fetch_one_sensitive_mysql_error(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = {"id": 1, "name": "foo"}
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(side_effect=OperationalError)

        with caplog.at_level("DEBUG"):
            with pytest.raises(MySQLError):
                base_mysql.fetch_one_sensitive(query, ["foo"])

        logs = " ".join(r.message for r in caplog.records)

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "one")
        assert "[foo]" not in logs
        assert str(expected_results) not in logs


def test_base_mysql_fetch_one_sensitive_general_error(caplog):
    with app.app_context():
        query = "SELECT * FROM test_table WHERE name LIKE %s;"
        expected_results = {"id": 1, "name": "foo"}
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(side_effect=RuntimeError)

        with caplog.at_level("DEBUG"):
            with pytest.raises(Exception):
                base_mysql.fetch_one_sensitive(query, ["foo"])

        logs = " ".join(r.message for r in caplog.records)

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, ["foo"], "one")
        assert "[foo]" not in logs
        assert str(expected_results) not in logs


# --------------------------------------------------------------------------
# Test execute
# ---------------------------------------------------------------------------
def test_mysql_base_execute_success():
    with app.app_context():
        query = "Call some_function;"
        expected_row = 1
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(return_value = expected_row)

        base_mysql.execute(query)

        base_mysql.logger.query.assert_called_once_with(query, None, f"{expected_row} rows affected")
        base_mysql._run_query.assert_called_once_with(query, None, None)

def test_mysql_base_execute_success_with_args():
    with app.app_context():
        query = "INSERT INTO `someTable` (id, value) VALUES (%s,%s)"
        args = [1, "test"]
        expected_row = 1
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(return_value = expected_row)

        base_mysql.execute(query, args)

        base_mysql.logger.query.assert_called_once_with(query, args, f"{expected_row} rows affected")
        base_mysql._run_query.assert_called_once_with(query, args, None)

def test_mysql_base_execute_mysql_error():
    with app.app_context():
        query = "Call some_function;"
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(side_effect = MySQLError)
        
        with pytest.raises(MySQLError):
            base_mysql.execute(query)

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, None, None)

def test_mysql_base_execute_general_error():
    with app.app_context():
        query = "Call some_function;"
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(side_effect = ValueError)
        
        with pytest.raises(Exception):
            base_mysql.execute(query)

        base_mysql.logger.error.assert_called_once()
        base_mysql._run_query.assert_called_once_with(query, None, None)
        
# --------------------------------------------------------------------------
# Test execute sensitive
# ---------------------------------------------------------------------------
def test_mysql_base_execute_sensitive_success(caplog):
    with app.app_context():
        query = "Call some_function;"
        expected_row = 1
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value = expected_row)
        with caplog.at_level("DEBUG"):
            base_mysql.execute_sensitive(query)

        logs = " ".join(r.message for r in caplog.records)
        
        assert "None" not in logs
        assert "[Redacted]" in logs
        base_mysql._run_query.assert_called_once_with(query, None, None)

def test_mysql_base_execute_sensitive_success_with_args(caplog):
    with app.app_context():
        query = "INSERT INTO `someTable` (id, value) VALUES (%s,%s)"
        args = [2, "cat"]
        expected_row = 1
        base_mysql = MySQLBase("default", "password", "TEST")

        base_mysql._run_query = MagicMock(return_value = expected_row)
        
        with caplog.at_level("DEBUG"):
            base_mysql.execute_sensitive(query, args)

        logs = " ".join(r.message for r in caplog.records)
        
        for arg in args:
            assert f"{arg}" not in logs
        assert "[Redacted]" in logs
        base_mysql._run_query.assert_called_once_with(query, args, None)

def test_mysql_base_execute_sensitive_mysql_error(caplog):
    with app.app_context():
        query = "Call some_function;"
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(side_effect = MySQLError)

        with caplog.at_level("DEBUG"):
            with pytest.raises(MySQLError):
                base_mysql.execute_sensitive(query)

        logs = " ".join(r.message for r in caplog.records)

        assert "None" not in logs
        base_mysql._run_query.assert_called_once_with(query, None, None)

def test_mysql_base_execute_sensitive_general_error(caplog):
    with app.app_context():
        query = "Call some_function;"
        base_mysql = MySQLBase("default", "password", "TEST")
        base_mysql.logger = MagicMock()

        base_mysql._run_query = MagicMock(side_effect = ValueError)
        
        with caplog.at_level("DEBUG"):
            with pytest.raises(Exception):
                base_mysql.execute_sensitive(query)

        logs = " ".join(r.message for r in caplog.records)

        assert "None" not in logs
        base_mysql._run_query.assert_called_once_with(query, None, None)