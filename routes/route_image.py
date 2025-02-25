from flask import Blueprint, jsonify, flash, abort, render_template
from utility_classes import custom_logger
from mysql_connections import mysql_view_user 
from markupsafe import escape


image_routes = Blueprint('image', __name__)

@image_routes.route('<hyphen:url_category>/<hyphen:url_project>/image_id_<int:url_image>')
def display_image(url_category, url_project, url_image):
    logger = custom_logger.log("IMAGE") #Build Logger
    logger.debug(url_category)
    logger.debug(url_project)
    logger.debug("Image")

    logger.info(f"User visited {url_category}/{url_project}/{url_image}")

    view_user = mysql_view_user.View_User() #Build view user

    image = view_user.get_image(url_image)

    logger.info(f"Image: {image}")
    if image is None: 
        logger.error(f"Image ID '{url_image}' not found.")
        flash(f"Image ID '{url_image}' not found.", "error")
        abort(404)

    return render_template("image.html", image = image)
