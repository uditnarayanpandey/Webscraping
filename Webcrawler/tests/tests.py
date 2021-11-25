import json
import unittest
from unittest.main import main
from bs4 import BeautifulSoup
import requests
from requests.sessions import session
from src.sample.webscraper import main_scraper
from src.sample.updatesheet import UpdateDatasheets
from src.sample.extract_grades import ExtractGradesInfo
from src.sample.prod_grades_httpclient import product_client
from src.sample.extract_product import ExtractProductItem
from src.sample.extract_product_family import ExtractProductFamily

class WebscraperTest(unittest.TestCase):
    session = requests.Session()
    def test_html_content_code(self):
        """
        Tests if web requests is returning proper status code
        """
        a = main_scraper().html_content(url="https://www.facebook.com")
        self.assertEqual(a[0].status_code, 200)

        b = main_scraper().html_content(url="https://www.pipsnacks.com/404")
        self.assertEqual(b[0].status_code, 404,"html request codes successfully tested")


    def test_html_content_body(self):
        """
        Tests if content is being returned according to status code
        """
        # session = requests.Session()
        a = main_scraper().html_content(url="https://www.facebook.com")
        self.assertNotEqual(len(a[0].content), 0,"html content successfully tested")

        b = main_scraper().html_content(url="https://www.pipsnacks.com/404")
        self.assertNotEqual(len(b[0].content), 0,"html content successfully tested")


    def test_get_valid_products(self):
        """
        Tests if all the valid products list is being scraped
        """

        r = requests.get("https://www.sabic.com/en")
        htmlContent = r.content
        soup = BeautifulSoup(htmlContent, 'html.parser')

        litag = soup.find('li', {'id': 'section_products'})

        expected_list = ["Polymers", "Specialties", "Chemicals", "Metals", "Agri-Nutrients"]

        valid_product_html_list = main_scraper().get_valid_products(litag.find_all('a'))

        valid_product_list = []

        for i in valid_product_html_list:
            valid_product_list.append(i.text)

        self.assertTrue(set(expected_list).issubset(set(valid_product_list)),msg="Valid Product list is being returned by function get_valid_products()")

    def test_get_grade_metadata(self):
        """
        Tests if proper grade details is being scraped
        """


        # passing correct grade id
        original_outcome = UpdateDatasheets().get_grade_metadata(grade_id="1e40f52f-b7d9-e611-819b-06b69393ae39")

        self.assertTrue(len(original_outcome)!=0,msg="Original grade id returining valid data")

        # Passing random grade
        original_outcome = UpdateDatasheets().get_grade_metadata(grade_id="kshgukshgnvilesknblsikvnz")

        self.assertFalse(len(original_outcome)!=0,msg="Original grade id returining valid data")


    def test_get_grade_details(self):
        """
        Tests if all the expected details for grades are being scraped
        """
        # passing correct grade id
        original_outcome = UpdateDatasheets().get_grade_details(grade_id="1e40f52f-b7d9-e611-819b-06b69393ae39")
        keys_expected = ['documentType','title','url','language','region','revision','id']

        self.assertEqual(sorted(list(original_outcome[0].keys())), sorted(keys_expected), msg="get grade details returning proper schema")

        # Passing random grade
        original_outcome = UpdateDatasheets().get_grade_metadata(grade_id="kshgukshgnvilesknblsikvnz")

        self.assertTrue(len(original_outcome)==0)


    def test_generate_grades_data(self):
        """
        Tests if all the expected grades are being scraped
        """

        # for acrylonitrile styrene acrylate asa
        expected_grades = ['CR7020', 'CR7500', 'CR7520', 'CR8510', 'FXTW26SK', 'FXW751SK', 'HRA170', 'HRA170D', 'HRA170E', 'HRA222', 'HRA222F', 'XP4025', 'XP4034', 'XP4045LG', 'XP7550', 'XP7560', 'XTPMFR10', 'XTWE270M', 'XTWE480', 'XTWM206']

        a = ExtractGradesInfo(url = "https://www.sabic.com/en/products/polymers/acrylonitrile-styrene-acrylate-asa/geloy-resin").generate_grades_data(product_id = 'c177b703-e1d8-e611-819b-06b69393ae39', category_name = 'Polymers')

        original_outcome = []

        for i in a['grades']:
            # print(i['title'])
            original_outcome.append(i['title'])

        self.assertEqual(original_outcome, expected_grades, msg="Grades are matching")


    def test_get_product_info(self):
        """
        Tests if all the expected details are being scraped for product
        """

        # for acrylonitrile styrene acrylate asa
        expected_dict = {'product_id': '46ee92d2-79c7-e611-8197-06b69393ae39', 'related_products': None, 'total_grades': 1}

        a = ExtractGradesInfo(url = "https://www.sabic.com/en/products/agri-nutrients/agri-nutrients/11-29-19_6s-npk").get_product_info('Agri-Nutrients')

        self.assertEqual(a,expected_dict)

    def test_get_submission_record(self):
        """
        Tests if all the api contains all the expected keys
        """

        expected_keys = ['$id', 'grades', 'processingTechniques', 'applications', 'regions', 'industrySegments']

        a = product_client(url = "https://Sabic.com/en/productdata/c077b703-e1d8-e611-819b-06b69393ae39").get_submission_records()

        original_keys = list(a.keys())

        self.assertEqual(expected_keys, original_keys, msg = "submission records returning proper data")


    def test_scrape_product_items(self):
        """
        Tests if all the products is being scraped
        """

        expected_product_list = ['11-29-19_6S NPK', '18-18-5_9S NPK', 'Anhydrous Ammonia', 'DAP', 'Date Palm NPK', 'Enriched Urea', 'GRANULAR UREA', 'MAP','PRILLED UREA', 'TECHNICAL GRADE UREA']
        scraped_product_items = ExtractProductItem(url = "https://www.sabic.com/en/products/agri-nutrients/agri-nutrients").scrape_product_items('Agri-Nutrients')

        outcome_product_list = []
        for i in scraped_product_items:
            outcome_product_list.append(i['product_name'])

        self.assertEqual(sorted(expected_product_list), sorted(outcome_product_list))

    def test_scrape_product_family(self):
        """
        Tests if all the products is being scraped
        """

        a = ExtractProductFamily(url = "https://www.sabic.com/en/products/agri-nutrients").scrape_product_family('Agri-Nutrients')

        expected_product_list = ['11-29-19_6S NPK', '18-18-5_9S NPK', 'Anhydrous Ammonia', 'DAP', 'Date Palm NPK', 'Enriched Urea', 'GRANULAR UREA', 'MAP','PRILLED UREA', 'TECHNICAL GRADE UREA']


        outcome_product_list = []
        for i in a[0]['product']:
            outcome_product_list.append(i['product_name'])

        self.assertEqual(sorted(expected_product_list), sorted(outcome_product_list))


if __name__ == '__main__':
    # obj = WebscraperTest()
    # obj.test_html_content_body()
    unittest.main()
