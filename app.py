from flask import Flask, request, redirect
import time, logging
from mysql_connections.mysql_root import Root
from utility_classes import custom_logger
from routes.route_category import category_routes
from routes.route_project import project_routes
from routes.route_image import image_routes

 
app = Flask(__name__)


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
        time.sleep(5)
        try: 
            connection = Root_user.try_connection()
        except Exception as e:
            logger.error(f"----Could not connect to the database----\n {e}")

    try:
        Root_user.create_users() #Creates users for the database that will be used later in the app.
    except Exception as e: 
        logger.critical(f"----Could not create users----\n {e}")

with app.app_context():
    logging.basicConfig(level="DEBUG", format=f'%(asctime)s %(levelname)-8s| %(message)s')
    logger = custom_logger.log("MAIN")
    app_start_up() #initializes application

@app.before_request
def log_request():
    logger.request(request.method, request.url, request.headers)
    start_time = time.time()
    request.environ["start_time"] = start_time

@app.route('/')
def index():
    logger.visit("Home")
    logger.redirect("/portfolio/comics")
    return redirect('/portfolio/comics')


@app.after_request
def log_response(response):
    start_time = request.environ.get("start_time", time.time())
    elapsed = time.time() - start_time
    logger.response(response.status, elapsed)
    return response

if __name__ == '__main__':
    app.run(debug=True)

