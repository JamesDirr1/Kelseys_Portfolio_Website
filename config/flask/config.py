import os
from os import environ, path
from dotenv import load_dotenv

# Load environment variables from .env file

load_dotenv(override=True)


class Config:
    #Flask 
    SECRET_KEY = os.getenv("FLASK_KEY")
    LOG_LEVEL = os.getenv("FLASK_LOG")
    FLASK_ENVIRONMENT = os.getenv("FLASK_ENVIRONMENT")
    DEBUG = FLASK_ENVIRONMENT == 'development'

    #Sever Connection
    MYSQL_HOST = os.getenv("MYSQL_HOST")
    MYSQL_PORT = os.getenv("MYSQL_PORT")
    MYSQL_DB = os.getenv("MYSQL_DB")

    #Root user
    MYSQL_ROOT = os.getenv("MYSQL_ROOT")
    MYSQL_ROOT_USER = os.getenv("MYSQL_ROOT_USER")
    MYSQL_ROOT_PASSWORD = os.getenv("MYSQL_ROOT_PASSWORD")

    #View user
    MYSQL_VIEW_USER = os.getenv("MYSQL_VIEW_USER")
    MYSQL_VIEW_USER_PASSWORD = os.getenv("MYSQL_VIEW_USER_PASSWORD")


    #Main admin account
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")







