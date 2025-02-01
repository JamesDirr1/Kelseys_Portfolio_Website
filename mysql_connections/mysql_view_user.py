import pymysql, os, time, utility_classes.custom_logger
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

class View_User():
    def __init__(self): #Load .env file and set variables need to connect to the mysql database as the View_user.
        load_dotenv
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
    
    def fetch_all(self, query): #Function uses provided query to query the database
        self.logger.con_open
        start_time = time.time()
        connection = self.create_connection()
        cursor = connection.cursor()
        try: 
            with connection.cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                self.logger.query(query, f"{results}")
        except pymysql.MySQLError as e:
            self.logger.error(f"unable to complete: {query}. MySQL error: {e}")
            results = None
        finally:
            connection.close()
            cursor.close()
            end_time = time.time - start_time
            self.logger.con_close(end_time)
            self.logger.debug(f"Results: {results}")
            return(results)

    
    def get_all_categories(self): #Function that attempts to query the database to get list of all categories.
        self.logger.info("Getting all categories")
        query = "SELECT * FROM Portfolio.`VV.category`;"
        results = self.fetch_all(query)
        return(results)
        
    def get_categories_ordered(self):#Function that attempts to query the database to get list of all categories sorted by order
        self.logger.info("Getting all categories - Sorted")
        query = "SELECT * FROM Portfolio.`VV.category` ORDER BY category_order ASC;"
        results = self.fetch_all(query)
        return (results)
        
    def get_category(self, id):#Function that attempts to query the database to get specific category by ID
        self.logger.info(f"Getting category {id}")
        query = f"SELECT * FROM Portfolio.`VV.category` WHERE category_id = {id};"
        results = self.fetch_all(query)
        return (results)
    
    def get_all_projects(self):#Function that attempts to query the database to get list of all projects
        self.logger.info("Getting all projects")
        query = "SELECT * FROM Portfolio.`VV.project`;"
        results = self.fetch_all(query)
        return (results)
    
    def get_projects_by_category(self, id, sort):#Function that attempts to query the database to get a list of projects for a specific category by ID
        if sort:
            self.logger.info(f"getting all projects from category {id} - Sorted")
            query = f"SELECT * FROM Portfolio.`VV.project` WHERE category_id = {id} ORDER BY project_date ASC;"
        else: 
            self.logger.info(f"getting all projects from category {id}")
            query = f"SELECT * FROM Portfolio.`VV.project` WHERE category_id = {id};"
        results = self.fetch_all(query)
        return (results)
    
    def get_project(self, id):#Function that attempts to query the database to get specific project by ID
        self.logger.info(f"getting project {id}")
        query = f"SELECT * FROM Portfolio.`VV.project` WHERE project_id = {id};"
        results = self.fetch_all(query)
        return (results)
    
    def get_all_images(self):#Function that attempts to query the database to get list of all images
        self.logger.info("getting all images")
        query = "SELECT * FROM Portfolio.`VV.image`;"
        results = self.fetch_all(query)
        return (results)

    def get_project_images(self, id):#Function that attempts to query the database to get a list of images for a specific project by project ID
        self.logger.info(f"getting all images for project {id}")
        query = f"SELECT * FROM Portfolio.`VV.image` WHERE project_id = {id} ORDER BY image_weight ASC;"
        results = self.fetch_all(query)
        return (results)
    
    def get_image(self, id):#Function that attempts to query the database to get specific image by ID
        self.logger.info(f"getting image {id}")
        query = f"SELECT * FROM Portfolio.`VV.image` WHERE image_id = {id};"
        results = self.fetch_all(query)
        return (results)

    