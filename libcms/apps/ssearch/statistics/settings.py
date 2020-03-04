import os
from django.conf import settings

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')


def get_income_report_file_path():
    statistics_dir_path = os.path.join(MEDIA_ROOT, 'ssearch', 'statistics')
    if not os.path.exists(statistics_dir_path):
        os.makedirs(statistics_dir_path)
    return os.path.join(statistics_dir_path, 'income_report.json')
