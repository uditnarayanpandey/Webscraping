import json

import requests
from retrying import retry
from src.sample.helpers import *

logger = help.get_module_logger(__name__)

class product_client:

    headers = {'Accept': 'application/json'}

    @retry(stop_max_attempt_number=4, wait_fixed=2000)
    def __init__(self, *args, **kwargs):
        try:
            self.r = requests.get(kwargs['url'], headers = self.headers)
            self.r.close()
        except Exception as error:
            logger.error(help.PrintException())
            raise Exception('Something went wrong while loading the record for grades through product_grades_httpclient')


    def get_submission_records(self):
        """
        Get grades data for each product id
        """
        try:
            api = self.r.json()
        except(requests.exceptions.ConnectionError, json.decoder.JSONDecodeError):
            logger.error(help.PrintException())
            raise Exception('Something went wrong while returning the api response in prod_grades_httpclient')
        else:
            return api


if __name__ == '__main__':

    try:
        obj = product_client(url = 'https://Sabic.com/en/productdata/c077b703-e1d8-e611-819b-06b69393ae39')
        print(obj.get_submission_records())
    except Exception as error:
        print(error)
