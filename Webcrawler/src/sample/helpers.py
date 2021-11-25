import datetime
import linecache
import logging
import os
import pathlib
import sys
import time
from configparser import ConfigParser

#loading config file to read necessary variables
config = ConfigParser()
configFilePath = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'config.ini')
config.read(configFilePath)




class help:

    @staticmethod
    def PrintException():
        """
        Description : This function prints the line number and the error as a stacktrace to the log file
        Returns: stacktrace
        """
        exc_type, exc_obj, tb = sys.exc_info()
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        return 'EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj)


    @staticmethod
    def time_taken(func):
        """
        A wrapper function to record the time taken for a fucntion to run completely
        Input : Decorated function for which we want to see the runtime
        Output : print time taken for the function
        """
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(func.__name__+" took " +
                  str((end-start)*1000) + " mil sec to get executed")
            return result
        return wrapper

    
    @staticmethod
    def get_module_logger(mod_name):
        """
        This function generates the logs 
        """
        dest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs/')
        file_name = datetime.datetime.today().strftime('%d_%m_%Y')
        logger = logging.getLogger(mod_name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(dest_path+file_name+'.log')
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        return logger




logger = help.get_module_logger(__name__)

class write_file(help):
    '''
    Description : To write json file
    parameter : dict/json
    '''

    def __init__(self, *args, **kwargs):
        self.name = kwargs['name']
        self.data = kwargs['json_data']
        self.path = kwargs['path']

    @property
    def write_json(self):
        if not(os.path.isdir(self.path)):
            pathlib.Path(self.path).mkdir(parents=True, exist_ok=True)
        try:
            os.remove(self.path + f"{self.name}.json")
        except FileNotFoundError as ex:
            logger.warn(f'File {self.name} does not exist. Creating a new {self.name}.json')
        finally:
            with open(self.path + f"{self.name}.json", 'w') as f:
                f.write(self.data)
            logger.info(f"{self.name}.json file is created with the updated data")
