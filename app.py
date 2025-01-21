from flask import Flask, jsonify
from dotenv import load_dotenv
import logging
from mysql_connections.mysql_view_images import view_images

app = Flask(__name__)

logging.basicConfig( level=logging.INFO, format=f'%(asctime)s %(levelname)s: %(message)s')

app.logger.info("Web app has started")

load_dotenv()
app.logger.info("ENV file has been loaded")

querry = view_images()
app.logger.info("querry has been created")
app.logger.debug("Querry config" + querry.list_connection_config())

@app.route('/')
def index():
    app.logger.info("user visited home page")
    images = querry.get_all_images()
    return jsonify(images)
if __name__ == '__main__':
    app.run(debug=True)