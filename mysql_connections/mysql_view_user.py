import pymysql, os, time, utility_classes.custom_logger
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

class View_User():
    def __init__(self): #Load .env file and set variables need to connect to the mysql database as the View_user.
        self.host = os.getenv('MYSQL_HOST')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.user = os.getenv('MYSQL_VIEW_USER')
        self.password = os.getenv('MYSQL_VIEW_USER_PASSWORD')
        self.db = os.getenv('MYSQL_DB')
        self.logger = utility_classes.custom_logger.log("VIEW_USER")

    def create_connection(self): #Function that creates a PyMySQL connection using the variables outlined above.
        self.logger.info("Connection created")
        connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.db,
            cursorclass=DictCursor
        )
        return connection
    
    def get_all_categories(self): #Function that attempts to query the database to get list of all categories.
        self.logger.con_open
        query = "SELECT * FROM Portfolio.`VV.category`;"
        start_time = time.time()
        connection = self.create_connection()
        cursor = connection.cursor()
        try: 
            with connection.cursor() as cursor:
                cursor.execute(query)
                categories = cursor.fetchall()
                self.logger.query(query, f"{categories}")
        except pymysql.MySQLError as e:
            self.logger.error(f"unable to get categories: {e}")
        finally:
            cursor.close()
            connection.close()
            end_time = time.time - start_time
            self.logger.con_close(end_time)
            return(categories) 
        
    def get_categories_ordered(self):#Function that attempts to query the database to get list of all categories sorted by order
        self.logger.con_open
        query = "SELECT * FROM Portfolio.`VV.category` ORDER BY category_order ASC;"
        start_time = time.time()
        connection = self.create_connection()
        cursor = connection.cursor()
        try: 
            with connection.cursor() as cursor:
                cursor.execute(query)
                categories = cursor.fetchall()
                self.logger.query(query, f"{categories}")
        except pymysql.MySQLError as e:
            self.logger.error(f"unable to get categories: {e}")
        finally:
            cursor.close()
            connection.close()
            end_time = time.time - start_time
            self.logger.con_close(end_time)
            return(categories)
        
    def get_category(self, id):#Function that attempts to query the database to get specific category by ID
        self.logger.con_open
        query = f"SELECT * FROM Portfolio.`VV.category` WHERE category_id = {id};"
        start_time = time.time()
        connection = self.create_connection()
        cursor = connection.cursor()
        try: 
            with connection.cursor() as cursor:
                cursor.execute(query)
                category = cursor.fetchall()
                self.logger.query(query, f"{category}")
        except pymysql.MySQLError as e:
            self.logger.error(f"unable to get categories: {e}")
        finally:
            cursor.close()
            connection.close()
            end_time = time.time - start_time
            self.logger.con_close(end_time)
            return(category) 
    
    #Function that attempts to query the database to get list of all projects

    #Function that attempts to query the database to get a list of projects for a specific category by ID

    #Function that attempts to query the database to get specific project by ID

    #Function that attempts to query the database to get list of all images

    #Function that attempts to query the database to get a list of projects for a specific category by category ID

    #Function that attempts to query the database to get a list of projects for a specific project by project ID

    #Function that attempts to query the database to get specific image by ID


    