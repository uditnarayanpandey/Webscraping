#importing important libraries
import json

import requests
from bs4 import BeautifulSoup
from retrying import retry
from src.sample.extract_grades import ExtractGradesInfo as grades_info
from src.sample.helpers import *

logger = help.get_module_logger(__name__)

#defining a class that will extract the product_items from all the products
#example -
''' ========================================================================
Flat Products has several different product_items
1) CRC
2) CRCG
3) CRS ... etc
'''
class ExtractProductItem:
    '''
    This class is used to extract data of products from each product category that was defined in webscraper.py
    '''
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
    
    def scrape_product_items(self, category_name) -> list: #to scrape data from the page
        '''
        Used to extract product_item information that are present under each product
        :param category_name: Name of product category
        :type category_name: string
        '''
        item_data = [] #declaring empty list to store product_item data like its name and link to different grades that falls under these product_items

        result = self.soup.find_all('div', {config['PRODUCT']['KEY_CLASS']: config['PRODUCT']['VALUE_CLASS']})

        if result is None:
            logger.warn("No information present for " + category_name)
        else:
            try:
                for row in result:
                    data = {}
                    data['product_name'] = row.text.replace('\n', '').encode("ascii", "ignore").decode()
                    data['product_link'] = str('https://www.sabic.com'+ row.find('a').get('href'))
                    data.update(grades_info(url= data['product_link']).get_product_info(category_name))
                    logger.info(f"{data['product_name']} is scraped")
                    item_data.append(data)
            except Exception as error:
                logger.error(help.PrintException())
                raise Exception(error)
            return item_data

if __name__ == '__main__':
    try:
        obj = ExtractProductItem(url = 'https://www.sabc.com')
    except Exception as error:
        print(error)
