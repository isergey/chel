from django.conf import settings
FILE_NAME_ENCODING = getattr(settings, 'FILE_NAME_ENCODING', 'utf-8')

UPLOAD_TO = getattr(settings, 'FILEBROWSER').get('upload_dir').strip('/').strip('\\')
MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL