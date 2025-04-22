import sys
from flask import Flask, request, redirect, flash, abort, render_template
import time, logging, os
from mysql_connections.mysql_Root import Root
from mysql_connections.mysql_view_user import View_User
from utility_classes import custom_logger
from routes.route_category import category_routes
from routes.route_project import project_routes
from routes.route_image import image_routes
from dotenv import load_dotenv
from data_classes.category import Category
from werkzeug.routing import BaseConverter

load = load_dotenv(override=True)

from config.flask.config import Config
 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.secret_key = app.config['SECRET_KEY']

    app.url_map.converters['hyphen'] = HyphenConverter

    app.register_blueprint(category_routes, url_prefix='/portfolio')
    app.register_blueprint(project_routes, url_prefix='/portfolio')
    app.register_blueprint(image_routes, url_prefix='/portfolio')

    return app

class HyphenConverter(BaseConverter): #Converts space characters to hyphens and hymens to spaces in urls.
    def to_python(self, value):
        value = value.replace('_', ' ')
        return value
    
    def to_url(self, value):
        value = value.replace(' ', '_')
        return value

app = create_app()



def database_setup():
    app.logger.info("---- Database Setup ----")
    Root_user= Root() #Creates MYSQL Root user
    app.logger.info("Root user created")
    app.logger.info("Checking if database is ready")
    connection = False 
    while connection == False: #Loops every 30 seconds and uses Root_user to try to connect to the database and make sure its ready to go.
        try: 
            connection = Root_user.try_connection()
        except Exception as e:
            app.logger.error(f"----Could not connect to the database----\n {e}")
        if connection:
           break
        else:
           time.sleep(5)
    app.logger.info("---- Connection established ----")

    try:
        Root_user.create_users() #Creates users for the database that will be used later in the app.
    except Exception as e: 
        app.logger.critical(f"----Could not create users----\n {e}")
    
    try:
        Root_user.create_test_data()
    except Exception as e:
        app.logger.debug(f"Could not create test data: {e}")

def category_list():
    view_user = View_User()
    cat_list = view_user.get_all_categories()
    cat_total = len(cat_list)
    cat_list.append(Category("About", 0, cat_total + 1))
    app.logger.debug(f"Category list: {cat_list}")
    return (cat_list)

with app.app_context():
    logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    format='%(asctime)s %(levelname)-8s| %(message)s'
)
    logger = custom_logger.log("MAIN")

    logger.info("---- APP STARTING ----")

    


    env = app.config['FLASK_ENVIRONMENT']
    if env != "Test":
        app.logger.debug('NOT IN TEST')
        database_setup()

@app.context_processor
def get_navbar():
    logger.info("Getting categories for nav bar")
    categories = category_list()
    return dict(categories = categories)

@app.before_request
def log_request():
    logger.request(request.method, request.url, request.headers)
    start_time = time.time()
    request.environ["start_time"] = start_time

@app.route('/')
def index():
    logger.visit("Home")
    categories = category_list()    
    if len(categories) == 0: #Checks if there is any categories in the database, throws 404 error if not
        app.logger.error("Trying to access categories when none exists")
        flash("No categories exists", "error")
        abort(404)
    main_category = min(categories, key=lambda cat: cat.category_order)
    url = main_category.category_title
    logger.redirect(f"/portfolio/{url}")
    return redirect(f'/portfolio/{url}')

@app.route('/error')
def error_route():
    logger.error("AN ERROR HAS OCCURRED")
    flash("AN ERROR HAS OCCURRED", "error" )
    abort(500)


@app.after_request
def log_response(response):
    start_time = request.environ.get("start_time", time.time())
    elapsed = time.time() - start_time
    logger.response(response.status, elapsed)
    return response

@app.errorhandler(404)
def page_not_found(e):
    # This renders the base template with a custom error message for 404
    return render_template('base.html', error_message="Page Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    # This renders the base template with a custom error message for 500
    return render_template('base.html', error_message="Internal Server Error"), 500



if __name__ == '__main__':
    app.run()

