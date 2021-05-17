from django.conf import settings
from opac_global_client.client import Client, Config
from opac_global_client.cache import DjangoTokenCache

OPAC_GLOBAL = getattr(settings, 'OPAC_GLOBAL', {})
USERNAME = OPAC_GLOBAL.get('username')
PASSWORD = OPAC_GLOBAL.get('password')
BASE_URL = OPAC_GLOBAL.get('base_url')
CLIENT_ID = OPAC_GLOBAL.get('client_id')
CLIENT_SECRET = OPAC_GLOBAL.get('client_secret')
SCOPE = OPAC_GLOBAL.get('scope', ['read', 'write'])

AUTH_SOURCE = 'opac'


token_cache = DjangoTokenCache()

opac_client = Client(config=Config(
            username=USERNAME,
            password=PASSWORD,
            base_url=BASE_URL,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE
        ), token_cache=token_cache)
