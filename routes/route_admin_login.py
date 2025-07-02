import urllib.parse
from flask import Blueprint, jsonify, flash, abort, redirect, render_template, request, session, url_for
from utility_classes import custom_logger
from mysql_connections import mysql_view_user 
from data_classes.category import Category
from data_classes.project import Project
from data_classes.image import Image
from dataclasses import asdict
from markupsafe import escape
import urllib


auth_routes = Blueprint('auth', __name__)

@auth_routes.route('/login', methods=['GET', 'POST'])
def login():
    logger = custom_logger.log("LOGIN")
    if request.method == 'POST':
        view_user = mysql_view_user.View_User()
        username = request.form.get('username')
        logger.info(f"'{username}' is attempting to login")
        password = request.form.get('password')

        name_match, password_match = view_user.check_user_exist_and_password(username, password)
        if name_match and password_match:
            logger.info(f"'{username}' authenticated")
            session['logged_in'] = True
            flash("Login successful!", "success")
            return redirect(url_for('dashboard.display_dashboard')) ,
        else:
            logger.info(f"Could not authenticate '{username}'")
            flash("Invalid credentials", "error")
            return redirect(url_for('auth.login'))

    return render_template('admin_login.html')
