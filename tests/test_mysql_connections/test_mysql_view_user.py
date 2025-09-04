import os
import sys
import time
from unittest.mock import ANY, MagicMock, patch

import pymysql
import pytest
from pymysql import MySQLError

from app import app, category_list, database_setup
from data_classes.category import Category
from mysql_connections.mysql_view_user import View_User

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# MySQL connection testing
@patch("mysql_connections.mysql_view_user.utility_classes.custom_logger.log")
@patch("mysql_connections.mysql_view_user.os.getenv")
def test_view_user_init(mock_getenv, mock_logger):

    env_values = {
        "MYSQL_HOST": "localhost",
        "MYSQL_PORT": "3307",
        "MYSQL_VIEW_USER": "view_user",
        "MYSQL_VIEW_USER_PASSWORD": "secret123",
        "MYSQL_DB": "portfolio_db",
    }

    mock_getenv.side_effect = lambda key, default=None: env_values.get(key, default)

    mock_logger_instance = mock_logger.return_value

    real_view_user = View_User()

    assert real_view_user.host == "localhost"
    assert real_view_user.port == 3307
    assert real_view_user.user == "view_user"
    assert real_view_user.password == "secret123"
    assert real_view_user.db == "portfolio_db"
    assert real_view_user.logger == mock_logger_instance
    mock_logger.assert_called_once_with("VIEW_USER")


def test_view_user_create_connection_success():
    with app.app_context():
        view_user = View_User()

        mock_connection = MagicMock()
        with patch(
            "mysql_connections.mysql_view_user.pymysql.connect",
            return_value=mock_connection,
        ) as mock_connect, patch.object(
            view_user.logger, "info"
        ) as mock_info_logger, patch.object(
            view_user.logger, "error"
        ) as mock_error_logger:

            connection = view_user.create_connection()

            mock_connect.assert_called_once_with(
                host=view_user.host,
                port=view_user.port,
                user=view_user.user,
                password=view_user.password,
                database=view_user.db,
                cursorclass=ANY,
            )

            assert connection == mock_connection
            mock_info_logger.assert_any_call(
                f"Creating connection to: {view_user.host}"
            )
            mock_info_logger.assert_any_call("Connection created")
            mock_error_logger.assert_not_called()


def test_view_user_create_connection_mysql_error():
    with app.app_context():
        view_user = View_User()

        with patch(
            "mysql_connections.mysql_view_user.pymysql.connect",
            side_effect=MySQLError("Mocked MySQL failure"),
        ), patch.object(view_user.logger, "error") as mock_error_logger:

            with pytest.raises(MySQLError):
                view_user.create_connection()

            mock_error_logger.assert_called_with(
                "Connection failed, could not create connection: Mocked MySQL failure"
            )


def test_view_user_create_connection_general_error():
    with app.app_context():
        view_user = View_User()

        with patch(
            "mysql_connections.mysql_view_user.pymysql.connect",
            side_effect=RuntimeError("Mocked failure"),
        ), patch.object(view_user.logger, "error") as mock_error_logger:

            with pytest.raises(RuntimeError):
                view_user.create_connection()

            mock_error_logger.assert_called_with(
                "Unexpected error, could not create connection: Mocked failure"
            )


# Mysql query testing
def test_view_user_fetch_all_success():
    with app.app_context():
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]

        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        view_user = View_User()
        view_user.create_connection = MagicMock(return_value=mock_connection)
        view_user.logger = MagicMock()

        results = view_user.fetch_all("SELECT * FROM test_table")

        assert results == [{"id": 1, "name": "test"}]
        view_user.logger.debug.assert_any_call("args are null")
        mock_cursor.execute.assert_called_once()
        view_user.logger.debug.assert_any_call("Results: [{'id': 1, 'name': 'test'}]")


def test_view_user_fetch_all_success_with_args():
    with app.app_context():
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [{"id": 1, "name": "test"}]

        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        view_user = View_User()
        view_user.create_connection = MagicMock(return_value=mock_connection)
        view_user.logger = MagicMock()

        results = view_user.fetch_all(
            "SELECT * FROM test_table WHERE name Like %s;", "test"
        )

        assert results == [{"id": 1, "name": "test"}]
        view_user.logger.debug.assert_any_call("args: test")
        mock_cursor.execute.assert_called_once()
        view_user.logger.debug.assert_any_call("Results: [{'id': 1, 'name': 'test'}]")


