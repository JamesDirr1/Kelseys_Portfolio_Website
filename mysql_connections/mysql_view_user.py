import os
from typing import Optional, Tuple
from werkzeug.security import check_password_hash
from mysql_connections.mysql_base import MySQLBase
from data_classes.category import Category
from data_classes.image import Image
from data_classes.project import Project
from data_classes.user import User


class View_User(MySQLBase):
    """Class for interacting with the MySQL database with view(read) only permissions"""

    def __init__(self):
        """Creates View user class with set functions to execute set queries to get data from the database.
        Inherits from the MySQLBase class"""
        user = os.getenv("MYSQL_VIEW_USER")
        password = os.getenv("MYSQL_VIEW_USER_PASSWORD")
        super().__init__(user, password, "VIEW_USER")

    def get_all_categories(self, ordered: bool = True) -> list[Category]:
        """Returns a list of all Categories from the database or an empty list if none are found.

        :param ordered: (Default: True) If true returns Categories stored by category_order.
        :type ordered: Bool
        :return: A list of category objects that can be empty.
        :rtype: List[Category]
        :raises Exception: If there is any error in getting the list of categories from the database.
        """
        try:
            if ordered:
                self.logger.info("Getting all categories - Sorted")
                query = (
                    "SELECT * FROM Portfolio.`VV.category` ORDER BY category_order ASC;"
                )
            else:
                self.logger.info("Getting all categories")
                query = "SELECT * FROM Portfolio.`VV.category`;"
            results = self.fetch_all(query)
            categories: list[Category] = []
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

    def get_category_by_title(self, title: str) -> Optional[Category]:
        """Returns Categories object if one with the same title provided is found in the database, otherwise returns None.

        :param title: Title of Category to pull from database.
        :type title: str
        :return: Category object from the database with from the provided title.
        :rtype: Category or None
        :raises Exception: If there is any error in getting the category from the database.
        """
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

    def get_all_projects(self) -> list[Project]:
        """Returns a list of all Projects from the database or an empty list if none are found.

        :return: A list of Project objects can be empty.
        :rtype: List[Project]
        :raises Exception: If there is any error in getting projects from the database.
        """
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

    def get_projects_by_category(self, id: int, ordered: bool = True) -> list[Project]:
        """Returns a list of all Projects from the database from provided Category or an empty list if none are found.

        :param id: ID of parent category.
        :type id: int
        :param ordered: (Default: True) If true returns Projects stored by project_date.
        :type ordered: bool
        :return: A list of Project objects can be empty.
        :rtype: List[Project]
        :raises Exception: If there is any error in getting projects from the database.
        """
        try:
            args = [id]
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
        self, title: str, ordered: bool = True
    ) -> list[Project]:
        """Returns a list of all Projects from the database from provided Category or an empty list if none are found.

        :param tile: Title of the parent category.
        :type title: str
        :param ordered: (Default: True) If true returns Projects stored by project_date.
        :type ordered: Bool
        :return: A list of Project objects can be empty.
        :rtype: List[Project]
        :raises Exception: If there is any error in getting projects from the database.
        """
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

    def get_project(self, id: int) -> Optional[Project]:
        """Returns a Project object if one with the same id provided is found in the database, otherwise returns None.

        :param id: Id of project.
        :type id: int
        :return:  A project object of the same ID from the database.
        :rtype: Project or None
        :raises Exception: If there is any error in getting the project from the database.
        """
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

    def get_project_by_title(self, project_title: str, category_title: str):
        """Returns a Project object if one with the same title provided and category title is found in the database. Otherwise returns None.

        :param project_title: Title of project.
        :type project_title: str
        :param category_title: Title of the category the project should be in.
        :type category_title: str
        :return:  A project object of the same title from the database.
        :rtype: Project or None
        :raises Exception: If there is any error in getting the project from the database.
        """
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

    def get_all_images(self) -> list[Image]:
        """Returns a list of all Images from the database or an empty list if none are found.

        :return:  A list of Image objects can be empty.
        :rtype: list[Image]
        :raises Exception: If there is any error in getting Images from the database.
        """
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

    def get_project_images(self, id: int) -> list[Image]:
        """Returns a list of all Images for a specific project base on project id or an empty list if none are found.

        :param id: ID of project
        :type id: Int
        :return:  A list of Image objects can be empty.
        :rtype: list[Image]
        :raises Exception: If there is any error in getting Images from the database.
        """
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

    def get_image(self, id: int) -> Optional[Image]:
        """Returns a Image object if one with the same id provided is found in the database, otherwise returns None.

        :param id: ID of Image
        :type id: Int
        :return:  A image object with the same ID from the database.
        :rtype: Image or None
        :raises Exception: If there is any error in getting the Image from the database.
        """
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
        self, user_name: str, user_password: str
    ) -> Tuple[bool, bool]:
        """Returns a bool value for if the provided user name or password exists and matches in the database.

        :param user_name: username to check.
        :type user_name: str
        :param user_password: users password that is hashed and compared to hashed password from database.
        :type user_password: str
        :return:  A tuple of two bool values the first for user name the second for password.
        :rtype: Tuple[bool, bool]
        :raises Exception: If there is any error in getting the user from the database.
        """
        name_match = False
        password_match = False
        query = "SELECT * FROM `VV.users` WHERE user_name=%s"
        try:
            self.logger.info(f"Checking if username '{user_name}' exist")
            result = self.fetch_all_sensitive(query, user_name)
            if result is None:
                self.logger.info(f"Unable to find username '{user_name}'")
                return (name_match, password_match)
            try:
                db_user = User.from_dict(result[0])  # creates user from query data
            except Exception as e:
                self.logger.error(f"Unable to create user '{user_name}': {e}")
                e.args = (f"Unable to create user '{user_name}': {e}",)
                raise

            if db_user.user_name == user_name:
                name_match = True
                # Compares password to hash
                self.logger.info(
                    f"Checking if username '{user_name}' entered password matches hashed"
                )
                if check_password_hash(db_user.user_password, user_password):
                    password_match = True
        except Exception as e:
            self.logger.error(f"Unexpected error when trying to get user login: {e}")
            raise Exception("Unable to validate user at this time")
        return (name_match, password_match)
