import os
from django.conf import settings

MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT')


def _create_report_file(name):
    statistics_dir_path = os.path.join(MEDIA_ROOT, 'ssearch', 'statistics')
    if not os.path.exists(statistics_dir_path):
        os.makedirs(statistics_dir_path)
    return os.path.join(statistics_dir_path, name)


def get_income_report_file_path():
    return _create_report_file('income_report.json')


def get_actions_report_file_path():
    return _create_report_file('actions_report.json')


def get_users_report_file_path():
    return _create_report_file('user_report.json')


def get_material_types_report_file_path():
    return _create_report_file('material_types_report.json')