def test_view_user_fetch_all_empty_result():
    with app.app_context():
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []

        mock_connection.cursor.return_value.__enter__.return_value = mock_cursor

        view_user = View_User()
        view_user.create_connection = MagicMock(return_value=mock_connection)
        view_user.logger = MagicMock()

        results = view_user.fetch_all("SELECT * FROM test_table")

        assert results == None
        mock_cursor.execute.assert_called_once()
        view_user.logger.debug.assert_any_call("Results: None")


def test_view_user_fetch_all_mysql_error():
    with app.app_context():
        view_user = View_User()

        with patch.object(
            view_user,
            "create_connection",
            side_effect=MySQLError("Mocked MySQL failure"),
        ), patch.object(view_user.logger, "info"), patch.object(
            view_user.logger, "error"
        ) as mock_error, patch.object(
            view_user.logger, "debug"
        ), patch.object(
            view_user.logger, "query"
        ), patch.object(
            view_user.logger, "con_open"
        ), patch.object(
            view_user.logger, "con_close"
        ):

            with pytest.raises(MySQLError):
                view_user.fetch_all("bad query")

            mock_error.assert_called_once()
            logged_message = mock_error.call_args[0][0]
            assert (
                "Unable to complete: bad query. MySQL error: Mocked MySQL failure"
                in logged_message
            )


def test_view_user_fetch_all_general_error():
    with app.app_context():
        view_user = View_User()

        with patch.object(
            view_user, "create_connection", side_effect=RuntimeError("Mocked failure")
        ), patch.object(view_user.logger, "info"), patch.object(
            view_user.logger, "error"
        ) as mock_error, patch.object(
            view_user.logger, "debug"
        ), patch.object(
            view_user.logger, "query"
        ), patch.object(
            view_user.logger, "con_open"
        ), patch.object(
            view_user.logger, "con_close"
        ):

            with pytest.raises(RuntimeError):
                view_user.fetch_all("bad query")

            mock_error.assert_called_once()
            logged_message = mock_error.call_args[0][0]
            assert (
                "Unexpected error when fetching data from the database: Mocked failure"
                in logged_message
            )


# Get all categories testing
def test_view_user_get_all_categories():
    with app.app_context():
        mock_result = [
            {"category_id": 1, "category_title": "Illustration", "category_order": 1},
            {"category_id": 2, "category_title": "Design", "category_order": 2},
            {"category_id": 3, "category_title": "Comics", "category_order": 3},
        ]
        mock_category = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.category.Category.from_dict", return_value=mock_category
        ) as mock_from_dict:
            result = view_user.get_all_categories()
            assert mock_from_dict.call_count == 3
            assert result == [mock_category, mock_category, mock_category]
            view_user.logger.info.assert_any_call("Getting all categories - Sorted")


def test_view_user_get_all_categories_return_none():
    with app.app_context():
        mock_result = None
        mock_category = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.category.Category.from_dict", return_value=mock_category
        ) as mock_from_dict:
            result = view_user.get_all_categories(False)
            assert mock_from_dict.call_count == 0
            assert result == []
            view_user.logger.info.assert_any_call("Getting all categories")


def test_view_user_get_all_categories_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {"category_id": 1, "category_title": "Illustration", "category_order": "1"},
            {"category_id": 2, "category_title": "Design", "category_order": "bad"},
            {"category_id": 3, "category_title": "Comics", "category_order": "3"},
        ]

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        def mock_from_dict(data):
            if data["category_order"] == "bad":
                raise ValueError("Invalid category_order")
            return f"Category-{data['category_id']}"

        with patch(
            "data_classes.category.Category.from_dict",
            side_effect=mock_from_dict,
        ):
            result = view_user.get_all_categories()
            assert result == ["Category-1", "Category-3"]
            view_user.logger.error.assert_any_call(
                "Failed to create category from {'category_id': 2, 'category_title': 'Design', 'category_order': 'bad'} -> Invalid category_order"
            )


def test_view_user_get_all_categories_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception) as exc_info:
            view_user.get_all_categories()
        assert "Failed to get categories" in str(exc_info.value)
        view_user.logger.error.assert_any_call(
            "Failed to get categories: Database error"
        )


# Get category by title testing
def test_view_user_get_category_by_title():
    with app.app_context():
        mock_result = [
            {"category_id": 1, "category_title": "Illustration", "category_order": 1}
        ]
        mock_category = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.category.Category.from_dict", return_value=mock_category
        ) as mock_from_dict:
            result = view_user.get_category_by_title("Illustration")
            assert mock_from_dict.call_count == 1
            assert result == mock_category
            view_user.logger.info.assert_any_call("Getting category by Illustration")


