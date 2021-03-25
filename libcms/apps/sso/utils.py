# coding=utf-8
from django.shortcuts import reverse


def normalize_fio(fio: str):
    """
    "иванов - петров Иван Иваныч" -> "Иванов-Петров Иван Иваныч"
    :param fio: ФИО
    :return: нормализованное имя
    """
    cleaned_fio = fio.strip().lower()
    fio_parts = []
    for fio_part in cleaned_fio.split(' '):
        if fio_part == ' ' or not fio_part:
            continue
        fio_parts.append(fio_part.title())

    cleaned_fio = ' '.join(fio_parts)
    fio_parts = []

    for fio_part in cleaned_fio.split('-'):
        if fio_part == ' ' or not fio_part:
            continue
        fio_parts.append(fio_part.strip().title())

    cleaned_fio = '-'.join(fio_parts)
    return cleaned_fio


def set_logout_url(request, url):
    request.session['logout_url'] = url


def get_logout_url(request):
    return request.session.get('logout_url') or reverse('logout')
