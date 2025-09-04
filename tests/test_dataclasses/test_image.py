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


def test_image_create():
    img = Image(1, 2, 3, "Title", "desc", "image.com")
    assert isinstance(img, Image)
    assert img.image_weight == 1
    assert img.project_id == 2
    assert img.image_id == 3
    assert img.image_title == "Title"
    assert img.image_desc == "desc"
    assert img.image_url == "image.com"


def test_image_create_with_defaults():
    img = Image(1, 2)
    assert isinstance(img, Image)
    assert img.image_weight == 1
    assert img.project_id == 2
    assert img.image_id == None
    assert img.image_title == None
    assert img.image_desc == None
    assert (
        img.image_url
        == "https://static.wixstatic.com/media/0fee66_18f00ad0221142dfbd4c21f7e54d425f~mv2.png/v1/fill/w_549,h_289,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Kelsey_Spade_Header.png"
    )


def test_image_create_from_dict_success():
    data = {
        "image_id": 1,
        "image_title": "Title",
        "image_desc": "some desc",
        "image_URL": "image.com",
        "image_weight": 2,
        "project_id": 3,
    }
    with patch("utility_classes.custom_logger.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()
        img = Image.from_dict(data)

        assert isinstance(img, Image)
        assert img.image_weight == 2
        assert img.project_id == 3
        assert img.image_id == 1
        assert img.image_title == "Title"
        assert img.image_desc == "some desc"
        assert img.image_url == "image.com"
        mock_logger.return_value.debug.assert_any_call(
            f"Successfully created Image: {img}"
        )


def test_image_create_from_dict_missing_key():
    data = {
        "image_title": "Title",
        "image_desc": "some desc",
        "image_URL": "image.com",
        "image_weight": 2,
        "project_id": 3,
    }

    with patch("utility_classes.custom_logger.log") as mock_logger:
        mock_logger.return_value.error = MagicMock()

        with pytest.raises(KeyError) as exc_info:
            Image.from_dict(data)

        assert "image_id" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Missing expected key: 'image_id' in data: {data} when creating Image"
        )


def test_image_create_from_dict_value_error():
    data = {
        "image_id": 1,
        "image_title": "Title",
        "image_desc": "some desc",
        "image_URL": "image.com",
        "image_weight": "some num",
        "project_id": 3,
    }

    with patch("utility_classes.custom_logger.log") as mock_logger:
        mock_logger.return_value.error = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            Image.from_dict(data)

        assert "image_weight" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Invalid value type when creating Image: invalid literal for int() with base 10: 'some num', data: {data}"
        )


def test_image_create_from_dict_unexpected_error():
    data = {
        "image_id": 1,
        "image_title": "Title",
        "image_desc": "some desc",
        "image_URL": "image.com",
        "image_weight": 2,
        "project_id": 3,
    }

    with patch("utility_classes.custom_logger.log") as mock_logger, patch.object(
        Image, "__init__", side_effect=Exception("Unexpected")
    ):
        mock_logger.return_value.error = MagicMock()

        with pytest.raises(Exception) as exc_info:
            Image.from_dict(data)

        assert "Unexpected" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Unexpected error when creating Image: Unexpected, data: {data}"
        )


def test_image_create_from_project_dict_success():
    data = {
        "project_id": 1,
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
        "project_image_id": 3,
        "image_id": 3,
        "image_title": "Image Title",
        "image_desc": "Image desc",
        "image_URL": "image.com",
        "image_weight": 1,
        "image.project_id": 1,
    }

    with patch("utility_classes.custom_logger.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()
        img = Image.from_project_dict(data)

        assert isinstance(img, Image)
        assert img.image_weight == 1
        assert img.project_id == 1
        assert img.image_id == 3
        assert img.image_title == "Image Title"
        assert img.image_desc == "Image desc"
        assert img.image_url == "image.com"
        mock_logger.return_value.debug.assert_any_call(
            f"Successfully created Image from Project data: {img}"
        )


def test_image_create_from_project_dict_null_image():
    data = {
        "project_id": 1,
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
        "project_image_id": None,
        "image_id": 3,
        "image_title": "Image Title",
        "image_desc": "Image desc",
        "image_URL": "image.com",
        "image_weight": 1,
        "image.project_id": 1,
    }

    with patch("utility_classes.custom_logger.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()
        img = Image.from_project_dict(data)

        assert isinstance(img, Image)
        assert img.image_weight == 0
        assert img.project_id == 1
        assert img.image_id == None
        assert img.image_title == None
        assert img.image_desc == None
        assert (
            img.image_url
            == "https://static.wixstatic.com/media/0fee66_18f00ad0221142dfbd4c21f7e54d425f~mv2.png/v1/fill/w_549,h_289,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Kelsey_Spade_Header.png"
        )
        mock_logger.return_value.debug.assert_any_call(
            f"Creating 'Null' project image with weight 0"
        )


def test_image_create_from_project_dict_missing_key():
    data = {
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
        "project_image_id": 3,
        "image_id": 3,
        "image_title": "Image Title",
        "image_desc": "Image desc",
        "image_URL": "image.com",
        "image_weight": 1,
    }

    with patch("utility_classes.custom_logger.log") as mock_logger:
        mock_logger.return_value.error = MagicMock()

        with pytest.raises(KeyError) as exc_info:
            Image.from_project_dict(data)

        assert "project_id" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Missing expected key: 'project_id' in data: {data} when creating Image from project"
        )


def test_image_create_from_project_dict_value_error():
    data = {
        "project_id": "not a number",
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
        "project_image_id": None,
        "image_id": 3,
        "image_title": "Image Title",
        "image_desc": "Image desc",
        "image_URL": "image.com",
        "image_weight": 1,
        "image.project_id": 1,
    }

    with patch("utility_classes.custom_logger.log") as mock_logger:
        mock_logger.return_value.error = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            Image.from_project_dict(data)

        assert "project_id" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Invalid value type when creating Image from project: invalid literal for int() with base 10: 'not a number', data: {data}"
        )

def test_image_create_from_project_dict_unexpected_error():
    data = {
        "project_id": 1,
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
        "project_image_id": None,
        "image_id": 3,
        "image_title": "Image Title",
        "image_desc": "Image desc",
        "image_URL": "image.com",
        "image_weight": 1,
        "image.project_id": 1,
    }

    with patch("utility_classes.custom_logger.log") as mock_logger, patch.object(
        Image, "__init__", side_effect=Exception("Unexpected")
    ):
        mock_logger.return_value.error = MagicMock()

        with pytest.raises(Exception) as exc_info:
            Image.from_project_dict(data)

        assert "Unexpected" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Unexpected error when creating Image from project: Unexpected, data: {data}"
        )
