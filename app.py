from flask import Flask, request, redirect
import time, logging, os
from mysql_connections.mysql_root import Root
from mysql_connections.mysql_view_user import View_User
from utility_classes import custom_logger
from routes.route_category import category_routes
from routes.route_project import project_routes
from routes.route_image import image_routes
from dotenv import load_dotenv
from data_classes.category import Category

 
app = Flask(__name__)

load_dotenv
app.secret_key = os.getenv("FLASK_KEY")

def app_start_up(): #Function that handles anything that need to be setup before handling any request.
    logger.info("---- APP STARTING ----")
    
    logger.register("category_routes")
    app.register_blueprint(category_routes)
    logger.register("project_routes")
    app.register_blueprint(project_routes)
    logger.register("image_routes")
    app.register_blueprint(image_routes)

    Root_user= Root() #Creates MYSQL Root user
    logger.info("Root user created")

    logger.info("Checking if database is ready")
    connection = False 
    while connection == False: #Loops every 30 seconds and uses Root_user to try to connect to the database and make sure its ready to go.
        try: 
            connection = Root_user.try_connection()
        except Exception as e:
            logger.error(f"----Could not connect to the database----\n {e}")
        if connection:
            break
        else:
            time.sleep(5)

    try:
        Root_user.create_users() #Creates users for the database that will be used later in the app.
    except Exception as e: 
        logger.critical(f"----Could not create users----\n {e}")
    
    try:
        Root_user.create_test_data()
    except Exception as e:
        logger.debug(f"Could not create test user: {e}")

def category_list():
    view_user = View_User()
    cat_list = view_user.get_all_categories()
    cat_list = [Category(**item) for item in cat_list]
    cat_total = len(cat_list)
    cat_list.append(Category("About", 0, cat_total + 1))
    logger.debug(f"Category list: {cat_list}")
    return (cat_list)

with app.app_context():
    logging.basicConfig(level="INFO", format=f'%(asctime)s %(levelname)-8s| %(message)s')
    logger = custom_logger.log("MAIN")
    app_start_up() #initializes application

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
    main_category = min(categories, key=lambda cat: cat.category_order)
    url = main_category.category_title
    logger.redirect(f"/portfolio/{url}")
    return redirect(f'/portfolio/{url}')


@app.after_request
def log_response(response):
    start_time = request.environ.get("start_time", time.time())
    elapsed = time.time() - start_time
    logger.response(response.status, elapsed)
    return response

from flask import render_template

@app.errorhandler(404)
def page_not_found(e):
    # This renders the base template with a custom error message for 404
    return render_template('base.html', error_message="Page Not Found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    # This renders the base template with a custom error message for 500
    return render_template('base.html', error_message="Internal Server Error"), 500


if __name__ == '__main__':
    app.run(debug=True)

