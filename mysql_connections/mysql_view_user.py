import pymysql, os, time, utility_classes.custom_logger
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
from data_classes.category import Category
from data_classes.project import Project
from data_classes.image import Image
from data_classes.user import User
from werkzeug.security import check_password_hash

#MySQL class that acts as the view user for executing MYSQL queries that are limited to the database views.
#Uses PyMySQL to execute queries. 

class View_User():
    def __init__(self): #Load .env file and set variables need to connect to the mysql database as the View_user.
        load_dotenv
        self.host = os.getenv('MYSQL_HOST')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.user = os.getenv('MYSQL_VIEW_USER')
        self.password = os.getenv('MYSQL_VIEW_USER_PASSWORD')
        self.db = os.getenv('MYSQL_DB')
        self.logger = utility_classes.custom_logger.log("VIEW_USER")
    
    def create_category(self, category): #Function that builds category object from a dic
        self.logger.debug(f"Creating category: {category}")
        category = Category(category_id = category["category_id"],
                            category_title = category["category_title"],
                            category_order = category["category_order"])
        return category
    
    def create_project(self, project): #Function that builds project object from a dic
        self.logger.debug(f"Creating project: {project}")
        project_image = None
        if "image_URL" in project:
            project_image = self.create_image_from_project(project)

        project = Project(project_title = project["project_title"],
                        project_date = project["project_date"],
                        project_desc = project["project_desc"],
                        project_id = project["project_id"],
                        project_image_id = project["project_image_id"],
                        category_id = project["category_id"],
                        project_image = project_image
                        )
        return project

    def create_image_from_project(self, project): #Function that builds image object from a project dic
        if project.get("project_image_id") is None:
            self.logger.debug("Creating 'Null' project image")
            project_image = Image(project_id = project["project_id"], image_weight = 0)
        else: 
            self.logger.debug(f"Creating project image from project: {project}")
            project_image = Image(image_id = project["project_image_id"], 
                                image_title = project["image_title"], 
                                image_desc = project["image_desc"], 
                                image_url = project["image_URL"], 
                                image_weight = project["image_weight"], 
                                project_id = project["project_id"])
        return project_image

    def create_image(self, image): #Function that builds an image object from a dic
        self.logger.debug(f"Creating image: {image}")
        image = Image(image_id = image["image_id"], 
                        image_title = image["image_title"], 
                        image_desc = image["image_desc"], 
                        image_url = image["image_URL"], 
                        image_weight = image["image_weight"], 
                        project_id = image["project_id"])
        return(image)
    
    def create_user(self, user): #function that builds an user object from a dic
        self.logger.debug("Creating user from dic")
        user = User(
            user_id=user["user_id"],
            user_name=user["user_name"],
            user_password=user["user_password"]
        )
        return(user)

    
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
    
    def fetch_all(self, query, args = None): #Function uses provided query to query the database
        self.logger.con_open
        start_time = time.time()
        connection = self.create_connection()
        cursor = connection.cursor()
        try: 
            with connection.cursor() as cursor:
                if args is None:
                    self.logger.debug("args are null")
                    cursor.execute(query)
                else: 
                    self.logger.debug(f"args: f{args}")
                    cursor.execute(query, args)
                results = cursor.fetchall()
                self.logger.query(query, f"{results}")
        except pymysql.MySQLError as e:
            self.logger.error(f"unable to complete: {query}. MySQL error: {e}")
            results = None
        finally:
            connection.close()
            cursor.close()
            end_time = time.time()- start_time
            self.logger.con_close(end_time)
            if results is not None and len(results) == 0:
                results = None 
            self.logger.debug(f"Results: {results}")
            return(results)

    
    def get_all_categories(self, ordered = True): #Function that attempts to query the database to get list of all categories.
        categories = None
        if ordered: #If true get categories ordered by ASC on category_order
            self.logger.info("Getting all categories - Sorted") 
            query = "SELECT * FROM Portfolio.`VV.category` ORDER BY category_order ASC;"
        else:
            self.logger.info("Getting all categories")
            query = "SELECT * FROM Portfolio.`VV.category`;"
        results = self.fetch_all(query)
        categories = []
        if results is not None:
            for result in results:
                categories.append(self.create_category(result))
        return(categories)
    
    def get_category_by_title(self, title): #Function that attempts to query the database to get a list of all categories 
        category = None
        self.logger.info(f"Getting category by {title}")
        args = [title]
        query = "SELECT * FROM Portfolio.`VV.category` WHERE category_title LIKE %s;"
        results = self.fetch_all(query, args)
        if results is not None:
            category = self.create_category(results[0])
        return (category)
        
        
    def get_all_projects(self):#Function that attempts to query the database to get list of all projects
        projects = None
        self.logger.info("Getting all projects")
        query = "SELECT * FROM Portfolio.`VV.project`;"
        results = self.fetch_all(query)
        projects = []
        if results is not None:
            for result in results:
                projects.append(self.create_project(result))
        return (projects)
    
    def get_projects_by_category(self, id, ordered = True):#Function that attempts to query the database to get a list of projects for a specific category by ID
        projects = None
        args = [f"{id}"]
        if ordered: #If true get project order by ASC on project date
            self.logger.info(f"Getting all projects from category {id} - Sorted")
            query = "Select * from `VV.project` as project left join `VV.image` as image on project.project_image_id = image.image_id WHERE category_id = %s ORDER BY project_date ASC;"
        else: 
            self.logger.info(f"Getting all projects from category {id}")
            query = "Select * from `VV.project` as project left join `VV.image` as image on project.project_image_id = image.image_id WHERE category_id = %s;"
        results = self.fetch_all(query, args)
        projects = []
        if results is not None:
            for result in results:
                projects.append(self.create_project(result))
        return (projects)
    
    def get_projects_by_category_title(self, title, ordered = True):#Function that attempts to query the database to get a list of projects for a specific category by title
        projects = None
        args = [title]
        if ordered: #If true get project order by ASC on project date
            self.logger.info(f"Getting all projects from category {title} - Sorted")
            query = "Select * from `VV.project` as project left join `VV.image` as image on project.project_image_id = image.image_id; WHERE category_title LIKE %s ORDER BY project_date ASC;"
        else: 
            self.logger.info(f"Getting all projects from category {title}")
            query = "Select * from `VV.project` as project left join `VV.image` as image on project.project_image_id = image.image_id; WHERE category_title LIKE %s;"
        results = self.fetch_all(query, args)
        projects = []
        if results is not None:
            for result in results:
                projects.append(self.create_project(result))
        return (projects)
    
    def get_project(self, id): #Function that attempts to query the database to get specific project by ID
        project = None
        args = [f"{id}"]
        self.logger.info(f"Getting project {id}")
        query = "SELECT * FROM Portfolio.`VV.project` WHERE project_id = %s;"
        results = self.fetch_all(query, args)
        if results is not None:
            project = self.create_project(results[0])
        return (project)
    
    def get_project_by_title(self, project_title, category_title ): #Function that attempts to query the database to get specific project by title and category
        project = None
        args = [category_title, project_title]
        self.logger.info(f"Getting project:{project_title}  from category:{category_title}")
        query = "SELECT * FROM `VV.project` AS project LEFT JOIN `VV.category` AS category ON category.category_id = project.category_id WHERE category.category_title LIKE %s AND project_title LIKE %s;"
        results = self.fetch_all(query, args)
        if results is not None:
            project = self.create_project(results[0])
        return (project)
    
    def get_all_images(self):#Function that attempts to query the database to get list of all images
        images = None
        self.logger.info("Getting all images")
        query = "SELECT * FROM Portfolio.`VV.image`;"
        results = self.fetch_all(query)
        images = []
        if results is not None:
            for result in results:
                images.append(self.create_image(result))
        return (images)

    def get_project_images(self, id):#Function that attempts to query the database to get a list of images for a specific project by project ID
        images = None
        args = [f"{id}"]
        self.logger.info(f"Getting all images for project {id}")
        query = "SELECT * FROM Portfolio.`VV.image` WHERE project_id = %s ORDER BY image_weight ASC;"
        results = self.fetch_all(query, args)
        images = []
        if results is not None:
            for result in results:
                images.append(self.create_image(result))
        return (images)
    
    def get_image(self, id):#Function that attempts to query the database to get specific image by ID
        image = None
        args = [f"{id}"]
        self.logger.info(f"Getting image {id}")
        query = "SELECT * FROM Portfolio.`VV.image` WHERE image_id = %s;"
        results = self.fetch_all(query, args)
        if results is not None:
            image = self.create_image(results[0])
        return (image)
    
    def check_user_exist_and_password(self, user_name, user_password):#Function that attempts to query a data base for a specific user and if their password matches
        name_match = False
        password_match = False
        self.logger.con_open
        start_time = time.time()
        connection = self.create_connection()
        cursor = connection.cursor()
        query = ("SELECT * FROM `VV.users` WHERE user_name=%s")
        try: 
            with connection.cursor() as cursor:
                self.logger.info(f"Checking if username '{user_name}' exist")
                cursor.execute(query, user_name)
                result = cursor.fetchone()
                self.logger.debug(f"USER RESULTS {result}") #dont use in prod

                if result is None:
                    self.logger.info(f"Unable to find username '{user_name}'")
                    return (name_match, password_match)
            
                db_user = self.create_user(result)

                if  db_user.user_name == user_name:
                    name_match = True

                # If you hashed passwords when saving:
                if check_password_hash(db_user.user_password, user_password):
                    password_match = True
        except pymysql.MySQLError as e:
            self.logger.error(f"unable to complete: {query}. MySQL error: {e}")
        finally:
            connection.close()
            cursor.close()
            end_time = time.time()- start_time
            self.logger.con_close(end_time)

        return (name_match, password_match)
                
    