def test_view_user_get_category_by_title_return_none():
    with app.app_context():
        mock_result = None
        mock_category = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.category.Category.from_dict", return_value=mock_category
        ) as mock_from_dict:
            result = view_user.get_category_by_title("Design")
            assert mock_from_dict.call_count == 0
            assert result is None
            view_user.logger.info.assert_any_call("Getting category by Design")


def test_view_user_get_category_by_title_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {
                "category_id": 1,
                "category_title": "Illustration",
                "category_order": "bad",
            }
        ]

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.category.Category.from_dict",
            side_effect=ValueError("bad data"),
        ):
            result = view_user.get_category_by_title("Illustration")
            view_user.logger.error.assert_any_call(
                "Failed to create category from {'category_id': 1, 'category_title': 'Illustration', 'category_order': 'bad'}: bad data"
            )
            assert result is None


def test_view_user_get_category_by_title_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception) as exc_info:
            view_user.get_category_by_title("Illustration")
        assert "Failed to get category 'Illustration': Database error" in str(
            exc_info.value
        )


# Get all projects testing
def test_view_user_get_all_projects():
    with app.app_context():
        mock_result = [
            {
                "image_id": 2,
                "image_title": "title",
                "image_desc": "desc",
                "image_URL": "some_link.com",
                "image_weight": 2,
                "project_id": 2,
            },
            {
                "image_id": 1,
                "image_title": "Title2",
                "image_desc": "desc2",
                "image_URL": "some_link2.com",
                "image_weight": 1,
                "project_id": 1,
            },
        ]
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_all_projects()
            assert mock_from_dict.call_count == 2
            assert result == [mock_project, mock_project]
            view_user.logger.info.assert_any_call("Getting all projects")


def test_view_user_get_all_projects_return_none():
    with app.app_context():
        mock_result = None
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_all_projects()
            assert mock_from_dict.call_count == 0
            assert result == []
            view_user.logger.info.assert_any_call("Getting all projects")


def test_view_user_get_all_projects_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {
                "image_id": 2,
                "image_title": "title",
                "image_desc": "desc",
                "image_URL": "some_link.com",
                "image_weight": 2,
                "project_id": 2,
            },
            {
                "image_id": 1,
                "image_title": "Title2",
                "image_desc": "desc2",
                "image_URL": "some_link2.com",
                "image_weight": 1,
                "project_id": 1,
            },
            {
                "image_id": 1,
                "image_title": "Title3",
                "image_desc": "desc3",
                "image_URL": "some_link3.com",
                "image_weight": 1,
                "project_id": "bad",
            },
        ]

        def mock_from_dict(data):
            if data["project_id"] == "bad":
                raise ValueError("Invalid project_id")
            return f"Project-{data['project_id']}"

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()
        with patch(
            "data_classes.project.Project.from_dict", side_effect=mock_from_dict
        ):
            result = view_user.get_all_projects()
            assert result == ["Project-2", "Project-1"]
            view_user.logger.error.assert_any_call(
                "Failed to create project from {'image_id': 1, 'image_title': 'Title3', 'image_desc': 'desc3', 'image_URL': 'some_link3.com', 'image_weight': 1, 'project_id': 'bad'}: Invalid project_id"
            )


def test_view_user_get_all_projects_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception) as exc_info:
            view_user.get_all_projects()
        assert "Failed to get all projects: Database error" in str(exc_info.value)


# Get project by category id testing
def test_view_user_get_project_by_category():
    with app.app_context():
        mock_result = [
            {
                "project_id": 1,
                "project_title": "project 1",
                "project_date": "date",
                "project_desc": "Desc 1",
                "category_id": 1,
                "project_image_id": 1,
                "image_id": 1,
                "image_title": "image title",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image.project_id": 1,
            },
            {
                "project_id": 2,
                "project_title": "project 2",
                "project_date": "date",
                "project_desc": "Desc 2",
                "category_id": 1,
                "project_image_id": 2,
                "image_id": 2,
                "image_title": "image title 2",
                "image_desc": None,
                "image_URL": "some_link2.com",
                "image.project_id": 2,
            },
            {
                "project_id": 3,
                "project_title": "project 3",
                "project_date": "date",
                "project_desc": "Desc 3",
                "category_id": 1,
                "project_image_id": 3,
                "image_id": 3,
                "image_title": "image title 3",
                "image_desc": None,
                "image_URL": "some_link3.com",
                "image.project_id": 3,
            },
        ]
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_projects_by_category(1)
            assert mock_from_dict.call_count == 3
            assert result == [mock_project, mock_project, mock_project]
            view_user.logger.info.assert_any_call(
                "Getting all projects from category 1 - Sorted"
            )


