import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock

from app import app
from data_classes.category import Category
from routes.route_category import category_routes

#To Run Test set Flask_environment to 'Test' and run 'coverage run -m pytest -sv' 
#To generate coverage report run 'Coverage' html


@pytest.fixture(scope='function')
def test_app_client_and_mocks():
    app.testing = True
    with app.test_client() as client, \
         patch('app.Root') as MockRoot, \
         patch('app.View_User') as MockViewUser, \
         patch('app.logger') as mock_logger:
        
        # Mock instances
        mock_root = MagicMock()
        MockRoot.return_value = mock_root
        
        mock_view_user = MagicMock()
        MockViewUser.return_value = mock_view_user
        
        # Yield the client and all mocks as a tuple
        yield client, mock_root, mock_view_user, mock_logger

@pytest.fixture(scope='function')
def test_category_client_and_mocks():
    app.testing = True
    with app.test_client() as client, \
         patch('routes.route_category.mysql_view_user.View_User') as MockViewUser, \
         patch('app.View_User') as app_view_user:
        
        # Mocking View_User
        mock_view_user = MagicMock()
        MockViewUser.return_value = mock_view_user
        
        # Mocking the get_navbar context processor
        app_view_user.get_all_categories.return_value = [Category("test", 1, 1)]
        
        # Yield the client and all mocks as a tuple
        yield client, mock_view_user

@pytest.fixture(scope='function')
def test_project_client_and_mocks():
    app.testing = True
    with app.test_client() as client, \
         patch('routes.route_project.mysql_view_user.View_User') as MockViewUser, \
         patch('app.View_User') as app_view_user:
        
        # Mocking View_User
        mock_view_user = MagicMock()
        MockViewUser.return_value = mock_view_user
        
        # Mocking the get_navbar context processor
        app_view_user.get_all_categories.return_value = [Category("test", 1, 1)]
        
        # Yield the client and all mocks as a tuple
        yield client, mock_view_user

@pytest.fixture(scope='function')
def test_image_client_and_mocks():
    app.testing = True
    with app.test_client() as client, \
         patch('routes.route_image.mysql_view_user.View_User') as MockViewUser, \
         patch('app.View_User') as app_view_user:
        
        # Mocking View_User
        mock_view_user = MagicMock()
        MockViewUser.return_value = mock_view_user
        
        # Mocking the get_navbar context processor
        app_view_user.get_all_categories.return_value = [Category("test", 1, 1)]
        
        # Yield the client and all mocks as a tuple
        yield client, mock_view_user