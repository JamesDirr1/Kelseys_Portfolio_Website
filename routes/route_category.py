from flask import Blueprint

category_routes = Blueprint('category', __name__)


@category_routes.route('/portfolio/<string:category>')
def category(category):
    return(category)