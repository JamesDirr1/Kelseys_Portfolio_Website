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


def test_project_create():
    proj = Project("Title", None, 1, date(2025, 1, 2), 2, "desc", 1)
    assert proj.project_title == "Title"
    assert proj.project_image == None
    assert proj.project_image_id == 1
    assert proj.project_id == 2
    assert str(proj.project_date) == "2025-01-02"
    assert proj.project_desc == "desc"
    assert proj.category_id == 1


def test_project_create_with_defaults():
    proj = Project("Title")
    today = str(date.today())
    assert proj.project_title == "Title"
    assert proj.project_image == None
    assert proj.project_image_id == None
    assert proj.project_id == None
    assert str(proj.project_date) == today
    assert proj.project_desc == None
    assert proj.category_id == None


def test_project_create_from_dict_success():
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

    mock_image = MagicMock()

    with patch("data_classes.project.log") as mock_logger, patch(
        "data_classes.image.Image.from_project_dict", return_value=mock_image
    ):
        mock_logger.return_value.debug = MagicMock()
        proj = Project.from_dict(data)

        assert isinstance(proj, Project)
        assert proj.project_title == "Project Title"
        assert proj.project_date == "12/12/2001"
        assert proj.project_desc == "Project Desc"
        assert proj.project_id == 1
        assert proj.project_image_id == 3
        assert proj.category_id == 2
        assert proj.project_image is mock_image
        mock_logger.return_value.debug.assert_any_call(
            f"Successfully created Project: {proj}"
        )


def test_project_create_from_dict_success_no_image():
    data = {
        "project_id": 1,
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
        "project_image_id": 3,
    }

    with patch("data_classes.project.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()
        proj = Project.from_dict(data)

        assert isinstance(proj, Project)
        assert proj.project_title == "Project Title"
        assert proj.project_date == "12/12/2001"
        assert proj.project_desc == "Project Desc"
        assert proj.project_id == 1
        assert proj.project_image_id == 3
        assert proj.category_id == 2
        assert proj.project_image is None
        mock_logger.return_value.debug.assert_any_call(
            f"Successfully created Project: {proj}"
        )


def test_project_create_from_dict_success_no_image_id():
    data = {
        "project_id": 1,
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
    }

    with patch("data_classes.project.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()
        proj = Project.from_dict(data)

        assert isinstance(proj, Project)
        assert proj.project_title == "Project Title"
        assert proj.project_date == "12/12/2001"
        assert proj.project_desc == "Project Desc"
        assert proj.project_id == 1
        assert proj.project_image_id == None
        assert proj.category_id == 2
        assert proj.project_image is None
        mock_logger.return_value.debug.assert_any_call(
            f"Successfully created Project: {proj}"
        )


def test_project_create_from_dict_missing_key():
    data = {
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
    }

    with patch("data_classes.project.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()

        with pytest.raises(KeyError) as exc_info:
            Project.from_dict(data)

        assert "project_id" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Missing expected key: 'project_id' in data: {data} when creating Project"
        )


def test_project_create_from_dict_value_error():
    data = {
        "project_id": "not a num",
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
    }

    with patch("data_classes.project.log") as mock_logger:
        mock_logger.return_value.debug = MagicMock()

        with pytest.raises(ValueError) as exc_info:
            Project.from_dict(data)

        assert "project_id" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Invalid value type when creating Project: invalid literal for int() with base 10: 'not a num', data: {data}"
        )


def test_project_create_from_dict_image_error():
    data = {
        "project_id": 1,
        "project_title": "Project Title",
        "project_date": "12/12/2001",
        "project_desc": "Project Desc",
        "category_id": 2,
        "image_URL": "some.url",
    }

    with patch("data_classes.project.log") as mock_logger, patch(
        "data_classes.image.Image.from_project_dict", side_effect=Exception("some image error")
    ):
        mock_logger.return_value.debug = MagicMock()

        with pytest.raises(Exception) as exc_info:
            Project.from_dict(data)

        assert "project_id" in str(exc_info.value)
        mock_logger.return_value.error.assert_called_once_with(
            f"Unexpected error when creating Project: some image error, data: {data}"
        )
