from flask import Blueprint, jsonify, flash, abort, render_template
from utility_classes import custom_logger
from mysql_connections import mysql_view_user 
from markupsafe import escape


project_routes = Blueprint('project', __name__)

def decode(string):
    return(string.replace("_", "'"))

@project_routes.route('/portfolio/<hyphen:url_category>/<hyphen:url_project>')
def display_project_images(url_category, url_project):
    url_category = decode(url_category)
    url_project = decode(url_project)
    logger = custom_logger.log("PROJECT") #Build Logger
    logger.debug(url_category)
    logger.debug(url_project)


    logger.info(f"User visited {url_category}/{url_project}")

    view_user = mysql_view_user.View_User() #Build view user
    
    project = view_user.get_project_by_title(url_project, url_category)

    logger.info(f"Project: {project}")
    if project is None:
        logger.error(f"Project '{url_project}' not found in category '{url_category}'.")
        flash(f"Project '{url_project}' not found in category '{url_category}'.", "error" )
        abort(404)

    images = view_user.get_project_images(project.project_id)

    result = {"Project" : project,
              "Images" : images
    }
    

    return(jsonify(result))
