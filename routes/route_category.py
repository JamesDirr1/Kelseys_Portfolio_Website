from flask import Blueprint, jsonify, flash, abort
from utility_classes import custom_logger
import time, logging
from mysql_connections import mysql_view_user 
from data_classes.category import Category
from data_classes.project import Project
from data_classes.image import Image
from dataclasses import asdict



 
category_routes = Blueprint('category', __name__)

def get_category_by_title(categories, title):
    # Filter categories list by category_title
    category = next((cat for cat in categories if cat['category_title'].lower() == title.lower()), None)
    
    return category

def create_project(project):
    project = Project(project_title = project["project_title"],
                      project_date = project["project_date"],
                      project_desc = project["project_desc"],
                      project_id = project["project_id"],
                      project_image_id = project["image_id"],
                      category_id = project["category_id"],
                      project_image = create_image_from_project(project)
                      )
    return project

def create_image_from_project(project):
    if project["image_id"] is None:
        project_image = Image(project_id = project["project_id"], image_weight = 0)
    else: 
        project_image = Image(image_id = project["image_id"], 
                              image_title = project["image_title"], 
                              image_desc = project["image_desc"], 
                              image_url = project["image_URL"], 
                              image_weight = project["image_weight"], 
                              project_id = project["project_id"])
    return project_image



@category_routes.route('/portfolio/<string:url_category>')
def display_category_projects(url_category):
    logger = custom_logger.log("CATEGORY")
    logger.info(f"User visited {url_category}")
    view_user = mysql_view_user.View_User()
    categories = view_user.get_all_categories()
    categories_list = [Category(**item) for item in categories]
    if len(categories_list) == 0:
        logger.error("Trying to access categories when none exists")
        flash("No categories exists")
        abort(404)
    
    current_category = get_category_by_title(categories, url_category)

    if not current_category:
        logger.error(f"Category {url_category} not found")
        flash(f"Category {url_category} not found")
        abort(404)
    
    projects = view_user.get_projects_by_category(current_category['category_id'], False)

    project_list = [asdict(create_project(p)) for p in projects]
   
    results = {
        "Categories": categories_list,
        url_category: project_list
    }
  
    return(jsonify(results))

