# -*- coding: utf-8 -*-

"""
/***************************************************************************
 OpenCageProcessing
                                 A QGIS plugin
 Geocoding using the OpenCage API
                              -------------------
        begin                : 2023-01-11
        copyright            : (C) 2023 by ByteRoad
        email                : info@byteroad.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'doublebyte'
__date__ = '2023-03-03'
__copyright__ = '(C) 2023 by opencage'

__revision__ = '$Format:%H$'

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
    """
    This class tests the forward geocoding algorithm.
    It contains different test cases, which use hardcoded strings and a file
    as input.

    Before running these tests, you should export your opencage key as
    an environmental variable.
    """
    def __init__(self, *args, **kwargs):
        super(TestForwardGeoCoding, self).__init__(*args, **kwargs)
        self.openCageGeocoder = QgsOpenCageGeocoder(API_KEY, True, True)

    def test_forward_geocoding_simple(self):
        """
        Simple forward geocoding test: sends an address string and
        should return a geocoded string.
        """
        json = self.openCageGeocoder.geocoder.geocode(str)
        formatted = json[0]['formatted']
        # print(formatted)

        self.assertEqual(formatted, simple_result, "Failed to geocode address.")

    def test_forward_geocoding_options(self):
        """
        Forward geocoding test with options: sends an address string
        with options and should return a geocoded string.
        """
        json = self.openCageGeocoder.geocoder.geocode(str, abbrv=0, no_annotations=1, 
                                     no_record=0, language="fr",
                                     countrycode="BR"
                                     )
        
        formatted = json[0]['formatted']
        # print(formatted)

        self.assertEqual(formatted, result_options, "Failed to geocode address with options.")

    def test_geocode_file(self):
        """
        Forward geocoding test from a file: reads addresses
        from a text(csv) file and should return a specific number of
        geocoded addresses.
        """
        filename = open(path.join(DATA_FOLDER, 'sample_small.csv'), 'r')
        
        # creating dictreader object
        file = csv.DictReader(filename)
        
        # creating empty list
        results = []
        
        # iterating over each row and append
        # values to empty list
        for col in file:
            json = self.openCageGeocoder.geocoder.geocode(col['Morada_'],countrycode="PT,BR")
            if json:
                results.append(json[0]['formatted'])
                # print(results[len(results)-1])

        self.assertEqual(3, len(results), "Failed to geocode address file.")
