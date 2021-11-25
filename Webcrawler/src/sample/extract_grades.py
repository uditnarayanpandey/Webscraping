import json
import os
import re

import requests
from bs4 import BeautifulSoup
from retrying import retry
from src.sample.helpers import *
from src.sample.prod_grades_httpclient import product_client

logger = help.get_module_logger(__name__)

class ExtractGradesInfo:

    @retry(stop_max_attempt_number=4, wait_fixed=2000)
    def __init__(self, *args, **kwargs):  #to get the url
        try:
            self.page = requests.get(kwargs['url'])
            self.page.close()
        except (requests.exceptions.ConnectionError , requests.exceptions.ChunkedEncodingError, json.decoder.JSONDecodeError):
            logger.error("Error encountered while connecting to url : " + kwargs['url'] + ', retrying again')
            logger.error(help.PrintException())
            raise Exception("Some issue faced while loading the page for grades")
        else:
            self.url = kwargs['url']
            self.soup = BeautifulSoup(self.page.content, 'html.parser')             # Creating an object for BeautifulSoup


    @retry(stop_max_attempt_number=4, wait_fixed=2000)
    def __init__(self, *args, **kwargs):  #to get the url
        try:
            page = requests.get(kwargs['url'])
            page.close()
        except (requests.exceptions.ConnectionError , requests.exceptions.ChunkedEncodingError, json.decoder.JSONDecodeError):
            logger.error("Error encountered while connecting to url : " + kwargs['url'] + ', retrying again')
            logger.error(help.PrintException())
            raise Exception("Some issue faced while loading the page for products")
        else:
            self.url = kwargs['url']
            self.soup = BeautifulSoup(page.content, 'html.parser')



    @retry(stop_max_attempt_number=4, wait_fixed=2000)
    def generate_grades_data(self, product_id, category_name):
        """
        Based on the product id and category name, this function generates grades level data for each product. It also
        writes as well as returns the same data in json format

        :param product_id: id of the product whose grades data is requireda
        :type product_id: string
        :param category_name: name of the product category e.g: Polymer, Metals etc
        :type category_name: string
        """
        dest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), f'data/{category_name}/')
        try:
            r = requests.get(f'https://Sabic.com/en/productdata/{product_id}')
            r.close()
        except Exception as error:
            logger.error(help.PrintException(), 'retrying again....')
            raise Exception('Something went wrong while loading the Grade JSON')
        else:
            json_api = json.dumps(r.json(), indent = 4)
            write_file(json_data = json_api, name = product_id , path = dest_path).write_json
            return r.json()


    def get_total_grades(func):
        """
        returns total number of grades available
        """
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            try:
                total_info = product_client(url = 'https://www.sabic.com/en/productdata/' + result['product_id']).get_submission_records()
            except Exception as error:
                logger.error(help.PrintException())
                raise Exception(error)
            total_grades = len(total_info['grades'])
            result['total_grades'] = total_grades
            return result
        return wrapper


    @get_total_grades
    def get_product_info(self, category_name):
        """
        Returns product id
        :param category_name: name of product category
        :type category_name: string
        """
        prod_info = {}
        href = self.soup.find('a', {config['GRADE_PRODUCT_ID']['KEY_CLASS'] :config['GRADE_PRODUCT_ID']['VALUE_CLASS']}).get('href')
        regex = re.match('.*productID=([A-Za-z0-9-]+)', href)
        prod_info['product_id'] = regex.group(1)
        try:
            prod_info['related_products'] = [re_prod.text.encode("ascii", "ignore").decode() for re_prod in self.soup.find('div', {'id':'related-products'}).find_all('a')]
        except Exception as ex:
            logger.warning("There are no releated products available for {0}".format(prod_info['product_id']))
            prod_info['related_products'] = None
        self.generate_grades_data(regex.group(1), category_name)
        return prod_info

if __name__ == '__main__':
    try: 
        obj = ExtractGradesInfo(url = 'https://www.sabic.com/en/products/metals/flat-product/crc')
        obj.get_product_info('Metals')
    except Exception as error:
        print(error)