def test_view_user_get_project_by_category_return_none():
    with app.app_context():
        mock_result = None
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_projects_by_category(20, False)
            assert result == []
            assert mock_from_dict.call_count == 0
            view_user.logger.info.assert_any_call(
                "Getting all projects from category 20"
            )


def test_view_user_get_project_by_category_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {
                "project_id": "bad",
                "project_title": "project 1",
                "project_date": "date",
                "project_desc": "Desc 1",
                "category_id": 1,
                "project_image_id": 1,
                "image_id": 1,
                "image_title": "image title",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image.project_id": 1,
            },
            {
                "project_id": 2,
                "project_title": "project 2",
                "project_date": "date",
                "project_desc": "Desc 2",
                "category_id": 1,
                "project_image_id": 2,
                "image_id": 2,
                "image_title": "image title 2",
                "image_desc": None,
                "image_URL": "some_link2.com",
                "image.project_id": 2,
            },
            {
                "project_id": 3,
                "project_title": "project 3",
                "project_date": "date",
                "project_desc": "Desc 3",
                "category_id": 1,
                "project_image_id": 3,
                "image_id": 3,
                "image_title": "image title 3",
                "image_desc": None,
                "image_URL": "some_link3.com",
                "image.project_id": 3,
            },
        ]

        def mock_from_dict(data):
            if data["project_id"] == "bad":
                raise ValueError("Invalid project_id")
            return f"Project-{data['project_id']}"

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", side_effect=mock_from_dict
        ):
            result = view_user.get_projects_by_category(1)
            assert result == ["Project-2", "Project-3"]
            view_user.logger.error.assert_any_call(
                "Failed to create project from {'project_id': 'bad', 'project_title': 'project 1', 'project_date': 'date', 'project_desc': 'Desc 1', 'category_id': 1, 'project_image_id': 1, 'image_id': 1, 'image_title': 'image title', 'image_desc': None, 'image_URL': 'some_link.com', 'image.project_id': 1}: Invalid project_id"
            )


def test_view_user_get_project_by_category_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception) as exc_info:
            view_user.get_projects_by_category(1)
        assert "Failed to get projects from category 1: Database error" in str(
            exc_info.value
        )


# Get project by category title testing
def test_view_user_get_project_by_category_title():
    with app.app_context():
        mock_result = [
            {
                "project_id": 1,
                "project_title": "project 1",
                "project_date": "date",
                "project_desc": "Desc 1",
                "category_id": 1,
                "project_image_id": 1,
                "image_id": 1,
                "image_title": "image title",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image.project_id": 1,
            },
            {
                "project_id": 2,
                "project_title": "project 2",
                "project_date": "date",
                "project_desc": "Desc 2",
                "category_id": 1,
                "project_image_id": 2,
                "image_id": 2,
                "image_title": "image title 2",
                "image_desc": None,
                "image_URL": "some_link2.com",
                "image.project_id": 2,
            },
            {
                "project_id": 3,
                "project_title": "project 3",
                "project_date": "date",
                "project_desc": "Desc 3",
                "category_id": 1,
                "project_image_id": 3,
                "image_id": 3,
                "image_title": "image title 3",
                "image_desc": None,
                "image_URL": "some_link3.com",
                "image.project_id": 3,
            },
        ]
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_projects_by_category_title("design")
            assert mock_from_dict.call_count == 3
            assert result == [mock_project, mock_project, mock_project]
            view_user.logger.info.assert_any_call(
                "Getting all projects from category 'design' - Sorted"
            )


def test_view_user_get_project_by_category_title_return_none():
    with app.app_context():
        mock_result = None
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_projects_by_category_title("design", False)
            assert result == []
            assert mock_from_dict.call_count == 0
            view_user.logger.info.assert_any_call(
                "Getting all projects from category 'design'"
            )


