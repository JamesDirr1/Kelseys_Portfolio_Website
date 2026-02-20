import os
import time
from typing import Optional, Literal
import pymysql
from dotenv import load_dotenv
from pymysql.cursors import DictCursor
from pymysql.err import OperationalError, MySQLError
from utility_classes.custom_logger import log


class MySQLBase:
    """Base class for all MySQL interactions. Handles creating the database connection and executing query"""

    def __init__(self, user: str, password: str, logger_name: str):
        """Creates base class for interacting with MySQL database.

        :param user: Username for the user from the MySQL database that queries should be executed with.
        :type user: str

        :param password: Password for the MySQL user.
        :type password: str

        :param logger_name: Name to be used when logging function calls.
        :type logger_name: str

        MySQL host, port, database are all pull from env
        """
        load_dotenv()
        self.host = os.getenv("MYSQL_HOST")
        self.port = int(os.getenv("MYSQL_PORT", 3306))
        self.db = os.getenv("MYSQL_DB")
        self.user = user
        self.password = password
        self.logger = log(logger_name)

    def create_connection(self):
        """Creates connection to the a MySQL database

        :return pymysql.connect: A pymysql connection object that is used later to initiate connection to the database.

        :raises OperationalError: pymysql throws a operation error when something is affecting the connection to the database such as network issues.
        :raises MySQLError: pymysql over all error handing, similar to an Exception but specifically for mysql errors.
        :raises Exception: If any uncaught exceptions happens.
        """
        self.logger.debug(f"Creating connection to: {self.host}")
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db,
                cursorclass=DictCursor,
            )
            self.logger.debug("Connection created")
            return connection
        except OperationalError as e:
            self.logger.error(f"Operational error when connecting to the database: {e}")
            raise
        except MySQLError as e:
            self.logger.error(f"Connection failed, could not create connection: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error, could not create connection: {e}")
            raise

    def _run_query(
        self, query: str, args=None, fetch: Optional[Literal["one", "all"]] = None
    ):
        """Core unified query runner used by all non-sensitive helper functions.
        Handles connections, logs, commits, and error handling.

        :param query: Query that needs to be executed.
        :type query: str

        :param args: Parameters used with query. (optional)
        :type args: tuple, list or dict

        :param fetch: "one" to fetch one row, "all" to fetch all rows, None to fetch nothing
        :type fetch: "one", "all", None

        :return: Results of query or row count of executions.
        :rtype: dict | int | None

        :raises ValueError: If 'fetch' is not a valid argument.
        :raises OperationalError: pymysql throws a operation error when something is affecting the connection to the database such as network issues.
        :raises MySQLError: pymysql over all error handing, similar to an Exception but specifically for mysql errors.
        :raises Exception: If any uncaught error happens.
        """
        if fetch not in ("one", "all", None):
            raise ValueError(
                f"Invalid fetch option: {fetch}. Must be 'one', 'all', or None."
            )

        self.logger.con_open()
        start_time = time.time()
        results = None
        connection = None
        cursor = None
        try:
            connection = self.create_connection()
            with connection.cursor() as cursor:
                # Execute query
                if args is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, args)

                # Fetch query
                if fetch == "one":
                    results = cursor.fetchone()
                elif fetch == "all":
                    results = cursor.fetchall()
                else:  # fetch is none
                    results = cursor.rowcount
                    connection.commit()

                return results

        except OperationalError as e:
            self.logger.error(f"Operational error while executing query: {e}")
            raise
        except MySQLError as e:
            self.logger.error(f"MySQL error while executing query: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Exception while executing query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
            self.logger.con_close(time.time() - start_time)

    def fetch_all(self, query: str, args=None):
        """Fetches all results from provided query.

        :param query: Query to execute.
        :type query: str

        :param args: Parameters used with query. (optional)
        :type args: tuple, list or dict

        :return: Results of query
        :rtype: dict | None

        :raises pymysql.MySQLError: When there is an error interacting with the database.
        :raises Exception: If any uncaught error happens.

        If args is a list or tuple, %s can be used as a placeholder in the query.
        If args is a dict, %(name)s can be used as a placeholder in the query.
        """
        results = None
        try:
            results = self._run_query(query, args, "all")
            self.logger.query(query, args, results)
        except MySQLError as e:
            self.logger.error(f"Unable to complete: '{query}'. MySQL error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unable to complete: '{query}'. Unknown Exception {e}")
            raise
        if results is not None and len(results) == 0:
            results = None
        return results

    def fetch_one(self, query: str, args=None):
        """Fetches one result from provided query

        :param query: Query to execute.
        :type query: str

        :param args: Parameters used with query. (optional)
        :type args: tuple, list or dict

        :return: Results of query
        :rtype: dict | None

        :raises pymysql.MySQLError: When there is an error interacting with the database.
        :raises Exception: If any uncaught error happens.

        If args is a list or tuple, %s can be used as a placeholder in the query.
        If args is a dict, %(name)s can be used as a placeholder in the query.
        """
        result = None
        try:
            result = self._run_query(query, args, "one")
            self.logger.query(query, args, result)
        except MySQLError as e:
            self.logger.error(f"Unable to complete: '{query}'. MySQL error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unable to complete: '{query}'. Unknown Exception {e}")
            raise
        if result is not None and len(result) == 0:
            result = None
        return result

    def fetch_all_sensitive(self, query: str, args=None):
        """Fetches all results from provided query but with limited logging
        to avoid logging sensitive data.

        :param query: Query to execute.
        :type query: str

        :param args: Parameters used with query. (optional)
        :type args: tuple, list or dict

        :return: Results of query
        :rtype: dict | None

        :raises pymysql.MySQLError: When there is an error interacting with the database.
        :raises Exception: If any uncaught error happens.

        If args is a list or tuple, %s can be used as a placeholder in the query.
        If args is a dict, %(name)s can be used as a placeholder in the query.
        """
        results = None
        try:
            results = self._run_query(query, args, "all")
            self.logger.query(query, "[REDACTED]", "[REDACTED]")
        except MySQLError as e:
            self.logger.error(f"Unable to complete: '{query}'. MySQL error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unable to complete: '{query}'. Unknown Exception {e}")
            raise
        if results is not None and len(results) == 0:
            results = None
        return results

    def fetch_one_sensitive(self, query: str, args=None):
        """Fetches one results from provided query but with limited logging
        to avoid logging sensitive data.

        :param query: Query to execute.
        :type query: str

        :param args: Parameters used with query. (optional)
        :type args: tuple, list or dict

        :return: Results of query
        :rtype: dict | None

        :raises pymysql.MySQLError: When there is an error interacting with the database.
        :raises Exception: If any uncaught error happens.

        If args is a list or tuple, %s can be used as a placeholder in the query.
        If args is a dict, %(name)s can be used as a placeholder in the query.
        """
        result = None
        try:
            result = self._run_query(query, args, "one")
            self.logger.query(query, "[REDACTED]", "[REDACTED]")
        except MySQLError as e:
            self.logger.error(f"Unable to complete: '{query}'. MySQL error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unable to complete: '{query}'. Unknown Exception {e}")
            raise
        if result is not None and len(result) == 0:
            result = None
        return result

    def execute(self, query, args=None):
        """Executes the provide query to the MySQL database. Does not return results.

        :param query: Query to execute.
        :type query: str

        :param args: Parameters used with query. (optional)
        :type args: tuple, list or dict

        :raises pymysql.MySQLError: When there is an error interacting with the database.
        :raises Exception: If any uncaught error happens.

        If args is a list or tuple, %s can be used as a placeholder in the query.
        If args is a dict, %(name)s can be used as a placeholder in the query.
        """
        try:
            row_count = self._run_query(query, args, None)
            self.logger.query(query, args, f"{row_count} rows affected")
        except pymysql.MySQLError as e:
            self.logger.error(f"Was not able to execute '{query}' {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error when executing query '{query}': {e}")
            raise

    def execute_sensitive(self, query, args=None):
        """Executes the provide query to the MySQL database but with limited logging
        to avoid logging sensitive data. Does not return results.

        :param query: Query to execute.
        :type query: str

        :param args: Parameters used with query. (optional)
        :type args: tuple, list or dict

        :raises pymysql.MySQLError: When there is an error interacting with the database.
        :raises Exception: If any uncaught error happens.

        If args is a list or tuple, %s can be used as a placeholder in the query.
        If args is a dict, %(name)s can be used as a placeholder in the query.
        """
        try:
            row_count = self._run_query(query, args, None)
            self.logger.query(query, "[Redacted]", f"{row_count} rows affected")
        except pymysql.MySQLError as e:
            self.logger.error(f"Was not able to execute '{query}' {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error when executing query '{query}': {e}")
            raise
