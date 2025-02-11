from flask import Blueprint, jsonify, flash, abort, render_template, request
from utility_classes import custom_logger
from mysql_connections import mysql_view_user 
from markupsafe import escape


project_routes = Blueprint('project', __name__)

@project_routes.route('<hyphen:url_category>/<hyphen:url_project>')
def display_project_images(url_category, url_project):
    logger = custom_logger.log("PROJECT") #Build Logger
    logger.debug(url_category)
    logger.debug(url_project)


    logger.info(f"User visited '{request.path}")

    view_user = mysql_view_user.View_User() #Build view user
    
    project = view_user.get_project_by_title(url_project, url_category)

    logger.info(f"Project: {project}")
    if project is None:
        logger.error(f"Project '{url_project}' not found in category '{url_category}'.")
        flash(f"Project '{url_project}' not found in category '{url_category}'.", "error" )
        abort(404)

    images = view_user.get_project_images(project.project_id)

    current_url = request.path + "/"
 
    return render_template("project.html", project = project, images = images, current_url = current_url)
