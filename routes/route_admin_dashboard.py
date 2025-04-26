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


 
admin_dashboard_routes = Blueprint('dashboard', __name__)

@admin_dashboard_routes.route('/dashboard')
def display_dashboard():
    logger = custom_logger.log("ADMIN")  # Build Logger
    logger.info("User visited Admin Dashboard")

    view_user = mysql_view_user.View_User()  # Build view user
    flash("Welcome!", "success")

    return render_template("admin_dashboard.html")


