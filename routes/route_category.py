from flask import Blueprint, jsonify, flash, abort, render_template
from utility_classes import custom_logger
import time, logging
from mysql_connections import mysql_view_user 
from data_classes.category import Category
from data_classes.project import Project
from data_classes.image import Image
from dataclasses import asdict
from markupsafe import escape



 
category_routes = Blueprint('category', __name__)

def get_category_by_title(categories, title): #Function that category from the url is in the datable.
    category = next((cat for cat in categories if cat.category_title.lower() == title.lower()), None)
    return category

def create_project(project): #Function that builds project object
    project = Project(project_title = project["project_title"],
                      project_date = project["project_date"],
                      project_desc = project["project_desc"],
                      project_id = project["project_id"],
                      project_image_id = project["image_id"],
                      category_id = project["category_id"],
                      project_image = create_image_from_project(project)
                      )
    return project

def create_image_from_project(project): #Function that builds image object
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
    url_category = escape(url_category) #Escape url variable

    logger = custom_logger.log("CATEGORY") #Build Logger
    logger.info(f"User visited {url_category}")

    view_user = mysql_view_user.View_User() #Build view user

    categories = view_user.get_all_categories() #Gets all categories in the database. This is used to generate possible tabs. 
    categories_list = [Category(**item) for item in categories] #Build list of categories 

    if len(categories_list) == 0: #Checks if there is any categories in the database, throws 404 error if not
        logger.error("Trying to access categories when none exists")
        flash("No categories exists", "error")
        abort(404)
    
    current_category = get_category_by_title(categories_list, url_category) #Checks if the provide url category exists

    if not current_category: #if the proved url does not exist throws 404
        logger.error(f"Category {url_category} not found")
        flash(f"Category {url_category} not found", "error" )
        abort(404)
    
    projects = view_user.get_projects_by_category(current_category.category_id, False) #Gets list of projects per the current category

    project_list = []
    for p in projects: #Creates projects form the results
        project_list.append(create_project(p))
   
    for project in project_list:
        logger.info(project.project_image.image_url)
  
    return render_template("category.html", project_list = project_list)