def test_view_user_get_project_by_category_title_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {
                "project_id": "bad",
                "project_title": "project 1",
                "project_date": "date",
                "project_desc": "Desc 1",
                "category_id": 1,
                "project_image_id": 1,
                "image_id": 1,
                "image_title": "image title",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image.project_id": 1,
            },
            {
                "project_id": 2,
                "project_title": "project 2",
                "project_date": "date",
                "project_desc": "Desc 2",
                "category_id": 1,
                "project_image_id": 2,
                "image_id": 2,
                "image_title": "image title 2",
                "image_desc": None,
                "image_URL": "some_link2.com",
                "image.project_id": 2,
            },
            {
                "project_id": 3,
                "project_title": "project 3",
                "project_date": "date",
                "project_desc": "Desc 3",
                "category_id": 1,
                "project_image_id": 3,
                "image_id": 3,
                "image_title": "image title 3",
                "image_desc": None,
                "image_URL": "some_link3.com",
                "image.project_id": 3,
            },
        ]

        def mock_from_dict(data):
            if data["project_id"] == "bad":
                raise ValueError("Invalid project_id")
            return f"Project-{data['project_id']}"

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", side_effect=mock_from_dict
        ):
            result = view_user.get_projects_by_category_title("design")
            assert result == ["Project-2", "Project-3"]
            view_user.logger.error.assert_any_call(
                "Failed to create project from {'project_id': 'bad', 'project_title': 'project 1', 'project_date': 'date', 'project_desc': 'Desc 1', 'category_id': 1, 'project_image_id': 1, 'image_id': 1, 'image_title': 'image title', 'image_desc': None, 'image_URL': 'some_link.com', 'image.project_id': 1}: Invalid project_id"
            )


def test_view_user_get_project_by_category_title_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception) as exc_info:
            view_user.get_projects_by_category_title("design")
        assert "Failed to get projects from category design: Database error" in str(
            exc_info.value
        )


# Get project by id testing
def test_view_user_get_project():
    with app.app_context():
        mock_result = [
            {
                "project_id": 1,
                "project_title": "project 1",
                "project_date": "date",
                "project_desc": "Desc 1",
                "category_id": 1,
                "project_image_id": 1,
                "image_id": 1,
                "image_title": "image title",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image.project_id": 1,
            }
        ]
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_project(1)
            assert mock_from_dict.call_count == 1
            assert result == mock_project
            view_user.logger.info.assert_any_call("Getting project by id 1")


def test_view_user_get_project_return_none():
    with app.app_context():
        mock_result = None
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_project(5)
            assert result == None
            assert mock_from_dict.call_count == 0
            view_user.logger.info.assert_any_call("Getting project by id 5")


def test_view_user_get_project_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {
                "project_id": "bad",
                "project_title": "project 1",
                "project_date": "date",
                "project_desc": "Desc 1",
                "category_id": 1,
                "project_image_id": 1,
                "image_id": 1,
                "image_title": "image title",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image.project_id": 1,
            }
        ]

        def mock_from_dict(data):
            if data["project_id"] == "bad":
                raise ValueError("Invalid project_id")
            return f"Project-{data['project_id']}"

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", side_effect=mock_from_dict
        ):
            result = view_user.get_project(1)
            assert result == None
            view_user.logger.error.assert_any_call(
                "Failed to create project from {'project_id': 'bad', 'project_title': 'project 1', 'project_date': 'date', 'project_desc': 'Desc 1', 'category_id': 1, 'project_image_id': 1, 'image_id': 1, 'image_title': 'image title', 'image_desc': None, 'image_URL': 'some_link.com', 'image.project_id': 1}: Invalid project_id"
            )


def test_view_user_get_project_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception) as exc_info:
            view_user.get_project(1)
        assert "Failed to get project by id 1: Database error" in str(exc_info.value)


# Get project by title testing
def test_view_user_get_project_by_title():
    with app.app_context():
        mock_result = [
            {
                "project_id": 1,
                "project_title": "project 1",
                "project_date": "date",
                "project_desc": "Desc 1",
                "category_id": 1,
                "project_image_id": 1,
                "image_id": 1,
                "image_title": "image title",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image.project_id": 1,
            }
        ]
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_project_by_title("project 1", "design")
            assert mock_from_dict.call_count == 1
            assert result == mock_project
            view_user.logger.info.assert_any_call(
                "Getting project: project 1  from category: design"
            )


def test_view_user_get_project_by_title_return_none():
    with app.app_context():
        mock_result = None
        mock_project = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", return_value=mock_project
        ) as mock_from_dict:
            result = view_user.get_project_by_title("project 7", "design")
            assert result == None
            assert mock_from_dict.call_count == 0
            view_user.logger.info.assert_any_call(
                "Getting project: project 7  from category: design"
            )


