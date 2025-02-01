from flask import Blueprint, jsonify, flash, abort
from utility_classes import custom_logger
import time, logging
from mysql_connections import mysql_view_user 
from data_classes.category import category



 
category_routes = Blueprint('category', __name__)

def get_category_by_title(categories, title):
    # Filter categories list by category_title
    category = next((cat for cat in categories if cat['category_title'].lower() == title.lower()), None)
    
    return category


@category_routes.route('/portfolio/<string:url_category>')
def display_category_projects(url_category):
    logger = custom_logger.log("CATEGORY")
    logger.info(f"User visited {url_category}")
    view_user = mysql_view_user.View_User()
    categories = view_user.get_all_categories()
    categories_list = [category(**item) for item in categories]
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

    results = {
        "Categories": categories_list,
        url_category: projects
    }
  
    return(results)

