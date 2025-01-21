import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os
from flask import current_app

class view_images():
    def __init__(self):
        
        load_dotenv()

        self.host = os.getenv('MYSQL_HOST')
        self.port = int(os.getenv('MYSQL_PORT', 3306)) 
        self.user = os.getenv('MYSQL_USER')
        self.password = os.getenv('MYSQL_PASSWORD')
        self.db = os.getenv('MYSQL_DB')
    
    def list_connection_config(self):
        config = f"Host: {self.host}, Port: {self.port}, User: {self.user}, Password: {self.password}, Database: {self.db}"
        return config
        
    def get_db_connection(self): 
        connection = pymysql.connect(
            host=self.host,
            port=self.port, 
            user=self.user,
            password=self.password,
            db=self.db,
            connect_timeout=10,
            read_timeout=10,
            cursorclass=DictCursor 
        )
        current_app.logger.info("View_Image connection created")
        return connection
    
    def get_all_images(self):
        current_app.logger.info("Connection to DB opening")
        connection = self.get_db_connection()
        cursor = connection.cursor()

        current_app.logger.debug("Running Querry: SELECT * FROM view_images")
        cursor.execute("SELECT * FROM view_images")
        data = cursor.fetchall()
        
        cursor.close()
        connection.close()
        current_app.logger.info("Connection to DB closing")

        return (data)
        