def test_view_user_get_project_by_title_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {
                "project_id": "bad",
                "project_title": "project 1",
                "project_date": "date",
                "project_desc": "Desc 1",
                "category_id": 1,
                "project_image_id": 1,
                "image_id": 1,
                "image_title": "image title",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image.project_id": 1,
            }
        ]

        def mock_from_dict(data):
            if data["project_id"] == "bad":
                raise ValueError("Invalid project_id")
            return f"Project-{data['project_id']}"

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.project.Project.from_dict", side_effect=mock_from_dict
        ):
            result = view_user.get_project_by_title("project 1", "design")
            assert result == None
            view_user.logger.error.assert_any_call(
                "Failed to create project from {'project_id': 'bad', 'project_title': 'project 1', 'project_date': 'date', 'project_desc': 'Desc 1', 'category_id': 1, 'project_image_id': 1, 'image_id': 1, 'image_title': 'image title', 'image_desc': None, 'image_URL': 'some_link.com', 'image.project_id': 1}: Invalid project_id"
            )


def test_view_user_get_project_by_title_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception) as exc_info:
            view_user.get_project_by_title("project 1", "design")
        assert (
            "Failed to get project project 1 in category design: Database error"
            in str(exc_info.value)
        )


# Get all images testing
def test_view_user_get_all_images():
    with app.app_context():
        mock_result = [
            {
                "image_id": 1,
                "image_title": "Image 1",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image_weight": 1,
                "project_id": 1,
            },
            {
                "image_id": 2,
                "image_title": "Image 2",
                "image_desc": "some desc2",
                "image_URL": "some_link2.com",
                "image_weight": 2,
                "project_id": 2,
            },
        ]
        mock_image = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.image.Image.from_dict", return_value=mock_image
        ) as mock_from_dict:
            result = view_user.get_all_images()
            assert mock_from_dict.call_count == 2
            assert result == [mock_image, mock_image]
            view_user.logger.info.assert_any_call("Getting all images")


def test_view_user_get_all_images_return_none():
    with app.app_context():
        mock_result = None
        mock_image = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.image.Image.from_dict", return_value=mock_image
        ) as mock_from_dict:
            result = view_user.get_all_images()
            assert mock_from_dict.call_count == 0
            assert result == []
            view_user.logger.info.assert_any_call("Getting all images")


def test_view_user_get_all_images_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {
                "image_id": "bad",
                "image_title": "Image 1",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image_weight": 1,
                "project_id": 1,
            },
            {
                "image_id": 2,
                "image_title": "Image 2",
                "image_desc": "some desc2",
                "image_URL": "some_link2.com",
                "image_weight": 2,
                "project_id": 2,
            },
        ]

        def mock_from_dict(data):
            if data["image_id"] == "bad":
                raise ValueError("Invalid image_id")
            return f"Image-{data['image_id']}"

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()
        with patch("data_classes.image.Image.from_dict", side_effect=mock_from_dict):
            result = view_user.get_all_images()
            assert result == ["Image-2"]
            view_user.logger.error.assert_any_call(
                "Failed to create image from {'image_id': 'bad', 'image_title': 'Image 1', 'image_desc': None, 'image_URL': 'some_link.com', 'image_weight': 1, 'project_id': 1}: Invalid image_id"
            )


def test_view_user_get_all_images_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception) as exc_info:
            view_user.get_all_images()
        assert "Failed to get all images: Database error" in str(exc_info.value)


# Get project images by id testing
def test_view_user_get_project_images():
    with app.app_context():
        mock_result = [
            {
                "image_id": 1,
                "image_title": "Image 1",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image_weight": 1,
                "project_id": 1,
            },
            {
                "image_id": 2,
                "image_title": "Image 2",
                "image_desc": "some desc2",
                "image_URL": "some_link2.com",
                "image_weight": 2,
                "project_id": 2,
            },
        ]
        mock_image = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.image.Image.from_dict", return_value=mock_image
        ) as mock_from_dict:
            result = view_user.get_project_images(1)
            assert mock_from_dict.call_count == 2
            assert result == [mock_image, mock_image]
            view_user.logger.info.assert_any_call("Getting all images for project id 1")


def test_view_user_get_project_images_return_none():
    with app.app_context():
        mock_result = None
        mock_image = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.image.Image.from_dict", return_value=mock_image
        ) as mock_from_dict:
            result = view_user.get_project_images(5)
            assert mock_from_dict.call_count == 0
            assert result == []
            view_user.logger.info.assert_any_call("Getting all images for project id 5")


