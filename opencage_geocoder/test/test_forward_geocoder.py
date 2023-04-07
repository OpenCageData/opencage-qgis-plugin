import os
import os.path as path
import unittest
import csv

from qgis.core import (
     QgsRectangle
)
    
from opencage_geocoder.processing.geocoder import OpenCageGeocode
from opencage_geocoder.processing.QgsOpenCageGeocoder import QgsOpenCageGeocoder

DATA_FOLDER = path.join(path.dirname(__file__), "data")

# Note: Export yout api key from the command line, before running this test
API_KEY = os.environ["OPENCAGE_KEY"]

str= "Rua da Misericordia, 230"
simple_result = "Rua da Misericordia, 7430-142 Crato, Portugal"
result_options = "Rua Da Misericordia, Quilombo do Alto do Tororó, Salvador - BA, 40800-570, Brésil"

class TestForwardGeoCoding(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestForwardGeoCoding, self).__init__(*args, **kwargs)
        self.openCageGeocoder = QgsOpenCageGeocoder(API_KEY, True)

    def test_forward_geocoding_simple(self):

        json = self.openCageGeocoder.geocoder.geocode(str)
        formatted = json[0]['formatted']
        # print(formatted)

        self.assertEqual(formatted, simple_result, "Failed to geocode address.")

    def test_forward_geocoding_options(self):

        json = self.openCageGeocoder.geocoder.geocode(str, abbrv=0, no_annotations=1, 
                                     no_record=0, language="fr",
                                     countrycode="BR"
                                     )
        
        formatted = json[0]['formatted']
        # print(formatted)

        self.assertEqual(formatted, result_options, "Failed to geocode address with options.")

    def test_geocode_file(self):
 
        filename = open(path.join(DATA_FOLDER, 'sample_small.csv'), 'r')
        
        # creating dictreader object
        file = csv.DictReader(filename)
        
        # creating empty lists
        results = []
        
        # iterating over each row and append
        # values to empty list
        for col in file:
            json = self.openCageGeocoder.geocoder.geocode(col['Morada_'],countrycode="PT,BR")
            if json:
                results.append(json[0]['formatted'])
                # print(results[len(results)-1])

        self.assertEqual(3, len(results), "Failed to geocode address file.")
