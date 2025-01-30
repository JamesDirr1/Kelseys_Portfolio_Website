import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv
import os
from flask import current_app

#MySQL class that acts as the Root user for executing MYSQL querries that require root level premisons.
#This should only be called when needed.
#Uses PyMySQL to execure querries. 

class Root():
    def __init__(self):
        #Load .env file and set variables need to connect to the mysql database as the root user. 
        load_dotenv()
        self.host = os.getenv('MYSQL_HOST')
        self.port = int(os.getenv('MYSQL_PORT', 3306))
        self.user = os.getenv('MYSQL_ROOT')
        self.password = os.getenv('MYSQL_ROOT_PASSWORD')
        self.db = os.getenv('MYSQL_DB')
        self.view_user = os.getenv('MYSQL_VIEW_USER')
        self.view_user_password = os.getenv('MYSQL_VIEW_USER_PASSWORD')

    def create_connection(self): #Function that creates a PyMySQL connection using the variables outlined above
        current_app.logger.info("<ROOT> Connection created")
        connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.db,
            cursorclass=DictCursor
        )
        return connection
    
    def try_connection(self): #Function that attempts to conenct to the database to ensure that it is ready to go.
        status = False
        #Set of table names ---Needs Updated if more tables are added---
        need_tables = {'VV.category', 'VV.image',
                       'VV.project', 'category',
                        'image', 'project'}
        
        current_app.logger.info("<ROOT> Testing connections to the database")
        current_app.logger.info("<ROOT> Connectionn Opening")
        connection = self.create_connection()
        cursor = connection.cursor()
        try:
            with connection.cursor() as cursor:
                current_app.logger.debug("Show tables;") 
                cursor.execute("Show tables;") #Query the database for a list of all tables.
                tables = cursor.fetchall()
                current_tables = {table['Tables_in_Portfolio'] for table in tables} #Turns result into a set of tables.
                current_app.logger.debug(f"<ROOT> Tables: {current_tables}")
                table_dif = need_tables - current_tables #Subtracts the tables in the currently in the database.
                current_app.logger.debug(f"<ROOT> DIFF: {table_dif}")
                if len(table_dif) == 0: #Checks if the length of the results of the diffrents in table sets. 
                    status = True
                    current_app.logger.info("<ROOT> All tables are in the database")
                else:
                    current_app.logger.error(f"<ROOT> Tables do not match. Missing tables: {table_dif}")
        except pymysql.MySQLError as e:
            current_app.logger.error(f"<ROOT> Unable to connect to server: {e}")
        finally:
            cursor.close()
            connection.close()
            current_app.logger.info("<Root> Connection to the database closing")
            return(status) #Returns status True if all tables made, false other wise. 



    def create_users(self): #Function that creates any other users need in the database. 
        current_app.logger.info("<ROOT> Connection to DB Starting")
        connection = self.create_connection()
        cursor = connection.cursor()
        queries = [ #List of queries that need executed when making the users.
                   f"GRANT SELECT ON `VV.category` TO '{self.view_user}'@'%';",
                   f"GRANT SELECT ON `VV.project` TO '{self.view_user}'@'%';",
                   f"GRANT SELECT ON `VV.image` TO '{self.view_user}'@'%';",
                   "FLUSH PRIVILEGES;"
                   ]
        try: 
            with connection.cursor() as cursor:
                current_app.logger.info(f"<ROOT> Createing Users")
                #Specficaly execute create user queery so that password is not logged. 
                cursor.execute(f"CREATE USER IF NOT EXISTS 'View_User'@'%' IDENTIFIED BY '{self.view_user_password}';")
                current_app.logger.debug("<ROOT> CREATE USER IF NOT EXISTS 'View_User'@'%' IDENTIFIED BY 'view_user_password';")
                for query in queries: #Loops through querries and excutes one at a time. 
                     current_app.logger.debug(f"<ROOT> {query}")
                     cursor.execute(query)
                connection.commit
        except pymysql.MySQLError as e:
                current_app.logger.error(f"<ROOT> Was not able to create users: {e}")
        finally:
             current_app.logger.info("<ROOT> Conneciton to DB CLOSING")
             cursor.close()
             connection.close()