def test_view_user_get_project_images_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {
                "image_id": "bad",
                "image_title": "Image 1",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image_weight": 1,
                "project_id": 1,
            },
            {
                "image_id": 2,
                "image_title": "Image 2",
                "image_desc": "some desc2",
                "image_URL": "some_link2.com",
                "image_weight": 2,
                "project_id": 2,
            },
        ]

        def mock_from_dict(data):
            if data["image_id"] == "bad":
                raise ValueError("Invalid image_id")
            return f"Image-{data['image_id']}"

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()
        with patch("data_classes.image.Image.from_dict", side_effect=mock_from_dict):
            result = view_user.get_project_images(1)
            assert result == ["Image-2"]
            view_user.logger.error.assert_any_call(
                "Failed to create image from {'image_id': 'bad', 'image_title': 'Image 1', 'image_desc': None, 'image_URL': 'some_link.com', 'image_weight': 1, 'project_id': 1}: Invalid image_id"
            )


def test_view_user_get_project_images_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception):
            view_user.get_project_images(1)
        view_user.logger.error.assert_any_call(
            "Failed to get all images by project id 1: Database error"
        )


# Get image by id testing
def test_view_user_get_image():
    with app.app_context():
        mock_result = [
            {
                "image_id": 1,
                "image_title": "Image 1",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image_weight": 1,
                "project_id": 1,
            }
        ]
        mock_image = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.image.Image.from_dict", return_value=mock_image
        ) as mock_from_dict:
            result = view_user.get_image(1)
            assert mock_from_dict.call_count == 1
            assert result == mock_image
            view_user.logger.info.assert_any_call("Getting image by id 1")


def test_view_user_get_image_return_none():
    with app.app_context():
        mock_result = None
        mock_image = MagicMock()

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()

        with patch(
            "data_classes.image.Image.from_dict", return_value=mock_image
        ) as mock_from_dict:
            result = view_user.get_image(5)
            assert mock_from_dict.call_count == 0
            assert result == None
            view_user.logger.info.assert_any_call("Getting image by id 5")


def test_view_user_get_image_failed_obj_creation():
    with app.app_context():
        mock_result = [
            {
                "image_id": "bad",
                "image_title": "Image 1",
                "image_desc": None,
                "image_URL": "some_link.com",
                "image_weight": 1,
                "project_id": 1,
            }
        ]

        def mock_from_dict(data):
            if data["image_id"] == "bad":
                raise ValueError("Invalid image_id")
            return f"Image-{data['image_id']}"

        view_user = View_User()
        view_user.fetch_all = MagicMock(return_value=mock_result)
        view_user.logger = MagicMock()
        with patch("data_classes.image.Image.from_dict", side_effect=mock_from_dict):
            result = view_user.get_image(1)
        assert result == None
        view_user.logger.error.assert_any_call(
            "Failed to create image from {'image_id': 'bad', 'image_title': 'Image 1', 'image_desc': None, 'image_URL': 'some_link.com', 'image_weight': 1, 'project_id': 1}: Invalid image_id"
        )


def test_view_user_get_image_failure():
    with app.app_context():
        view_user = View_User()
        view_user.fetch_all = MagicMock(side_effect=Exception("Database error"))
        view_user.logger = MagicMock()

        with pytest.raises(Exception) as exc_info:
            view_user.get_image(1)
        assert "Failed to get image by id 1: Database error" in str(exc_info.value)


# Check user name and password testing
def test_view_user_check_user_exist_and_password():
    with app.app_context():
        mock_result = [
            {
                "user_id": 1,
                "user_name": "Test-Admin",
                "user_password": "hashed password",
                "user_creation_time": "date",
            }
        ]

        view_user = View_User()
        mock_user_obj = MagicMock()
        mock_user_obj.user_name = "Test-Admin"
        mock_user_obj.user_password = "password"

        with patch.object(view_user, "create_connection"), patch.object(
            view_user, "logger"
        ), patch(
            "mysql_connections.mysql_view_user.User.from_dict",
            return_value=mock_user_obj,
        ), patch(
            "mysql_connections.mysql_view_user.check_password_hash", return_value=True
        ):
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = mock_result
            mock_conn = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            view_user.create_connection.return_value = mock_conn

            name_match, password_match = view_user.check_user_exist_and_password(
                "Test-Admin", "password"
            )

            assert name_match is True
            assert password_match is True
            mock_cursor.execute.assert_called_once()
            view_user.logger.info.assert_any_call(
                "Checking if username 'Test-Admin' exist"
            )


