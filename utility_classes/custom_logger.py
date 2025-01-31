import re
from flask import current_app


class log(): #A simple logging class that just forces standerd message format across the whole project.  
    def __init__(self, tag):
        self.tag = f"[{tag}]"
        self.level = current_app.logger.getEffectiveLevel()

    def debug(self, message): #Defualt DEBUG message
        current_app.logger.debug(f"{self.tag} {message}")

    def info(self, message): #Defualt INFO message
        current_app.logger.info(f"{self.tag} {message}")
    
    def error(self, message): #Default ERROR message
        current_app.logger.error(f"{self.tag} {message}")

    def crtical(self, message): #Default CRITICAL message
        current_app.logger.critical(f"{self.tag} {message}")

    def con_open(self): #Default open database connection message
        current_app.logger.info(f"{self.tag} ---Connecting to database---")
    
    def con_close(self, time): #Default close database connection message
        current_app.logger.info(f"{self.tag} ---Connecting Closing---Time: {time:.2f}s---")

    def query(self, message, results): #Default query message
        if self.level == 10: #checks if log level is debug
            current_app.logger.debug(f"{self.tag} Querying the databse: {message} \n ----Results---- \n {results}")
        else:
            current_app.logger.info(f"{self.tag} Querying the databse: {message}")
    
    def register(self, blueprint): #Defualt blueprint registation message
        current_app.logger.info(f"{self.tag} Registering blueprint {blueprint}")
    
    def visit(self, page): #Default site visit message
        current_app.logger.info(f"{self.tag} User visited page: {page}")
    
    def redirect(self, url): #Defualt redirect message
        current_app.logger.info(f"{self.tag} Redirecting user to: {url}")
   
    def request(self, method, url, headers): #Defualt request
        current_app.logger.info(f"{self.tag} Request: {method} {url}")
        if self.level == 10: #checks if level is debug
            current_app.logger.debug(f"{self.tag} Headers: {dict(headers)}")
    
    def response(self, status, time):
        if re.match(r'^5', status): #Checks if status is of type 500
            current_app.logger.critical(f"{self.tag} Response status: {status} - Processing time: {time:.2f}s")
        elif re.match(r'^4', status):#Checks if status is of type 400
            current_app.logger.warning(f"{self.tag} Response status: {status} - Processing time: {time:.2f}s")
        else: 
            current_app.logger.info(f"{self.tag} Response status: {status} - Processing time: {time:.2f}")
            