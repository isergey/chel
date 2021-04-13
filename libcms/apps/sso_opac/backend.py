# encoding: utf-8
import hashlib
import logging

from django.contrib.auth.models import User
from django.db import transaction

from opac_global_client.entities import ReaderResponse
from sso.models import create_or_update_external_user, find_external_user
from .settings import opac_client, AUTH_SOURCE



logger = logging.getLogger('django.request')


class OpacGlobalAuthBackend:
    def __init__(self):
        self.__opac_client = opac_client

    def authenticate(self, request, username, password):
        if username:
            username = username.strip()

        if password:
            password = password.strip()

        if not username or not password:
            return None

        reader_response = None

        readers = self.__opac_client.readers()
        try:
            reader_response = readers.find_by_login(username)
        except Exception as e:
            logger.exception(str(e), exc_info=True)

        if reader_response is None:
            return None

        if hashlib.md5(password.encode('utf-8')).hexdigest() != reader_response.attributes.password:
            return None

        return self.get_or_create_user(username, password, reader_response)

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    @transaction.atomic()
    def get_or_create_user(self, username, password, reader: ReaderResponse):
        user = find_external_user(external_username=username, auth_source=AUTH_SOURCE)
        if user is not None:
            return user

        fio_parts = (reader.attributes.fio or '').split(' ')

        last_name = ''
        first_name = ''

        fio_parts_length = len(fio_parts)
        if fio_parts_length > 1:
            last_name = fio_parts[0].lower().title()
            first_name = fio_parts[1].title()
        elif fio_parts_length > 0:
            last_name = fio_parts[0].lower().title()

        external_user = create_or_update_external_user(
            external_username=username,
            auth_source=AUTH_SOURCE,
            attributes=reader.dict(),
            first_name=first_name,
            last_name=last_name,
            email=reader.attributes.email or '',
            is_active=True
        )

        return external_user.user
