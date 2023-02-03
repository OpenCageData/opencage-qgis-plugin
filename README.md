# OpenCage Geocoder QGIS Plugin

This processing plugin enables geocoding using the [OpenCage Geocoding API](https://opencagedata.com). In order to use it, you need to [sign up](https://opencagedata.com/users/sign_up) for an API key first. Sign up is quick and free.

## Manual Install

* Copy the entire directory containing the plugin to the QGIS plugin directory
* Enable the plugin the QGIS plugin manager
  
## Develop

  * You can use the ` Makefile` to compile and deploy when you make changes. This requires GNU make (gmake). The Makefile is ready to use, however you  will have to edit it to add addional Python source files, dialogs, and translations.
  * You can also use `pb_tool` to compile and deploy your plugin. Tweak the `pb_tool.cfg`  file included with your plugin as you add files. Install `pb_tool` using 
  `pip` or `easy_install`. See http://loc8.cc/pb_tool for more information.
  * Test the code using `make test` (or run tests from your IDE)

  For information on writing PyQGIS code, see http://loc8.cc/pyqgis_resources for a list of resources.

## Who is OpenCage GmbH?

<a href="https://opencagedata.com"><img src="./opencage_logo_300_150.png"></a>

We run the [OpenCage Geocoding API](https://opencagedata.com). Learn more [about us](https://opencagedata.com/about). 

We also run [Geomob](https://thegeomob.com), a series of regular meetups for location based service creators, where we do our best to highlight geoinnovation. If you like geo stuff, you will probably enjoy [the Geomob podcast](https://thegeomob.com/podcast/).