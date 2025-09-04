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


def test_category_hyphen_converter(test_category_client_and_mocks):
    client, mock_view_user = test_category_client_and_mocks
    response = client.get("/portfolio/test_test")
    mock_view_user.get_category_by_title.assert_called_once_with("test test")
    assert response.request.path == "/portfolio/test_test"
    assert response.status_code == 200


def test_category_hyphen_converter_space(test_category_client_and_mocks):
    client, mock_view_user = test_category_client_and_mocks
    response = client.get("/portfolio/test test")
    mock_view_user.get_category_by_title.assert_called_once_with("test test")
    assert response.request.path == "/portfolio/test test"
    assert response.status_code == 200


def test_category_hyphen_converter_apostrophe(test_category_client_and_mocks):
    client, mock_view_user = test_category_client_and_mocks
    response = client.get("/portfolio/test's")
    mock_view_user.get_category_by_title.assert_called_once_with("test's")
    assert response.request.path == "/portfolio/test's"
    assert response.status_code == 200


def test_category_load_about_page(test_category_client_and_mocks):
    client, _ = test_category_client_and_mocks
    response = client.get("/portfolio/about")
    assert response.request.path == "/portfolio/about"
    assert response.status_code == 200
    assert b"<h2>About</h2>" in response.data


# UPDATE WHEN ADJUSTMENTS TO HEADER ARE MADE
def test_category_load_category_page(test_category_client_and_mocks):
    client, mock_view_user = test_category_client_and_mocks
    category = Category("test", 1, 1)
    image = Image(1, 1, 1, "test_image", "image_desc", "test_url")
    proj_date = date(2025, 1, 2)
    project = Project("test_project", image, 1, proj_date, 1, "project_desc", 1)
    mock_view_user.get_category_by_title.return_value = category
    mock_view_user.get_projects_by_category.return_value = [project]
    response = client.get("/portfolio/test")
    assert response.request.path == "/portfolio/test"
    assert response.status_code == 200
    assert b"""<div class="project-title">test_project</div>""" in response.data


def test_category_not_found(test_category_client_and_mocks, caplog):
    client, mock_view_user = test_category_client_and_mocks
    mock_view_user.get_category_by_title.return_value = None

    with caplog.at_level("ERROR"):
        response = client.get("/portfolio/NotACategory")
    assert response.status_code == 404
    assert (
        b"""<div class="flash-message error">Category &#39;NotACategory&#39; not found</div>"""
        in response.data
    )


def test_category_error(test_category_client_and_mocks, caplog):
    client, mock_view_user = test_category_client_and_mocks
    mock_view_user.get_category_by_title.side_effect = Exception("DB Error")

    with caplog.at_level("ERROR"):
        response = client.get("/portfolio/badCategory")
    assert response.status_code == 500
    assert (
        b"""<div class="flash-message error">An Error occurred when attempting to look up &#39;badCategory&#39;</div>"""
        in response.data
    )
