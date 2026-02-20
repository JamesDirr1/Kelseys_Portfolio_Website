import re
import logging
import sys
from flask import current_app, has_app_context


class log(): #A simple logging class that just forces standard message format across the whole project.  
    def __init__(self, tag):
        self.tag = f"[{tag}]"

        if has_app_context():
            self.logger = current_app.logger
        else:
            self.logger = logging.getLogger(tag)
            if not self.logger.handlers:
                stream = logging.StreamHandler(sys.stdout)
                formatter = logging.Formatter(
                    '%(asctime)s %(levelname)-8s| %(message)s'
                )
                stream.setFormatter(formatter)
                self.logger.addHandler(stream)
            self.logger.setLevel(logging.DEBUG)

        self.level = self.logger.getEffectiveLevel()

    def debug(self, message): #Default DEBUG message
        self.logger.debug(f"{self.tag} {message}")

    def info(self, message): #Default INFO message
        self.logger.info(f"{self.tag} {message}")
    
    def error(self, message): #Default ERROR message
        self.logger.error(f"{self.tag} {message}")

    def critical(self, message): #Default CRITICAL message
        self.logger.critical(f"{self.tag} {message}")

    def con_open(self): #Default open database connection message
        self.logger.info(f"{self.tag} ---Connecting to database---")
    
    def con_close(self, time): #Default close database connection message
        self.logger.info(f"{self.tag} ---Connecting Closing---Time: {time:.2f}s---")

    def query(self, query, args, results): #Default query message
        if self.level == 10: #checks if log level is debug
            self.logger.debug(f"{self.tag} Query: {query}\nargs: {args}\n Results:{results}")
        else:
            self.logger.info(f"{self.tag} Query: {query}\nargs: {args}")
    
    def register(self, blueprint): #Default blueprint registration message
        self.logger.info(f"{self.tag} Registering blueprint {blueprint}")
    
    def visit(self, page): #Default site visit message
        self.logger.info(f"{self.tag} User visited page: {page}")
    
    def redirect(self, url): #Default redirect message
        self.logger.info(f"{self.tag} Redirecting user to: {url}")

    def request(self, method, url, headers): #Default request
        self.logger.info(f"{self.tag} Request: {method} {url}")
        if self.level == 10: #checks if level is debug
            self.logger.debug(f"{self.tag} Headers: {dict(headers)}")
    
    def response(self, status, time):
        if re.match(r'^5', status): #Checks if status is of type 500
            self.logger.critical(f"{self.tag} Response status: {status} - Processing time: {time:.2f}s")
        elif re.match(r'^4', status):#Checks if status is of type 400
            self.logger.warning(f"{self.tag} Response status: {status} - Processing time: {time:.2f}s")
        else: 
            self.logger.info(f"{self.tag} Response status: {status} - Processing time: {time:.2f}")
            