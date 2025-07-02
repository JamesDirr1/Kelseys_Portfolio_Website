import pymysql, time, os, utility_classes.custom_logger
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

#MySQL class that acts as the Root user for executing MYSQL queries that require root level permissions.
#This should only be called when needed.
#Uses PyMySQL to execute queries. 

class Root():
    def __init__(self): #Load .env file and set variables need to connect to the mysql database as the root user. 
        load_dotenv()
        self.host = os.getenv('MYSQL_HOST')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.user = os.getenv('MYSQL_ROOT')
        self.password = os.getenv('MYSQL_ROOT_PASSWORD')
        self.db = os.getenv('MYSQL_DB')
        self.view_user = os.getenv('MYSQL_VIEW_USER')
        self.view_user_password = os.getenv('MYSQL_VIEW_USER_PASSWORD')
        self.logger = utility_classes.custom_logger.log("ROOT")

    def create_connection(self): #Function that creates a PyMySQL connection using the variables outlined above
        self.logger.info(f"Creating connection to: {self.host}")
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db,
                cursorclass=DictCursor
            )
            self.logger.info("Connection created")
            return connection
        except pymysql.MySQLError as e:
            self.logger.error(f"Connection failed, could not create connection: {e}")
            raise  # re-raise so it still fails in calling function
        except Exception as e:
            self.logger.error(f"Unexpected error, could not create connection:: {e}")
            raise
    
    def try_connection(self): #Function that attempts to connect to the database to ensure that it is ready to go.
        status = False
        #Set of table names ---Needs Updated if more tables are added---
        need_tables = {'VV.category', 'VV.image',
                       'VV.project', 'category',
                        'image', 'project',
                        'VV.users', 'users'}
        
        self.logger.info("Testing connection to database Root Class")
        start_time = time.time()
        self.logger.con_open()
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            with connection.cursor() as cursor:
                cursor.execute("Show tables;") #Query the database for a list of all tables.
                tables = cursor.fetchall()
                self.logger.query("Show tables;", f"{tables}")
                current_tables = {table['Tables_in_Portfolio'] for table in tables} #Turns result into a set of tables.
                table_dif = need_tables - current_tables #Subtracts the tables in the currently in the database.
                self.logger.debug(f"Table Diff: {table_dif}")
                if len(table_dif) == 0: #Checks if the length of the results of the differences in table sets. 
                    status = True
                    self.logger.info("All tables have been created - Database is ready")
                else:
                    self.logger.error(f"Tables do not match. Missing tables: {table_dif}")
        except pymysql.MySQLError as e:
            self.logger.error(f"Unable to connect to server: {e}")
        finally:
            cursor.close()
            connection.close()
            end_time = time.time() - start_time
            self.logger.con_close(end_time)
            return(status) #Returns status True if all tables made, false other wise. 



    def create_users(self): #Function that creates any other users need in the database. 
        self.logger.info("Creating users")
        self.logger.con_open()
        start_time = time.time()
        connection = self.create_connection()
        cursor = connection.cursor()
        queries = [ #List of queries that need executed when making the users.
                   f"GRANT SELECT ON `VV.category` TO '{self.view_user}'@'%';",
                   f"GRANT SELECT ON `VV.project` TO '{self.view_user}'@'%';",
                   f"GRANT SELECT ON `VV.image` TO '{self.view_user}'@'%';",
                   f"GRANT SELECT ON `VV.users` TO '{self.view_user}'@'%';",
                   "FLUSH PRIVILEGES;"
                   ]
        try: 
            with connection.cursor() as cursor:
                self.logger.info(f"Checking if user {self.view_user} exist")
                cursor.execute(f"SELECT user FROM mysql.user WHERE user = '{self.view_user}';")
                users = cursor.fetchall()
                self.logger.query(f"SELECT user FROM mysql.user WHERE user = '{self.view_user}';", users)
                if len(users) == 1:
                    self.logger.info("Users already exist")
                else:
                    self.logger.info("Creating Users")
                    #Specifically execute create user query so that password is not logged. 
                    cursor.execute(f"CREATE USER IF NOT EXISTS 'View_User'@'%' IDENTIFIED BY '{self.view_user_password}';")
                    self.logger.debug("CREATE USER IF NOT EXISTS 'View_User'@'%' IDENTIFIED BY 'view_user_password';")
                    for query in queries: #Loops through queries and executes one at a time. 
                        self.logger.debug(f"{query}")
                        cursor.execute(query)
                    connection.commit
        except pymysql.MySQLError as e:
                self.logger.error(f"Was not able to create users: {e}")
        finally:
             cursor.close()
             connection.close()
             end_time = time.time() - start_time
             self.logger.con_close(end_time)
    
    def add_admin_user(self):
        user = os.getenv('ADMIN_USERNAME')
        self.logger.info(f'Adding admin user {user} to the database')
        query = f"SELECT * FROM `users` WHERE user_name= '{user}';"
        self.logger.con_open()
        start_time = time.time()
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                users = cursor.fetchall()
                self.logger.query(query, users)
                if len(users) == 1:
                    self.logger.info(f"Admin user {user} already exist")
                else:
                    self.logger.info(f'Adding admin user does not exist adding base admin account')
                    password = os.getenv('ADMIN_PASSWORD')
                    password = generate_password_hash(password)
                    cursor.execute(f"INSERT INTO users (user_name, user_password) VALUES (%s,%s)", (user, password))
                    connection.commit()
        except pymysql.MySQLError as e:
            self.logger.error(f"Was not able to create admin account: {e}")
        finally:
            cursor.close()
            connection.close()
            end_time = time.time() - start_time
            self.logger.con_close(end_time)


    def create_test_data(self): # DO NOT USE IN PROD - Function used to fill database with test data. 
        self.logger.con_open()
        start_time = time.time()
        connection = self.create_connection()
        cursor = connection.cursor()
        query = "select * from `category`;"
        test_data = "Call clear_data(); Call test_data();"
        try:
            with connection.cursor() as cursor:
                self.logger.info("Testing if there is already data")
                cursor.execute(query)
                result = cursor.fetchall()
                self.logger.query(query, result)
                if len(result) == 0: #Check if there is any data already in the database
                    self.logger.info("Creating test data") 
                    cursor.execute("Call clear_data();")
                    cursor.execute("Call test_data();")
                    connection.commit()
                    self.logger.debug(test_data)
                else:
                    self.logger.info("Database already has data")
        except pymysql.MySQLError as e:
            self.logger.error(f"Was not able to add test data: {e}")
        finally:
            cursor.close()
            connection.close()
            end_time = time.time() - start_time
            self.logger.con_close(end_time)

