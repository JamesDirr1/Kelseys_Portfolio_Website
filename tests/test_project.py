import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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

def test_project_hyphen_converter(test_project_client_and_mocks):
    client, mock_view_user= test_project_client_and_mocks
    response = client.get('/portfolio/test_test/project_name')
    mock_view_user.get_project_by_title.assert_called_once_with("project name", "test test")
    assert response.request.path == '/portfolio/test_test/project_name'
    assert response.status_code == 200

def test_project_hyphen_converter_space(test_project_client_and_mocks):
    client, mock_view_user= test_project_client_and_mocks
    response = client.get('/portfolio/test test/project name')
    mock_view_user.get_project_by_title.assert_called_once_with("project name", "test test")
    assert response.request.path == '/portfolio/test test/project name'
    assert response.status_code == 200

def test_project_hyphen_converter_apostrophe(test_project_client_and_mocks):
    client, mock_view_user= test_project_client_and_mocks
    response = client.get("/portfolio/test's/project's")
    mock_view_user.get_project_by_title.assert_called_once_with("project's", "test's")
    assert response.request.path == "/portfolio/test's/project's"
    assert response.status_code == 200

#UPDATE WHEN ADJUSTMENTS TO HEADER ARE MADE
def test_project_load_page(test_project_client_and_mocks):
    client, mock_view_user= test_project_client_and_mocks
    proj = Project("Title", None, 1, date(2025, 1, 2), 2, "desc", 1)
    image = Image(1, 2)
    mock_view_user.get_project_by_title.return_value = proj
    mock_view_user.get_project_images.return_value = [image]
    response = client.get('/portfolio/test/Title')
    assert response.request.path == '/portfolio/test/Title'
    assert response.status_code == 200
    assert b"""<div class="h3">Title</div>""" in response.data
    assert b"""<div class="image-title">None</div>""" in response.data

def test_project_load_page_project_not_found(test_project_client_and_mocks):
    client, mock_view_user= test_project_client_and_mocks
    proj = None
    image = Image(1, 2)
    mock_view_user.get_project_by_title.return_value = proj
    mock_view_user.get_project_images.return_value = [image]
    response = client.get('/portfolio/test/NotAProject')
    assert response.status_code == 404
    assert b""" <div class="flash-message error">Project &#39;NotAProject&#39; not found in category &#39;test&#39;.</div>""" in response.data
    
