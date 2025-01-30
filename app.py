from flask import Flask, jsonify, request
from dotenv import load_dotenv
import time
import logging
from mysql_connections.mysql_Root import Root

app = Flask(__name__)

def app_start_up(): #Function that handles anthing that need to be setup before handling any request.
    logging.basicConfig(level="DEBUG", format=f'%(asctime)s %(levelname)s: %(message)s')
    app.logger.info("<APP> ---- APP STARTING ----")
    
    Root_user= Root() #Creates MYSQL Root user
    app.logger.info("<APP> Root user created")

    connection = False 
    while connection == False: #Loops every 30 seconds and uses Root_user to try to connect to the database and make sure its ready to go.
        time.sleep(30)
        try: 
            connection = Root_user.try_connection()
        except Exception as e:
            app.logger.error(f"<APP> Database connection failed: {e}")

    try:
        Root_user.create_users() #Creates users for the database that will be used later in the app.
    except Exception as e: 
        app.logger.critical(f"<APP> Could not create users: {e}")

with app.app_context():
    app_start_up() #initializes application

@app.before_request
def log_request():
    logging.debug(f"Request: {request.method} {request.url}")
    start_time = time.time()
    request.environ["start_time"] = start_time
    logging.debug(f"Headers: {dict(request.headers)}")

@app.route('/')
def index():
    app.logger.info("<APP> User visted home page")
    return("hello")

@app.after_request
def log_response(response):
    start_time = request.environ.get("start_time", time.time())
    elapsed = time.time() - start_time
    logging.debug(f"Response status: {response.status} - Processing time: {elapsed:.2f}s")
    return response

if __name__ == '__main__':
    app.run(debug=True)

