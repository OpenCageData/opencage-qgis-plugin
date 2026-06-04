# import qgis libs so that ve set the correct sip api version
import atexit
import gc
import os
import tempfile

import qgis   # pylint: disable=W0611  # NOQA

from qgis.core import QgsApplication

# Initialise a headless QGIS application so the tests have a valid application
# path (silences "Application path not initialized"). The prefix is auto-detected.
if QgsApplication.instance() is None:
    # Write the QGIS profile (symbology-style.db, etc.) to a temp dir so test
    # runs don't litter the working tree.
    os.environ.setdefault("QGIS_CUSTOM_CONFIG_PATH",
                          tempfile.mkdtemp(prefix="qgis-test-"))
    _qgs_app = QgsApplication([], False)
    _qgs_app.initQgis()

    @atexit.register
    def _teardown_qgis():
        # Destroy the QgsApplication while the main thread is still alive,
        # otherwise Qt prints "QThreadStorage ... destroyed before end of
        # thread" during interpreter shutdown.
        global _qgs_app
        _qgs_app.exitQgis()
        _qgs_app = None
        gc.collect()
