#importing important libraries
import json

import requests
from bs4 import BeautifulSoup
from retrying import retry
from src.sample.extract_product import ExtractProductItem as extract_items
from src.sample.helpers import *

logger = help.get_module_logger(__name__)

#defining a class that will extract the products from all the product categories
#example -
# ========================================
# Metal has two different product families
# 1) Flat products
# 2) Long products
# ========================================

class ExtractProductFamily:

    @retry(stop_max_attempt_number=4, wait_fixed=2000)
    def __init__(self, *args, **kwargs): # to get the url

        try:
            page = requests.get(kwargs['url'])
            page.close()
        except (requests.exceptions.ConnectionError , requests.exceptions.ChunkedEncodingError, json.decoder.JSONDecodeError):
            logger.warning("Error encountered while connecting to url : " + kwargs['url'] + ', retrying again')
            logger.error(help.PrintException())
            raise Exception("Some issue faced while loading the page for family")
        else:
            logger.info("Connection has been successfully setup for extracting family information")
            self.url = kwargs['url']
            self.soup = BeautifulSoup(page.content, 'html.parser')


    def scrape_product_family(self, category_name) -> list: #this function returns the list
        '''
        Scrapes and returns a list  with product family information like family name, description, link and product information

        :param category_name: Name of the product category e.g. Polymers, Metals, Specialties etc
        :type category_name: string
        '''

        product_data = [] #declaring empty list to store product data like its name, description, and link to product_items
        divtag = self.soup.find('div', {config['PRODUCT_FAMILY']['KEY_CLASS']: config['PRODUCT_FAMILY']['VALUE_CLASS']})
        if divtag is None:
            logger.warn("No Products are present" + self.url)


        try :
            for row in divtag.find_all('div', {'class':'row'}):
                data = {}
                data['family_name'] = row.find('h3').text.encode("ascii", "ignore").decode()
                data['family_description'] = row.find('p').text.encode("ascii", "ignore").decode()
                data['family_link'] = str('https://www.sabic.com'+ row.find('a').get('href'))
                data['product'] = extract_items(url ='https://www.sabic.com'+ row.find('a').get('href')).scrape_product_items(category_name)
                logger.info(f"{data['family_name']} family is scrapped")
                product_data.append(data)
        except Exception as error:
            logger.error(help.PrintException())
            raise Exception(error)
        else:
            return product_data

if __name__ == '__main__':
    obj = ExtractProductFamily(url = 'https://www.sabic.com/en/products/metals')
    obj.scrape_product_family('Metals')


