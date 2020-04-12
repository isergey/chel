import os
import tempfile
from django.conf import settings

TMP_DIR = getattr(settings, 'HARVESTER_TMP_DIR', {}) or tempfile.gettempdir()



SOLR = settings.SEARCH.get('solr')
SOLR_BASE_URL = SOLR.get('host', 'http://localhost:8983')
SOLR_COLLECTION = SOLR.get('collection', 'collection1')

if not os.path.isdir(TMP_DIR):
    os.makedirs(TMP_DIR, exist_ok=True)

PDFBOX_PATH = os.path.join(settings.BASE_DIR, 'bin', 'pdfbox', 'pdfbox-app-2.0.9.jar')