def test_view_user_check_user_exist_and_password_user_name_not_match():
    with app.app_context():
        mock_result = [
            {
                "user_id": 1,
                "user_name": "Test-Admin",
                "user_password": "hashed password",
                "user_creation_time": "date",
            }
        ]

        view_user = View_User()
        mock_user_obj = MagicMock()
        mock_user_obj.user_name = "test-Admin"
        mock_user_obj.user_password = "password"

        with patch.object(view_user, "create_connection"), patch.object(
            view_user, "logger"
        ), patch(
            "mysql_connections.mysql_view_user.User.from_dict",
            return_value=mock_user_obj,
        ), patch(
            "mysql_connections.mysql_view_user.check_password_hash", return_value=True
        ):
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = mock_result
            mock_conn = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            view_user.create_connection.return_value = mock_conn

            name_match, password_match = view_user.check_user_exist_and_password(
                "Test-Admin", "password"
            )

            assert name_match is False
            assert password_match is False
            mock_cursor.execute.assert_called_once()
            view_user.logger.info.assert_any_call(
                "Checking if username 'Test-Admin' exist"
            )


def test_view_user_check_user_exist_and_password_password_not_match():
    with app.app_context():
        mock_result = [
            {
                "user_id": 1,
                "user_name": "Test-Admin",
                "user_password": "hashed password",
                "user_creation_time": "date",
            }
        ]

        view_user = View_User()
        mock_user_obj = MagicMock()
        mock_user_obj.user_name = "Test-Admin"
        mock_user_obj.user_password = "password"

        with patch.object(view_user, "create_connection"), patch.object(
            view_user, "logger"
        ), patch(
            "mysql_connections.mysql_view_user.User.from_dict",
            return_value=mock_user_obj,
        ), patch(
            "mysql_connections.mysql_view_user.check_password_hash", return_value=False
        ):
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = mock_result
            mock_conn = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            view_user.create_connection.return_value = mock_conn

            name_match, password_match = view_user.check_user_exist_and_password(
                "Test-Admin", "password"
            )

            assert name_match is True
            assert password_match is False
            mock_cursor.execute.assert_called_once()
            view_user.logger.info.assert_any_call(
                "Checking if username 'Test-Admin' entered password matches hashed"
            )


def test_view_user_check_user_exist_and_password_return_none():
    with app.app_context():
        mock_result = None

        view_user = View_User()
        mock_user_obj = MagicMock()
        mock_user_obj.user_name = "Test-Admin"
        mock_user_obj.user_password = "password"

        with patch.object(view_user, "create_connection"), patch.object(
            view_user, "logger"
        ), patch(
            "mysql_connections.mysql_view_user.User.from_dict",
            return_value=mock_user_obj,
        ), patch(
            "mysql_connections.mysql_view_user.check_password_hash", return_value=True
        ):
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = mock_result
            mock_conn = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            view_user.create_connection.return_value = mock_conn

            name_match, password_match = view_user.check_user_exist_and_password(
                "Test-Admin", "password"
            )

            assert name_match is False
            assert password_match is False
            mock_cursor.execute.assert_called_once()
            view_user.logger.info.assert_any_call(
                "Checking if username 'Test-Admin' exist"
            )


def test_view_user_check_user_exist_and_password_failed_user_creation():
    with app.app_context():
        mock_result = [
            {
                "user_id": 1,
                "user_name": "Test-Admin",
                "user_password": "bad password",
                "user_creation_time": "date",
            }
        ]

        view_user = View_User()
        mock_user_obj = MagicMock()
        mock_user_obj.user_name = "Test-Admin"
        mock_user_obj.user_password = "password"

        with patch.object(view_user, "create_connection"), patch.object(
            view_user, "logger"
        ), patch(
            "mysql_connections.mysql_view_user.User.from_dict",
            side_effect=ValueError("Invalid password"),
        ), patch(
            "mysql_connections.mysql_view_user.check_password_hash", return_value=True
        ):
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = mock_result
            mock_conn = MagicMock()
            mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
            view_user.create_connection.return_value = mock_conn

            with pytest.raises(Exception):
                view_user.check_user_exist_and_password("Test-Admin", "password")
            mock_cursor.execute.assert_called_once()
            view_user.logger.error.assert_any_call(
                "Unexpected error when trying to get user login: Unable to create user Test-Admin: Invalid password"
            )


def test_view_user_check_user_exist_and_password_failed_sql():
    with app.app_context():
        view_user = View_User()
        with patch(
            "mysql_connections.mysql_view_user.pymysql.connect",
            side_effect=MySQLError("Mocked MySQL failure"),
        ), patch.object(view_user.logger, "error") as mock_error_logger:

            with pytest.raises(pymysql.MySQLError):
                view_user.check_user_exist_and_password("Test-Admin", "password")
            view_user.logger.error.assert_any_call(
                "Unable to complete: SELECT * FROM `VV.users` WHERE user_name=%s. MySQL error: Mocked MySQL failure"
            )
