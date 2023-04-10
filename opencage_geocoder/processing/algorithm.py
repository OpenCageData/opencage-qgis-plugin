# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

from qgis.analysis import QgsBatchGeocodeAlgorithm
from .QgsOpenCageGeocoder import QgsOpenCageGeocoder

import logging
logging.basicConfig(filename='/tmp/opencage1.log', encoding='utf-8', level=logging.DEBUG)

class OpenCageBatchGeocode(QgsBatchGeocodeAlgorithm):

    def __init__(self, api_key, region):
        self.api_key = api_key
        self.region = region
        self.coder = QgsOpenCageGeocoder(api_key, self.region)
        QgsBatchGeocodeAlgorithm.__init__(self, self.coder)

    def groupId(self):
        return None

    def group(self):
        return None

    def name(self):
        return 'opencage_geocode'

    def displayName(self):
        return 'OpenCage batch geocoder'

    def createInstance(self):
        return QgsOpenCageGeocoder(self.api_key, self.region)
