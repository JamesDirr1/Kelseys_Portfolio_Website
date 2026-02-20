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


def test_category_create():
    cat = Category("Title", 1, 2)
    assert isinstance(cat, Category)
    assert cat.category_title == "Title"
    assert cat.category_id == 1
    assert cat.category_order == 2


def test_category_create_with_defaults():
    cat = Category("Title")
    assert isinstance(cat, Category)
    assert cat.category_title == "Title"
    assert cat.category_id is None
    assert cat.category_order is None


def test_category_create_from_dict_success():
    data = {"category_id": 1, "category_title": "Title", "category_order": 2}
    with patch("data_classes.category.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()
        cat = Category.from_dict(data)

        assert isinstance(cat, Category)
        assert cat.category_id == 1
        assert cat.category_title == "Title"
        assert cat.category_order == 2
        mock_logger.return_value.debug.assert_any_call(
            f"Successfully created Category: {cat}"
        )


def test_category_create_from_dict_missing_key():
    data = {"category_id": 1, "category_order": 2}

    with patch("data_classes.category.log") as mock_logger:
        mock_logger.return_value.error = MagicMock()

        with pytest.raises(KeyError) as exc_info:
            Category.from_dict(data)

        assert "Missing expected key" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Missing expected key: 'category_title' in data: {data} when creating Category"
        )


def test_category_create_from_dict_type_error():
    data = {"category_id": "one", "category_title": "Title", "category_order": 2}

    with patch("data_classes.category.log") as mock_logger:
        mock_logger.return_value.error = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            Category.from_dict(data)

        assert "Invalid value type" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Invalid value type when creating Category: invalid literal for int() with base 10: 'one', data: {data}"
        )


def test_category_create_from_dict_unexpected_exception():
    data = {"category_id": 1, "category_title": "Title", "category_order": 2}

    with patch("data_classes.category.log") as mock_logger, patch.object(
        Category, "__init__", side_effect=Exception("Unexpected")
    ):
        mock_logger.return_value.error = MagicMock()

        with pytest.raises(Exception) as exc_info:
            Category.from_dict(data)

        # These run after the exception is caught
        assert "Unexpected" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Unexpected error when creating Category: Unexpected, data: {data}"
        )
