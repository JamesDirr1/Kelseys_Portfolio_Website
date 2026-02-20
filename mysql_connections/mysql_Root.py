import pymysql, time, os, utility_classes.custom_logger
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from mysql_connections.mysql_base import MySQLBase
from pymysql.err import  MySQLError

# MySQL class that acts as the Root user for executing MYSQL queries that require root level permissions.
# This should only be called when needed.
# Uses PyMySQL to execute queries.


class Root(MySQLBase):
    """Class for interacting with the MySQL database with Root permissions.
    USE WITH CAUTION. SHOULD NOT BE USED FOR WITH USER DATA."""

    def __init__(
        self,
    ):
        """Creates Root user class with set functions to execute set queries to interact with the
        database with admin permissions.
        Inherits from MySQLBase class.
        """
        user = os.getenv("MYSQL_ROOT")
        password = os.getenv("MYSQL_ROOT_PASSWORD")
        super().__init__(user, password, "ROOT")

    def try_connection(self) -> bool:
        """Test the connection to the database and ensures that all need tables are made and ready for use.

        :return: Returns status of database tables
        :rtype: bool
        """
        status = False
        # Set of table names ---Needs Updated if more tables are added--- should prob pull from somewhere
        need_tables = {
            "VV.category",
            "VV.image",
            "VV.project",
            "category",
            "image",
            "project",
            "VV.users",
            "users",
            "site_meta",
            "VV.site_meta",
        }

        self.logger.info("Testing connection to database")
        try:
            # Query the database for a list of all tables.
            tables = self.fetch_all("Show tables;")
            current_tables = {
                table["Tables_in_Portfolio"] for table in tables
            }  # Turns result into a set of tables.
            table_dif = (
                need_tables - current_tables
            )  # Subtracts the tables in the currently in the database.
            self.logger.debug(f"Table Diff: {table_dif}")
            if (
                len(table_dif) == 0
            ):  # Checks if the length of the results of the differences in table sets.
                status = True
                self.logger.info("All tables have been created - Database is ready")
            else:
                self.logger.error(
                    f"Tables do not match. Missing tables: {table_dif}"
                )
        except MySQLError as e:
            self.logger.error(f"An error occurred when trying to connect to database during test. {e}")
            return status
        except Exception as e:
            self.logger.error(f"An Exception was thrown when trying to test database connection. {e}")
            return status
        return status

    def create_db_users(self):
        """Creates need database users and provides them set permissions.

        :raises pymysql.MySQLError: When there is an error interacting with the database.
        :raises Exception: If any uncaught error happens.
        """
        user_list = [
            {
                "user": os.getenv("MYSQL_VIEW_USER"),
                "password": os.getenv("MYSQL_VIEW_USER_PASSWORD"),
                "permissions": [
                    "GRANT SELECT ON `VV.category` TO %s;",
                    "GRANT SELECT ON `VV.project` TO %s;",
                    "GRANT SELECT ON `VV.image` TO %s;",
                    "GRANT SELECT ON `VV.users` TO %s;",
                    "GRANT SELECT ON `VV.site_meta` TO %s;",
                ],
            }
        ]
        for user in user_list:
            try:
                self.logger.info(f"Checking if user '{user.get('user')}' exist.")
                users = self.fetch_all(
                    "SELECT user FROM mysql.user WHERE user = %s;", [user.get("user")]
                )
                if len(users) == 1:
                    self.logger.info(f"User '{user.get('user')}' already exists.")
                else:
                    self.logger.info(
                        f"User '{user.get('user')}' not found, creating user."
                    )
                    self.execute_sensitive(
                        "CREATE USER IF NOT EXISTS %s IDENTIFIED BY %s;",
                        [user.get("user"), user.get("password")],
                    )
                    for permission in user.get("permissions"):
                        self.execute(permission, [user.get("user")])
                    self.execute(
                        "FLUSH PRIVILEGES"
                    )  # used to flush permission additions
            except MySQLError as e:
                self.logger.error(f"Was not able to create database users: {e}")
                raise
            except Exception as e:
                self.logger.error(
                    f"An unexpected error when trying to create database users: {e}"
                )
                raise

    def add_admin_user(self):
        """Adds the web-admin user to the user table in the database. This should not be used in any user facing functions. User credentials are pull from ENV file.

        :raises pymysql.MySQLError: When there is an error interacting with the database.
        :raises Exception: If any uncaught error happens.
        """
        user = os.getenv("ADMIN_USERNAME")
        password = generate_password_hash(os.getenv("ADMIN_PASSWORD"))
        self.logger.info(f"Adding web-admin user '{user}' to the database")

        select_query = "SELECT * FROM `users` WHERE user_name= %s;"
        insert_query = "INSERT INTO `users` (user_name, user_password) VALUES (%s,%s)"
        try:
            self.logger.debug(f"Checking if web-admin '{user}' already exist.")
            result = self.fetch_all_sensitive(select_query, [user])
            
            if len(result) == 1:
                self.logger.info(f"Web-admin '{user}' user already exists")
            else:
                self.logger.debug(
                    f"Web-admin '{user}' user not found, creating to default web-admin account."
                )
                self.execute_sensitive(insert_query, [user, password])
        except MySQLError as e:
            self.logger.error(f"Was not able to create web-admin account: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Was not able to create web-admin account: {e}")
            raise

    def create_test_data(self):
        """DO NOT USE IN PRODUCTION -
        This function should only be used in test environments to fill the database with dummy data.
        """
        query = "select * from `category`;"
        try:
            self.logger.info("Testing if there is already data")
            result = self.fetch_all(query)
            if len(result) == 0:
                self.logger.info("Creating test data")
                self.execute("Call clear_data();")
                self.execute("Call test_data();")
            else:
                self.logger.info("Database already has data")
        except Exception as e:
            self.logger.error(f"Was not able to add test data: {e}")
            raise


