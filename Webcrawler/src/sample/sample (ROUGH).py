import json, time, random, requests, simplejson
from custom_logger import get_module_logger

logger = get_module_logger(__name__)

class UpdateDatasheets:
    '''
    description: updating datasheets to the grade json
    parameters : path
    '''

    def __init__(self, *args, **kwargs):
        self.grade_details_url_format = "https://www.sabic.com/en/productsearch/getdocumentsearchpagination?grades={}"

    #Loads the grade metadata from the http url
    def get_grade_metadata(self, grade_id, try_number = 1):
        """
        Returns grades metadata from api call

        :param grade_id: ID of grade
        :type grade_id: string
        :param try_number: number of times the code retries api call during exception
        :type try_number: int
        """
        url = self.grade_details_url_format.format(grade_id)
        if (try_number > 10):
            logger.info('Achieved maximum number of retries....')
        else:
            try:
                r= requests.get(url)
                r.close()

                if (len(r.content)) != 0:
                    self.res = r.json()
                else:
                    logger.warn("No data available for grade : "+grade_id)
                    self.res = {}
            except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError, simplejson.errors.JSONDecodeError):
                logger.info(f'retrying it for {try_number} times')
                logger.error("Connection Error/ JSONDecodeError")
                time.sleep(2**try_number) #exponential backoff
                return self.get_grade_metadata(grade_id, try_number =+ 1)
            else:
                return self.res

    #Loads the facet data from the grade_json for filter key and return the list of values for the filter
    def get_facet_data(self, key, grade_json):
        """
        Maps region, language and document type keys to its value
        """
        return list(filter(lambda facet: facet['Key'] == key, grade_json['facets']))[0]['Value']

    #Returns the correct value from the list for the given id.
    #collection should be a list returned from get_facet_data()
    def get_value_from_collection(self, id, collection):
        return list(filter(lambda dictionary: dictionary['id'] == id, collection))[0]['title']

    def get_grade_details(self, grade_id):
        """
        Returns grade data as dictionary
        """
        # Load the data
        try:
            grade_json_response = self.get_grade_metadata(grade_id) #Gets grade details json from http request
            grade_raw = {key:grade_json_response['grades'][0][key] for key in grade_json_response['grades'][0].keys() & {'documents'}}
            # grade_raw = grade_json_response['grades'][0] # loads raw grade details with ids from documents
            document_details_raw = grade_json_response['documents'] # Loading raw documents list which has region id and language code 

            # Load data from facet block to map with the id
            documentTypes = self.get_facet_data(key='documentTypes', grade_json=grade_json_response)
            regionTypes = self.get_facet_data(key='regions', grade_json=grade_json_response)
            languageTypes = self.get_facet_data(key='languages', grade_json=grade_json_response)

            #Loading document ids for the grade
            grade_document_ids = grade_raw['documents']
            del grade_raw['documents'] # Removing document id list from raw grade details
            grade_detail = grade_raw #Grade details without documents detail
            grade_documents = [] #Empty grade_documents list

            # Updating and mapping id for document details for the grade ids
            for doc_id in grade_document_ids:
                # Filters and returns the document for the given id from the raw documents list
                document_detail = list(filter(lambda d: d['id'] == doc_id, document_details_raw))
                # To handle cases where data is wrong. Like : [Specialities] [ LNP™ COMPOUNDS ] [LNP™ KONDUIT™ Compound] [grade id: 5e41aad7-e0d8-e611-819b-06b69393ae39]
                if len(document_detail)==0:
                    continue
                else:
                    document_detail = dict([(key, val) for key, val in document_detail[0].items() if key not in ('$id','mimeType', 'publishedAt', 'sequence', 'registrationRequired', 'visibility', 'productTitle', 'gradeTitle', 'familyTitle', 'categoryTitle')])
                    # document_detail = document_detail[0]
                # Get data from the facet list for documentType mapping
                document_detail["documentType"] = self.get_value_from_collection(id=document_detail["documentType"], collection=documentTypes)
                # Get data from the facet list for regionType mapping
                document_detail['region'] = self.get_value_from_collection(id=document_detail["region"], collection=regionTypes)
                # Get data from the facet list for languageType mapping
                document_detail['language'] = self.get_value_from_collection(id=document_detail["language"], collection=languageTypes)
                grade_documents.append(document_detail)
            
            # Adding document details for the grade
            # return grade_documents
        except KeyError as ke:
            logger.error("Key not present/ empty json document")
            # grade_detail['documents'] = None
            # return grade_detail
            return 
        else:
            return grade_documents
            
        
if __name__ == '__main__':
    # print(UpdateDatasheets().get_grade_details(grade_id='a1d50144-d23f-e911-8100-005056857ef3'))
    print(UpdateDatasheets().get_grade_details(grade_id='591b6627-7bc7-e611-8197-06b69393ae39'))





































    def get_grade_metadata(self, grade_id, try_number = 1):
        """
        Returns grades metadata from api call

        :param grade_id: ID of grade
        :type grade_id: string
        :param try_number: number of times the code retries api call during exception
        :type try_number: int
        """
        url = self.grade_details_url_format.format(grade_id)
        if (try_number > 10):
            logger.info('Achieved maximum number of retries....')
        else:
            try:
                r= requests.get(url)
                r.close()

                if (len(r.content)) != 0:
                    self.res = r.json()
                else:
                    logger.warn("No data available for grade : "+grade_id)
                    self.res = {}
            except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError, simplejson.errors.JSONDecodeError):
                logger.info(f'retrying it for {try_number} times')
                logger.error("Connection Error/ JSONDecodeError")
                time.sleep(2**try_number) #exponential backoff
                return self.get_grade_metadata(grade_id, try_number = try_number + 1)
            else:
                return self.res
    











    # ====================================================================== JSON writer ===========================================================================
    import json
import os,pathlib
from src.sample.helpers import *

logger = help.get_module_logger(__name__)

class write_file:
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
        """
        Description : Function used to write JSON in an appropriate directory
        Input : -
        Output : JSON file
        """
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


