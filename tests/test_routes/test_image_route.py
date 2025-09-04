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
    assert img.image_weight == 1
    assert img.project_id == 2
    assert img.image_id == 3
    assert img.image_title == "Title"
    assert img.image_desc == "desc"
    assert img.image_url == "image.com"


def test_image_create_with_defaults():
    img = Image(1, 2)
    assert img.image_weight == 1
    assert img.project_id == 2
    assert img.image_id == None
    assert img.image_title == None
    assert img.image_desc == None
    assert (
        img.image_url
        == "https://static.wixstatic.com/media/0fee66_18f00ad0221142dfbd4c21f7e54d425f~mv2.png/v1/fill/w_549,h_289,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/Kelsey_Spade_Header.png"
    )


def test_image_hyphen_converter(test_image_client_and_mocks):
    client, mock_view_user = test_image_client_and_mocks
    response = client.get("/portfolio/test_test/project_name/image_id_1")
    mock_view_user.get_image.assert_called_once_with(1)
    assert response.request.path == "/portfolio/test_test/project_name/image_id_1"
    assert response.status_code == 200


def test_image_hyphen_converter_space(test_image_client_and_mocks):
    client, mock_view_user = test_image_client_and_mocks
    response = client.get("/portfolio/test test/project name/image_id_1")
    mock_view_user.get_image.assert_called_once_with(1)
    assert response.request.path == "/portfolio/test test/project name/image_id_1"
    assert response.status_code == 200


def test_image_hyphen_converter_non_int(test_image_client_and_mocks):
    client, _ = test_image_client_and_mocks
    response = client.get("/portfolio/test test/project name/image_id_one")
    assert response.request.path == "/portfolio/test test/project name/image_id_one"
    assert response.status_code == 404


def test_image_load_page(test_image_client_and_mocks):
    client, mock_view_user = test_image_client_and_mocks
    image = Image(1, 2, 3, "Title", "Desc", "cat.com")
    mock_view_user.get_image.return_value = image
    response = client.get("/portfolio/test/project/image_id_3")
    assert response.request.path == "/portfolio/test/project/image_id_3"
    assert response.status_code == 200
    assert b"""<img class="image" src="cat.com" alt="Desc" >""" in response.data


def test_image_load_page_not_found(test_image_client_and_mocks):
    client, mock_view_user = test_image_client_and_mocks
    image = None
    mock_view_user.get_image.return_value = image
    response = client.get("/portfolio/test/project/image_id_3")
    print(response.data)
    assert response.status_code == 404
    assert (
        b"""<div class="flash-message error">Image ID &#39;3&#39; not found.</div>"""
        in response.data
    )


def test_image_error(test_image_client_and_mocks, caplog):
    client, mock_view_user = test_image_client_and_mocks
    mock_view_user.get_image.side_effect = Exception("DB Error")

    with caplog.at_level("ERROR"):
        response = client.get("/portfolio/Category/project/image_id_4")

    assert response.status_code == 500
    assert (
        b"""<div class="flash-message error">An Error occurred when attempting to look up image &#39;4&#39; from &#39;project&#39;</div>"""
        in response.data
    )
