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

from qgis.PyQt.QtCore import QCoreApplication, QVariant
from qgis.core import (QgsGeocoderInterface,
                       QgsFields,
                       QgsField,
                       QgsWkbTypes,
                       QgsPointXY,
                       QgsGeometry,
                       QgsCoordinateReferenceSystem,
                       QgsGeocoderResult,
                       QgsFeature
                       )

from .geocoder import OpenCageGeocode
from qgis.analysis import QgsBatchGeocodeAlgorithm

import logging
logging.basicConfig(filename='/tmp/opencage.log', encoding='utf-8', level=logging.DEBUG)

class QgsOpenCageGeocoder(QgsGeocoderInterface):

    def __init__(self, api_key, region, no_annotations):
        self.api_key = api_key
        self.region = region
        self.endpoint = 'https://api.opencagedata.com/geocode/v1/json'
        self.geocoder = OpenCageGeocode(self.api_key)
        self.fieldList = self.setFields(no_annotations)
        QgsGeocoderInterface.__init__(self)

    def apiKey(self):
        return self.api_key

    def flags():
        return QgsGeocoderInterface.GeocodesStrings

    def forward(self, str, abbrveviation, n_annotations, context, feedback):
        json = self.geocoder.geocode(str, abbrv=abbrveviation, no_annotations=n_annotations)
        # logging.debug(n_annotations)
        # logging.debug(json)

        if json and len(json):
            geom = QgsGeometry.fromPointXY( 
                QgsPointXY( json[0]['geometry']['lng'], json[0]['geometry']['lat'] ) )
            new_feature= QgsFeature()

            new_feature.setGeometry(geom)
            new_feature.setFields(self.appendedFields())

            # Adds components

            for k,v in json[0]['components'].items():
                if k in self.fieldList:
                    new_feature.setAttribute(k, v)
                    logging.debug(k,v)

            new_feature.setAttribute('formatted',json[0]['formatted'])

            if 'annotations' in json[0]:
                new_feature.setAttribute('DMS.lat',json[0]['annotations']['DMS']['lat'])
                new_feature.setAttribute('DMS.lng',json[0]['annotations']['DMS']['lng'])



            new_feature.setAttribute('formatted',json[0]['formatted'])

            feedback.pushInfo("{} geocoded to: {}".format(str, json[0]['formatted']))
            return new_feature
        
        feedback.pushWarning("Could not geocode {}".format(str))
        return None

    def setFields(self, no_annotations):

        logging.debug("SET FIELDS")

        fieldList = {
        "ISO_3166-1_alpha-2": "",
        "ISO_3166-1_alpha-3": "",
        "_category": "",
        "_type": "",
        "continent": "",
        "country": "",
        "country_code": "",
        "state": "",
        "state_code": "",
        "town": "",
        "formatted": "",
        }

        if (no_annotations == False):
            fieldList["DMS.lat"] = ""
            fieldList["DMS.lng"] = ""

        return fieldList

    def appendedFields(self):

        logging.debug("Field List")
        logging.debug(self.fieldList)

        fields=QgsFields();

        for key in self.fieldList:
            fields.append( QgsField(key, QVariant.String ))
        
        return fields

    def geocodeString(self, str, context, feedback):
        result = self.geocoder.geocode(str, no_annotations=1, countrycode=self.region)

        # TODO: add some checks here
        return self.jsonToResult(result)

    def jsonToResult(self, json):
        # Extract geometry
        geom = QgsGeometry.fromPointXY( QgsPointXY( json[0]['geometry']['lng'], json[0]['geometry']['lat'] ) )
        res = QgsGeocoderResult( json[0]['formatted'],
                                geom,
                                QgsCoordinateReferenceSystem( "EPSG:4326" ) )

        # Add attributes
        attributes= {}
        for f in self.appendedFields():
            attributes[f.name] = json[0]['components'][f.name]

        res.setAdditionalAttributes( attributes )

        return res

    def requestUrl(self):
        return self.endpoint
    
    def setApiKey(self, api_key):
        self.api_key = api_key

    def setEndpoint(self, url):
        self.endpoint = url

    def setRegion(self, region):
        self.region = region

    def wkbType():
        return QgsWkbTypes.Point
