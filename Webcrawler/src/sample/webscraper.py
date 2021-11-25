#importing required libraries
import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from retrying import retry
from src.sample.extract_product_family import ExtractProductFamily as extract
from src.sample.helpers import *
from src.sample.updatesheet import UpdateDatasheets

logger = help.get_module_logger(__name__)

class main_scraper:

        #Setting the configuaration path for writing data (later will be placed into config file)
        dest_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data/')
        
        #inititating Beautifulsoup to load the content of the webpage and then closing the request
        @retry(stop_max_attempt_number=4, wait_fixed=2000)
        def html_content(self, url):
                """
                Requests web page and returns content of the page in beautiful soup format
                :param url: Webpage url
                :type url: string
                """

                session = requests.Session()
                try:
                        r = session.get(url)
                        htmlContent = r.content
                        r.close()
                #checking for HTTP error exception
                except requests.exceptions.HTTPError as http_error:
                        logger.error(help.PrintException())
                        raise Exception(f'HTTP error occured, exception caught {http_error}')

                #checking invalid URL exception
                except requests.exceptions.MissingSchema as ms_error:
                        logger.error(help.PrintException())
                        raise Exception(f'URL not valid, exception caught {ms_error}')

                except (requests.exceptions.ConnectionError , requests.exceptions.ChunkedEncodingError, json.decoder.JSONDecodeError):
                        logger.error(help.PrintException())
                        raise Exception("Connection Error/Chuncked Encoding Error/ JSONDecode Error")

                #Checking other exceptions
                except Exception as err:
                        logger.error(help.PrintException())
                        raise Exception(f'Other Error : {err}')
                else:
                        
                        self.soup = BeautifulSoup(htmlContent, 'html.parser')
                        logger.info('Request successfully connected to website')
                        return (r,self.soup)



        #Defining a function to update the datasheet's grade and document information
        def Update_Datasheets(self, file_name):
                '''
                Iterate through all the files from the folder to update the Document and other information of the JSON
                :param file: name of the folder where product.JSON is stored
                :type file: string
                '''
                update_path =  self.dest_path + f'{file_name}/'
                for file in os.listdir(update_path):
                        logger.info(f'Updating {file} {"="*15}{">"}')
                        json_object = None
                        with open(update_path + file, 'r+') as f:
                                json_object = json.load(f)
                        if len(json_object['grades']) > 0:
                                grades_initial = json_object['grades']
                                new_grades = []
                                for grade in grades_initial:
                                        grade['documents']= UpdateDatasheets().get_grade_details(grade_id = grade['id'])
                                        grade['applications'] = list([list_val[0]['title'] for id in grade['applications'] if len(list_val := list(filter(lambda x: x['id'] == id, json_object['applications']))) > 0]) if (len(grade['applications'])) > 0 else None
                                        grade['processingTechniques'] = list([list_val[0]['title'] for id in grade['processingTechniques'] if len( list_val := list(filter(lambda x: x['id'] == id, json_object['processingTechniques']))) > 0]) if (len(grade['processingTechniques'])) > 0 else None
                                        grade['industrySegments'] = list([list_val[0]['title'] for id in grade['industrySegments'] if len(list_val := list(filter(lambda x: x['id'] == id, json_object['industrySegments']))) > 0]) if (len(grade['industrySegments'])) > 0 else None
                                        grade['regions'] = list([list_val[0]['title'] if id != 'a3c56a19-9937-49e3-a578-81b38ed00b45' else 'Global' for id in grade['regions'] if len( list_val := list(filter(lambda x: x['id'] == id, json_object['regions']))) > 0]) if (len(grade['regions'])) > 0 else None
                                        new_grades.append(grade)
                                json_object['grades'] = new_grades
                                ins = write_file(json_data = json.dumps(json_object, indent=4), name = file.rsplit('.', 1)[0], path = update_path)
                                ins.write_json
                        else:
                                continue




        #Get the valid product categories from the list of all that are mentioned in the product drop down on the main webpage
        def get_valid_products(self, collection):
                """
                returns list of product categories
                """
                return list(filter( lambda ele : \
                not(re.match("(.*[b|B]ack.*)|(.*[p|P]roducts.*)|(.*[t|T]erms.*)|(.*[s|S]ervices.*)", ele.text) or re.match(".*[s|S]ervices.*", ele.get('href'))) ,collection))



        #Master function to initiate the scraping
        def scrape_products(self, url) -> json:
                '''
                Calls other classes internally to crawl through different levels of the product i.e Product_Category, Product_Family, Product, Grades
                :param url: url of the product category page to scrape down the further information from it
                '''
                #this calls the function on the top that will initiate the request to get the html content of the main page
                self.html_content(url) 
                #extracting data from <li> tags
                litag = self.soup.find('li', {config['CATEGORY']['KEY_ID']: config['CATEGORY']['VALUE_ID']}) 

                if litag is None:
                        logger.warn("No Products returned while searching for id = section_products in beautiful soup object")
                #passing regex to skip all unnecessary product categories
                for ele in self.get_valid_products(litag.find_all('a')): 
                        start = time.time()
                        product_dict = {}
                        
                        try:
                                logger.info(f"{ele.text} is getting started to get scraped \n")
                                #calling scrape_item() from the ExtractProduct class
                                product_dict[ele.text] = extract(url = str('https://www.sabic.com' + ele.get('href'))).scrape_product_family(ele.text) 
                                
                        except FileNotFoundError as FileNotFound:
                                logger.error(help.PrintException())
                                raise FileNotFoundError('No folder created for category {}'.format(ele.text))
                        except Exception as ex:
                                logger.error(help.PrintException())
                                raise Exception("Data cannot be scraped for " + ele.text + ' due to error encountered : {}'.format(ex))
                        else:
                                #converts the dictionary data to JSON object to create the JSON file for each product category
                                json_object = json.dumps(product_dict, indent = 4)
                                #Class that will write the JSON file
                                write_file(json_data = json_object, name = ele.text, path = self.dest_path).write_json 
                                #To update the document & grade information from the product level JSON
                                self.Update_Datasheets(ele.text) 
                                logger.info(f'Total time taken to Scrape {ele.text} is {(time.time()-start)/60}')
                                # return product_dict
                        

if __name__ == '__main__':

        try:
                start = main_scraper()
                start.scrape_products("https://www.sabic.com/en")

        except Exception as error:
                logger.error(error)
