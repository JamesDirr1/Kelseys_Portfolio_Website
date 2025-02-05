from flask import Blueprint, jsonify, flash, abort, render_template
from utility_classes import custom_logger
from mysql_connections import mysql_view_user 
from data_classes.category import Category
from data_classes.project import Project
from data_classes.image import Image
from dataclasses import asdict
from markupsafe import escape

project_routes = Blueprint('project', __name__)


def create_project(project): #Function that builds project object
    project = Project(project_title = project["project_title"],
                      project_date = project["project_date"],
                      project_desc = project["project_desc"],
                      project_id = project["project_id"],
                      project_image_id = None, #image ID is not need
                      category_id = project["category_id"],
                      project_image = None #image is not need
                      )
    return project


@project_routes.route('/portfolio/<hyphen:url_category>/<hyphen:url_project>')
def display_project_images(url_category, url_project):
    url_category = escape(url_category)
    url_project = escape(url_project)

    logger = custom_logger.log("PROJECT") #Build Logger
    logger.info(f"User visited {url_category}/{url_project}")

    view_user = mysql_view_user.View_User() #Build view user
    
    project = view_user.get_project_by_title(url_project, url_category)

    logger.info(f"Project: {project}")

    project = project[0]

    project = create_project(project)

    result = jsonify(project)

    return(result)
