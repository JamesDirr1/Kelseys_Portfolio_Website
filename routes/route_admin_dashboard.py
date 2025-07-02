import urllib.parse
from flask import Blueprint, jsonify, flash, abort, redirect, render_template, session, url_for
from utility_classes import custom_logger
from mysql_connections import mysql_view_user 
from data_classes.category import Category
from data_classes.project import Project
from data_classes.image import Image
from dataclasses import asdict
from markupsafe import escape
import urllib


 
admin_dashboard_routes = Blueprint('dashboard', __name__)

@admin_dashboard_routes.before_request
def require_login_for_dashboard():
    if not session.get("logged_in"):  # Adjust key if your login uses something else
        flash("Login required to access the dashboard.", "error")
        return redirect(url_for("auth.login"))

@admin_dashboard_routes.route('/dashboard')
def display_dashboard():
    logger = custom_logger.log("ADMIN")  # Build Logger
    logger.info("User visited Admin Dashboard")

    view_user = mysql_view_user.View_User()  # Build view user
    flash("Welcome!", "success")

    return render_template("admin_dashboard.html")


