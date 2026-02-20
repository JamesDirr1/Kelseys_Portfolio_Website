import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
from unittest.mock import patch, MagicMock
from app import app
from datetime import date
from app import database_setup, category_list
from data_classes.category import Category
from data_classes.project import Project
from data_classes.image import Image
from data_classes.user import User


def test_user_create():
    user = User(1, "user_name", "password", "12/12/01")
    assert isinstance(user, User)
    assert user.user_id == 1
    assert user.user_name == "user_name"
    assert user.user_password == "password"
    assert user.user_created_date == "12/12/01"


def test_user_create_with_defaults():
    user = User(1, "user_name", "password")
    assert isinstance(user, User)
    assert user.user_id == 1
    assert user.user_name == "user_name"
    assert user.user_password == "password"
    assert user.user_created_date is None


def test_user_create_from_dict_success():
    data = {"user_id": 1, "user_name": "Test Name", "user_password": "secret"}
    with patch("data_classes.user.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()
        user = User.from_dict(data)

    assert isinstance(user, User)
    assert user.user_id == 1
    assert user.user_name == "Test Name"
    assert user.user_password == "secret"
    assert user.user_created_date is None
    mock_logger.return_value.debug.assert_any_call(
        f"Successfully created user: {user.user_name}"
    )


def test_user_create_from_dict_missing_key():
    data = {"user_name": "Test Name", "user_password": "secret"}
    with patch("data_classes.user.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()

        with pytest.raises(KeyError) as exc_info:
            User.from_dict(data)

    assert "Missing expected key" in str(exc_info.value)
    mock_logger.return_value.error.assert_called_once_with(
        f"Missing expected key: 'user_id' in data when creating user"
    )


def test_user_create_from_dict_type_error():
    data = {"user_id": "not a num", "user_name": "Test Name", "user_password": "secret"}
    with patch("data_classes.user.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            User.from_dict(data)

    assert "Invalid value type" in str(exc_info.value)
    mock_logger.return_value.error.assert_called_once_with(
        f"Invalid value type when creating user: invalid literal for int() with base 10: 'not a num'"
    )


def test_user_create_from_dict_unexpected_exception():
    data = {"user_id": 1, "user_name": "Test Name", "user_password": "secret"}
    with patch("data_classes.user.log") as mock_logger, patch.object(
        User, "__init__", side_effect=Exception("Unexpected")
    ):
        mock_logger.return_value.debug = MagicMock()

        with pytest.raises(Exception) as exc_info:
            User.from_dict(data)

    assert "Unexpected" in str(exc_info.value)
    mock_logger.return_value.error.assert_called_once_with(
        f"Unexpected error when creating user: Unexpected"
    )
