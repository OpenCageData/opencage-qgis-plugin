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
     QgsRectangle,
    QgsVectorLayer,
    QgsProject,
    QgsApplication
)
    
from opencage_geocoder.processing.geocoder import OpenCageGeocode
from opencage_geocoder.processing.QgsOpenCageGeocoder import QgsOpenCageGeocoder

DATA_FOLDER = path.join(path.dirname(__file__), "data")

# Note: Export yout api key from the command line, before running this test
API_KEY = os.environ["OPENCAGE_KEY"]

lat=32.797545
lng=-17.04206
simple_result = "Grutas e Centro do Vulcanismo, Estrada Dom João V, 9240-221 São Vicente, Madeira, Portugal"
address_only = "Estrada Dom João V, 9240-221 São Vicente, Madeira, Portugal"

class TestReverseGeoCoding(unittest.TestCase):
    """
    This class tests the reverse geocoding algorithm.
    It contains different test cases, which use hardcoded coordinates and a file
    as input.

    Before running these tests, you should export your opencage key as
    an environmental variable.
    """
    def __init__(self, *args, **kwargs):
        super(TestReverseGeoCoding, self).__init__(*args, **kwargs)
        self.openCageGeocoder = QgsOpenCageGeocoder(API_KEY, False, True)

    def test_reverse_geocoding_simple(self):
        """
        Simple reverse geocoding test: sends a pair of
        coordinates and should return a geocoded string.
        """
        json = self.openCageGeocoder.geocoder.reverse_geocode(lat,lng)
        formatted = json[0]['formatted']
        # print(formatted)

        self.assertEqual(formatted, simple_result, "Failed to geocode address.")

    def test_reverse_address_only(self):
        """
        Forward geocoding test with address only: sends an address string
        and should return the geocoded address only (e.g.: without poi).
        """
        json = self.openCageGeocoder.geocoder.reverse_geocode(lat,lng,address_only=1)
        
        formatted = json[0]['formatted']
        # print(formatted)

        self.assertEqual(formatted, address_only, "Failed to geocode address with options.")

    def test_geocode_file(self):
        """
        Reverse geocoding test from a file: reads point geometries
        from a vector file and should return a specific number of
        geocoded addresses.
        """
        path_to_gpkg = path.join(DATA_FOLDER, 'portuguese-poi_small.gpkg')
        # print(path_to_gpkg)
        layer = QgsVectorLayer(path_to_gpkg,"test","ogr")
        gpkg_layer = path_to_gpkg + "|layername=portuguesepoi__portuguese_points_of_interest_via_ogr_gpkg"
        vlayer = QgsVectorLayer(gpkg_layer, "poi layer", "ogr")

        if not vlayer.isValid():
            print("Layer failed to load!")
        else:

            features = vlayer.getFeatures()

            # creating empty list
            results = []

            for feature in features:
                # fetch geometry
                geom = feature.geometry()
                json = self.openCageGeocoder.geocoder.reverse_geocode(geom.asPoint().y(),
                                                                        geom.asPoint().x())        
                if json:
                    results.append(json[0]['formatted'])
                    # print(results[len(results)-1])

            self.assertEqual(59, len(results), "Failed to geometry file.")
