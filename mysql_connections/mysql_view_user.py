import os
import time

import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor
from werkzeug.security import check_password_hash

import utility_classes.custom_logger
from data_classes.category import Category
from data_classes.image import Image
from data_classes.project import Project
from data_classes.user import User

# MySQL class that acts as the view user for executing MYSQL queries that are limited to the database views.
# Uses PyMySQL to execute queries.


class View_User:

    def __init__(  # Load .env file and set variables need to connect to the mysql database as the View_user.
        self,
    ):
        load_dotenv
        self.host = os.getenv("MYSQL_HOST")
        self.port = int(os.getenv("MYSQL_PORT", 3306))
        self.user = os.getenv("MYSQL_VIEW_USER")
        self.password = os.getenv("MYSQL_VIEW_USER_PASSWORD")
        self.db = os.getenv("MYSQL_DB")
        self.logger = utility_classes.custom_logger.log("VIEW_USER")

    def create_connection(  # Function that creates a PyMySQL connection using the variables outlined above.
        self,
    ):
        self.logger.info(f"Creating connection to: {self.host}")
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db,
                cursorclass=DictCursor,
            )
            self.logger.info("Connection created")
            return connection
        except pymysql.MySQLError as e:
            self.logger.error(f"Connection failed, could not create connection: {e}")
            raise  # re-raise so it still fails in calling function
        except Exception as e:
            self.logger.error(f"Unexpected error, could not create connection: {e}")
            raise

    def fetch_all(  # Function uses provided query to query the database
        self, query, args=None
    ):
        self.logger.con_open
        start_time = time.time()
        results = None
        connection = None
        cursor = None
        try:
            connection = self.create_connection()
            with connection.cursor() as cursor:
                if args is None:
                    self.logger.debug("args are null")
                    cursor.execute(query)
                else:
                    self.logger.debug(f"args: {args}")
                    cursor.execute(query, args)
                results = cursor.fetchall()
                self.logger.query(query, f"{results}")
        except pymysql.MySQLError as e:
            self.logger.error(f"Unable to complete: {query}. MySQL error: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error when fetching data from the database: {e}"
            )
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            end_time = time.time() - start_time
            self.logger.con_close(end_time)
        if results is not None and len(results) == 0:
            results = None
        self.logger.debug(f"Results: {results}")
        return results

    def get_all_categories(  # Function that attempts to query the database to get list of all categories.
        self, ordered=True
    ):
        try:
            categories = []
            if ordered:  # If true get categories ordered by ASC on category_order
                self.logger.info("Getting all categories - Sorted")
                query = (
                    "SELECT * FROM Portfolio.`VV.category` ORDER BY category_order ASC;"
                )
            else:
                self.logger.info("Getting all categories")
                query = "SELECT * FROM Portfolio.`VV.category`;"
            results = self.fetch_all(query)
            if results is not None:
                for result in results:
                    try:
                        categories.append(Category.from_dict(result))
                    except Exception as e:
                        self.logger.error(
                            f"Failed to create category from {result} -> {e}"
                        )
                        continue
            return categories
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            raise Exception(f"Failed to get categories: {e}")

    def get_category_by_title(  # Function that attempts to query the database to get a list of all categories.
        self, title
    ):
        try:
            category = None
            self.logger.info(f"Getting category by {title}")
            args = [title]
            query = (
                "SELECT * FROM Portfolio.`VV.category` WHERE category_title LIKE %s;"
            )
            results = self.fetch_all(query, args)
            if results is not None:
                try:
                    category = Category.from_dict(results[0])
                except Exception as e:
                    self.logger.error(
                        f"Failed to create category from {results[0]}: {e}"
                    )
                    return None
            return category
        except Exception as e:
            self.logger.error(f"Failed to get category '{title}': {e}")
            raise Exception(f"Failed to get category '{title}': {e}")

    def get_all_projects(  # Function that attempts to query the database to get list of all projects.
        self,
    ):
        try:
            self.logger.info("Getting all projects")
            query = "SELECT * FROM Portfolio.`VV.project`;"
            results = self.fetch_all(query)
            projects = []
            if results is not None:
                for result in results:
                    try:
                        projects.append(Project.from_dict(result))
                    except Exception as e:
                        self.logger.error(
                            f"Failed to create project from {result}: {e}"
                        )
                        continue
            return projects
        except Exception as e:
            self.logger.error(f"Failed to get all projects: {e}")
            raise Exception(f"Failed to get all projects: {e}")

    def get_projects_by_category(
        self, id, ordered=True
    ):  # Function that attempts to query the database to get a list of projects for a specific category by ID
        try:
            args = [f"{id}"]
            if ordered:  # If true get project order by ASC on project date
                self.logger.info(f"Getting all projects from category {id} - Sorted")
                query = "Select * from `VV.project` as project left join `VV.image` as image on project.project_image_id = image.image_id WHERE category_id = %s ORDER BY project_date ASC;"
            else:
                self.logger.info(f"Getting all projects from category {id}")
                query = "Select * from `VV.project` as project left join `VV.image` as image on project.project_image_id = image.image_id WHERE category_id = %s;"
            results = self.fetch_all(query, args)
            projects = []
            if results is not None:
                for result in results:
                    try:
                        projects.append(Project.from_dict(result))
                    except Exception as e:
                        self.logger.error(
                            f"Failed to create project from {result}: {e}"
                        )
                        continue
            return projects
        except Exception as e:
            self.logger.error(f"Failed to get projects from category {id}: {e}")
            raise Exception(f"Failed to get projects from category {id}: {e}")

    def get_projects_by_category_title(
        self, title, ordered=True
    ) -> (
        list
    ):  # Function that attempts to query the database to get a list of projects for a specific category by title
        try:
            args = [title]
            if ordered:  # If true get project order by ASC on project date
                self.logger.info(
                    f"Getting all projects from category '{title}' - Sorted"
                )
                query = "Select * from `VV.project` as project left join `VV.image` as image on project.project_image_id = image.image_id; WHERE category_title LIKE %s ORDER BY project_date ASC;"
            else:
                self.logger.info(f"Getting all projects from category '{title}'")
                query = "Select * from `VV.project` as project left join `VV.image` as image on project.project_image_id = image.image_id; WHERE category_title LIKE %s;"
            results = self.fetch_all(query, args)
            projects = []
            if results is not None:
                for result in results:
                    try:
                        projects.append(Project.from_dict(result))
                    except Exception as e:
                        self.logger.error(
                            f"Failed to create project from {result}: {e}"
                        )
                        continue
            return projects
        except Exception as e:
            self.logger.error(f"Failed to get projects from category {title}: {e}")
            raise Exception(f"Failed to get projects from category {title}: {e}")

    def get_project(
        self, id
    ):  # Function that attempts to query the database to get specific project by ID
        try:
            project = None
            args = [f"{id}"]
            self.logger.info(f"Getting project by id {id}")
            query = "SELECT * FROM Portfolio.`VV.project` WHERE project_id = %s;"
            results = self.fetch_all(query, args)
            if results is not None:
                try:
                    project = Project.from_dict(results[0])
                except Exception as e:
                    self.logger.error(
                        f"Failed to create project from {results[0]}: {e}"
                    )
                    return None
            return project
        except Exception as e:
            self.logger.error(f"Failed to get project by id {id}: {e}")
            raise Exception(f"Failed to get project by id {id}: {e}")

    def get_project_by_title(
        self, project_title, category_title
    ):  # Function that attempts to query the database to get specific project by title and category
        try:
            project = None
            args = [category_title, project_title]
            self.logger.info(
                f"Getting project: {project_title}  from category: {category_title}"
            )
            query = "SELECT * FROM `VV.project` AS project LEFT JOIN `VV.category` AS category ON category.category_id = project.category_id WHERE category.category_title LIKE %s AND project_title LIKE %s;"
            results = self.fetch_all(query, args)
            if results is not None:
                try:
                    project = Project.from_dict(results[0])
                except Exception as e:
                    self.logger.error(
                        f"Failed to create project from {results[0]}: {e}"
                    )
                    return None
            return project
        except Exception as e:
            self.logger.error(
                f"Failed to get project {project_title} in category {category_title}: {e}"
            )
            raise Exception(
                f"Failed to get project {project_title} in category {category_title}: {e}"
            )

    def get_all_images(
        self,
    ):  # Function that attempts to query the database to get list of all images
        try:
            self.logger.info("Getting all images")
            query = "SELECT * FROM Portfolio.`VV.image`;"
            results = self.fetch_all(query)
            images = []
            if results is not None:
                for result in results:
                    try:
                        images.append(Image.from_dict(result))
                    except Exception as e:
                        self.logger.error(f"Failed to create image from {result}: {e}")
                        continue
            return images
        except Exception as e:
            self.logger.error(f"Failed to get all images: {e}")
            raise Exception(f"Failed to get all images: {e}")

    def get_project_images(
        self, id
    ):  # Function that attempts to query the database to get a list of images for a specific project by project ID
        try:
            args = [f"{id}"]
            self.logger.info(f"Getting all images for project id {id}")
            query = "SELECT * FROM Portfolio.`VV.image` WHERE project_id = %s ORDER BY image_weight ASC;"
            results = self.fetch_all(query, args)
            images = []
            if results is not None:
                for result in results:
                    try:
                        images.append(Image.from_dict(result))
                    except Exception as e:
                        self.logger.error(f"Failed to create image from {result}: {e}")
                        continue
            return images
        except Exception as e:
            self.logger.error(f"Failed to get all images by project id {id}: {e}")
            raise Exception(f"Failed to get all images by project id {id}: {e}")

    def get_image(
        self, id
    ):  # Function that attempts to query the database to get specific image by ID
        try:
            image = None
            args = [f"{id}"]
            self.logger.info(f"Getting image by id {id}")
            query = "SELECT * FROM Portfolio.`VV.image` WHERE image_id = %s;"
            results = self.fetch_all(query, args)
            if results is not None:
                try:
                    image = Image.from_dict(results[0])
                except Exception as e:
                    self.logger.error(f"Failed to create image from {results[0]}: {e}")
                    return None
            return image
        except Exception as e:
            self.logger.error(f"Failed to get image by id {id}: {e}")
            raise Exception(f"Failed to get image by id {id}: {e}")

    def check_user_exist_and_password(
        self, user_name, user_password
    ):  # Function that attempts to query a data base for a specific user and if their password matches
        name_match = False
        password_match = False
        self.logger.con_open
        start_time = time.time()
        connection = None
        cursor = None
        query = "SELECT * FROM `VV.users` WHERE user_name=%s"
        try:
            connection = self.create_connection()
            with connection.cursor() as cursor:
                self.logger.info(f"Checking if username '{user_name}' exist")
                cursor.execute(query, user_name)
                result = cursor.fetchone()
                self.logger.debug(f"USER RESULTS {result}")  ###DONT USE IN PROD###

                if result is None:
                    self.logger.info(f"Unable to find username '{user_name}'")
                    return (name_match, password_match)
                try:
                    db_user = User.from_dict(result)
                except Exception as e:
                    self.logger.error(f"Unable to create user {user_name}: {e}")
                    e.args = (f"Unable to create user {user_name}: {e}",)
                    raise

                if db_user.user_name == user_name:
                    name_match = True
                    # Compares password to hash
                    self.logger.info(f"Checking if username '{user_name}' entered password matches hashed")
                    if check_password_hash(db_user.user_password, user_password):
                        password_match = True
        except pymysql.MySQLError as e:
            self.logger.error(f"Unable to complete: {query}. MySQL error: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error when trying to get user login: {e}"
            )
            raise Exception ("Unable to validate user at this time")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            end_time = time.time() - start_time
            self.logger.con_close(end_time)
        return (name_match, password_match)
