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

import json as jsn

import logging
logging.basicConfig(filename='/tmp/opencage.log', encoding='utf-8', level=logging.DEBUG)

class QgsOpenCageGeocoder(QgsGeocoderInterface):

    def __init__(self, api_key, no_annotations):
        self.api_key = api_key
        self.endpoint = 'https://api.opencagedata.com/geocode/v1/json'
        self.geocoder = OpenCageGeocode(self.api_key)
        self.fieldList = self.setFields(no_annotations)
        QgsGeocoderInterface.__init__(self)

    def apiKey(self):
        return self.api_key

    def flags():
        return QgsGeocoderInterface.GeocodesStrings

    def forward(self, str, abbrveviation, n_annotations, 
                n_record, lang, extent, countries, context, feedback):

        formatted_bounds = '{},{},{},{}'.format(extent.xMinimum(),extent.yMinimum(),extent.xMaximum(),extent.yMaximum())
        # logging.debug("EXTENT: {}".format(formatted_bounds))

        json = self.geocoder.geocode(str, abbrv=abbrveviation, no_annotations=n_annotations, 
                                     no_record=n_record, language=lang,
                                     countrycode=countries, bounds=formatted_bounds)
        # logging.debug(json)

        if json and len(json):
            geom = QgsGeometry.fromPointXY( 
                QgsPointXY( json[0]['geometry']['lng'], json[0]['geometry']['lat'] ) )
            new_feature= QgsFeature()

            # Adds geometry
            new_feature.setGeometry(geom)

            new_feature.setFields(self.appendedFields())

            # Adds components
            for k,v in json[0]['components'].items():
                if k in self.fieldList:
                    new_feature.setAttribute(k, v)
                    # logging.debug(k,v)

            # Adds annotations
            if 'annotations' in json[0]:
                self.setAnnotations(json, new_feature)

            # Adds original address, formatted string and confidence
            new_feature.setAttribute('original_address',str)
            new_feature.setAttribute('formatted',json[0]['formatted'])
            new_feature.setAttribute('confidence',json[0]['confidence'])

            feedback.pushInfo("{} geocoded to: {}".format(str, json[0]['formatted']))
            return new_feature
        
        feedback.pushWarning("Could not geocode {}".format(str))
        return None

    def reverse(self, geom, lat, lng, abbrveviation, n_annotations, 
                n_record, address, lang, context, feedback):
    
        json = self.geocoder.reverse_geocode(lat, lng, abbrv=abbrveviation, no_annotations=n_annotations, 
                                     no_record=n_record, address_only=address, language=lang)

        # logging.debug(json)

        if json and len(json):

            logging.debug("COMES HERE!")

            new_feature= QgsFeature()
            new_feature.setGeometry(geom)

            new_feature.setFields(self.appendedFields())

            # Adds components
            for k,v in json[0]['components'].items():
                if k in self.fieldList:
                    new_feature.setAttribute(k, v)
                    logging.debug(k,v)

            # Adds annotations
            if 'annotations' in json[0]:
                self.setAnnotations(json, new_feature)

            # Adds original address, formatted string and confidence
            new_feature.setAttribute('formatted',json[0]['formatted'])
            new_feature.setAttribute('confidence',json[0]['confidence'])
            logging.debug('formatted',json[0]['formatted'])

            feedback.pushInfo("({:.2f},{:.2f}) geocoded to: {}".format(lat,lng,json[0]['formatted']))
            return new_feature
        
        feedback.pushWarning("Could not geocode: ({:.2f},{:.2f})".format(lat,lng))
        return None



    def setAnnotations(self, json, feature):
                feature.setAttribute('DMS.lat',json[0]['annotations']['DMS']['lat'])
                feature.setAttribute('DMS.lng',json[0]['annotations']['DMS']['lng'])
                feature.setAttribute('MGRS',json[0]['annotations']['MGRS'])
                feature.setAttribute('Maidenhead',json[0]['annotations']['Maidenhead'])
                feature.setAttribute('Mercator.x',json[0]['annotations']['Mercator']['x'])
                feature.setAttribute('Mercator.y',json[0]['annotations']['Mercator']['y'])
                if 'NUTS' in json[0]['annotations']:
                    feature.setAttribute('NUTS0',json[0]['annotations']['NUTS']['NUTS0']['code'])
                    feature.setAttribute('NUTS1',json[0]['annotations']['NUTS']['NUTS1']['code'])
                    feature.setAttribute('NUTS2',json[0]['annotations']['NUTS']['NUTS2']['code'])
                    feature.setAttribute('NUTS3',json[0]['annotations']['NUTS']['NUTS3']['code'])
                if 'OSM' in json[0]['annotations']: 
                    feature.setAttribute('OSM.note_url',json[0]['annotations']['OSM']['note_url'])
                    feature.setAttribute('OSM.url',json[0]['annotations']['OSM']['url'])
                if 'UN_M49' in json[0]['annotations']: 
                    feature.setAttribute('UN_M49.regions',jsn.dumps(json[0]['annotations']['UN_M49']['regions']))
                    feature.setAttribute('UN_M49.statistical_groupings',jsn.dumps(json[0]['annotations']['UN_M49']['statistical_groupings']))
                feature.setAttribute('callingcode',json[0]['annotations']['callingcode'])
                if 'currency' in json[0]['annotations']: 
                    if 'alternate_symbols' in json[0]['annotations']['currency']: 
                        feature.setAttribute('currency.alternate_symbols',jsn.dumps(json[0]['annotations']['currency']['alternate_symbols']))
                    feature.setAttribute('currency.decimal_mark',json[0]['annotations']['currency']['decimal_mark'])
                    feature.setAttribute('currency.iso_code',json[0]['annotations']['currency']['iso_code'])
                    feature.setAttribute('currency.iso_numeric',json[0]['annotations']['currency']['iso_numeric'])
                    feature.setAttribute('currency.name',json[0]['annotations']['currency']['name'])
                    feature.setAttribute('currency.smallest_denomination',json[0]['annotations']['currency']['smallest_denomination'])
                    feature.setAttribute('currency.subunit',json[0]['annotations']['currency']['subunit'])
                    feature.setAttribute('currency.subunit_to_unit',json[0]['annotations']['currency']['subunit_to_unit'])
                    feature.setAttribute('currency.symbol',json[0]['annotations']['currency']['symbol'])
                    feature.setAttribute('currency.symbol_first',json[0]['annotations']['currency']['symbol_first'])
                    feature.setAttribute('currency.thousands_separator',json[0]['annotations']['currency']['thousands_separator'])
                feature.setAttribute('flag',json[0]['annotations']['flag'])
                feature.setAttribute('geohash',json[0]['annotations']['geohash'])
                feature.setAttribute('qibla',json[0]['annotations']['qibla'])
                feature.setAttribute('roadinfo.drive_on',json[0]['annotations']['roadinfo']['drive_on'])
                feature.setAttribute('roadinfo.speed_in',json[0]['annotations']['roadinfo']['speed_in'])
                feature.setAttribute('sun.rise.apparent',json[0]['annotations']['sun']['rise']['apparent'])
                feature.setAttribute('sun.rise.astronomical',json[0]['annotations']['sun']['rise']['astronomical'])
                feature.setAttribute('sun.rise.civil',json[0]['annotations']['sun']['rise']['civil'])
                feature.setAttribute('sun.rise.nautical',json[0]['annotations']['sun']['rise']['nautical'])
                feature.setAttribute('sun.set.apparent',json[0]['annotations']['sun']['set']['apparent'])
                feature.setAttribute('sun.set.astronomical',json[0]['annotations']['sun']['set']['astronomical'])
                feature.setAttribute('sun.set.civil',json[0]['annotations']['sun']['set']['civil'])
                feature.setAttribute('sun.set.nautical',json[0]['annotations']['sun']['set']['nautical'])
                feature.setAttribute('timezone.name',json[0]['annotations']['timezone']['name'])
                feature.setAttribute('timezone.now_in_dst',json[0]['annotations']['timezone']['now_in_dst'])
                feature.setAttribute('timezone.offset_sec',json[0]['annotations']['timezone']['offset_sec'])
                feature.setAttribute('timezone.offset_string',json[0]['annotations']['timezone']['offset_string'])
                feature.setAttribute('timezone.short_name',json[0]['annotations']['timezone']['short_name'])
                feature.setAttribute('what3words',json[0]['annotations']['what3words']['words'])


    def setFields(self, forward, no_annotations):

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
        "original_address": "",
        "confidence": 0,
        }

        if (no_annotations == False):
            fieldList["DMS.lat"] = ""
            fieldList["DMS.lng"] = ""
            fieldList["MGRS"] = ""
            fieldList["Maidenhead"] = ""
            fieldList["Mercator.x"] = ""
            fieldList["Mercator.y"] = ""
            fieldList["NUTS0"] = ""
            fieldList["NUTS1"] = ""
            fieldList["NUTS2"] = ""
            fieldList["NUTS3"] = ""
            fieldList["OSM.note_url"] = ""
            fieldList["OSM.url"] = ""
            fieldList["UN_M49.regions"] = ""
            fieldList["UN_M49.statistical_groupings"] = ""
            fieldList["callingcode"] = ""
            fieldList["currency.alternate_symbols"] = ""
            fieldList["currency.decimal_mark"] = ""
            fieldList["currency.html_entity"] = ""
            fieldList["currency.iso_code"] = ""
            fieldList["currency.iso_numeric"] = ""
            fieldList["currency.name"] = ""
            fieldList["currency.smallest_denomination"] = ""
            fieldList["currency.subunit"] = ""
            fieldList["currency.subunit_to_unit"] = ""
            fieldList["currency.symbol"] = ""
            fieldList["currency.symbol_first"] = ""
            fieldList["currency.thousands_separator"] = ""
            fieldList["flag"] = ""
            fieldList["geohash"] = ""
            fieldList["qibla"] = ""
            fieldList["roadinfo.drive_on"] = ""
            fieldList["roadinfo.speed_in"] = ""
            fieldList["sun.rise.apparent"] = ""
            fieldList["sun.rise.astronomical"] = ""
            fieldList["sun.rise.civil"] = ""
            fieldList["sun.rise.nautical"] = ""
            fieldList["sun.set.apparent"] = ""
            fieldList["sun.set.astronomical"] = ""
            fieldList["sun.set.civil"] = ""
            fieldList["sun.set.nautical"] = ""
            fieldList["timezone.name"] = ""
            fieldList["timezone.now_in_dst"] = ""
            fieldList["timezone.offset_sec"] = ""
            fieldList["timezone.offset_string"] = ""
            fieldList["timezone.short_name"] = ""
            fieldList["what3words"] = ""

        return fieldList

    def appendedFields(self):

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
