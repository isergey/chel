import os
import sys
from django.conf import settings

COMMANDS = getattr(settings, 'SUBSCRIBE_COMMANDS', [])
MANAGE_PY_PATH = os.path.join(settings.BASE_DIR, 'manage.py')
PYTHON_PATH = sys.executable

if not os.path.isfile(MANAGE_PY_PATH):
    raise ValueError('File %s does not exists' % (MANAGE_PY_PATH,))

