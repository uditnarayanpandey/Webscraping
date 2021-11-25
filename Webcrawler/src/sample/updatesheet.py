import json
import sys

import requests
from retrying import retry
from src.sample.helpers import *

logger = help.get_module_logger(__name__)

class UpdateDatasheets:
    '''
    description: updating datasheets to the grade json
    parameters : path
    '''

    def __init__(self, *args, **kwargs):
        self.grade_details_url_format = "https://www.sabic.com/en/productsearch/getdocumentsearchpagination?grades={}"

    #Loads the grade metadata from the http url


    @retry(stop_max_attempt_number=4, wait_fixed=2000)
    def get_grade_metadata(self, grade_id):
        """
        Returns grades metadata from api call

        :param grade_id: ID of grade
        :type grade_id: string
        :param try_number: number of times the code retries api call during exception
        :type try_number: int
        """
        url = self.grade_details_url_format.format(grade_id)
        try:
            r= requests.get(url)
            r.close()
        except (requests.exceptions.ConnectionError, json.decoder.JSONDecodeError, json.decoder.JSONDecodeError) as error:
            logger.error(help.PrintException())
            raise Exception(f'Something went wrong ("Connection Error/ JSONDecodeError") while updating the {grade_id}.json in updatesheet, retrying....\n')    
        else:
            if (len(r.content)) != 0:
                self.res = r.json()
            else:
                logger.warning("No data available for grade : "+ grade_id)
                self.res = {}
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
            #Gets grade details json from http request
            grade_json_response = self.get_grade_metadata(grade_id) 
            grade_raw = {key:grade_json_response['grades'][0][key] for key in grade_json_response['grades'][0].keys() & {'documents'}}
            #Loading raw documents list which has region id and language code
            document_details_raw = grade_json_response['documents'] 

            # Load data from facet block to map with the id
            documentTypes = self.get_facet_data(key='documentTypes', grade_json = grade_json_response)
            regionTypes = self.get_facet_data(key='regions', grade_json = grade_json_response)
            languageTypes = self.get_facet_data(key='languages', grade_json = grade_json_response)

            #Loading document ids for the grade
            grade_document_ids = grade_raw['documents']
            #Removing document id list from raw grade details
            del grade_raw['documents'] 
            #Empty grade_documents list
            grade_documents = [] 

            # Updating and mapping id for document details for the grade ids
            for doc_id in grade_document_ids:
                # Filters and returns the document for the given id from the raw documents list
                document_detail = list(filter(lambda d: d['id'] == doc_id, document_details_raw))
                # To handle cases where data is wrong. Like : [Specialities] [ LNP™ COMPOUNDS ] [LNP™ KONDUIT™ Compound] [grade id: 5e41aad7-e0d8-e611-819b-06b69393ae39]
                if len(document_detail)==0:
                    continue
                else:
                    document_detail = dict([(key, val) for key, val in document_detail[0].items() if key not in ('$id','mimeType', 'publishedAt', 'sequence', 'registrationRequired', 'visibility', 'productTitle', 'gradeTitle', 'familyTitle', 'categoryTitle', 'country')])
                # Get data from the facet list for documentType mapping
                document_detail["documentType"] = self.get_value_from_collection(id=document_detail["documentType"], collection=documentTypes)
                # Get data from the facet list for regionType mapping
                document_detail['region'] = self.get_value_from_collection(id=document_detail["region"], collection=regionTypes)
                # Get data from the facet list for languageType mapping
                document_detail['language'] = self.get_value_from_collection(id=document_detail["language"], collection=languageTypes)
                #appending document details
                grade_documents.append(document_detail)
        except KeyError as key:
            logger.error("Key not present/ empty json document")
            #returning Null when the documents are not present
            return
        else:
            #returning list of documents for each grade
            return grade_documents

if __name__ == '__main__':
    
    try:
        obj = UpdateDatasheets()
        obj.get_grade_details(grade_id='f9be5d67-63e0-440a-abd5-4477bb351edb')
    except Exception as error:
        print('This is the error: {}'.format(error))
