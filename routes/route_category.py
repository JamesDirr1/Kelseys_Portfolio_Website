import urllib.parse
from flask import Blueprint, jsonify, flash, abort, render_template
from utility_classes import custom_logger
from mysql_connections import mysql_view_user 
from data_classes.category import Category
from data_classes.project import Project
from data_classes.image import Image
from dataclasses import asdict
from markupsafe import escape
import urllib


 
category_routes = Blueprint('category', __name__)

def decode(string):
    return(string.replace("_", "'"))

@category_routes.route('<hyphen:url_category>')
def display_category_projects(url_category):
    logger = custom_logger.log("CATEGORY") #Build Logger
    logger.info(f"User visited {url_category}")

    view_user = mysql_view_user.View_User() #Build view user
    
    current_category = view_user.get_category_by_title(url_category) #Checks if the provide url category exists

    if not current_category: #if the proved url does not exist throws 404
        logger.error(f"Category '{url_category}' not found")
        flash(f"Category '{url_category}' not found", "error" )
        abort(404)

    flash("Welcome!", "success")
    
    projects = view_user.get_projects_by_category(current_category.category_id, False) #Gets list of projects per the current category

    return render_template("category.html", projects = projects, category = current_category)

