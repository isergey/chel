from dataclasses import dataclass
from typing import List

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from opac_global_client.entities import ReaderResponse, CirculationOperation
from .settings import opac_client, AUTH_SOURCE
from sso import models


@dataclass
class CirculationOperationInfo:
    operation: CirculationOperation
    libcard: str


@login_required
def index(request):
    external_user = models.get_external_users(request.user, AUTH_SOURCE).first()
    if not external_user:
        return HttpResponse('Вы не являетесь читателем')
    return render(request, 'sso_opac/index.html')


@login_required
def on_hand(request):
    external_user = models.get_external_users(request.user, AUTH_SOURCE).first()
    if not external_user:
        return HttpResponse('Вы не являетесь читателем')

    reader_response = ReaderResponse(**external_user.get_attributes())

    checkouts_response = opac_client.circulation().get_reader_checkouts(reader_response.id)
    databases = opac_client.databases()
    checkouts: List[CirculationOperationInfo] = []
    for checkout in checkouts_response.data:
        operation = checkout.attributes
        record = databases.get_record(db_id=operation.db_id, record_id=operation.record_id)
        libcard = '\n'.join(record.get('data', {}).get('attributes', {}).get('SHOTFORM', {}).get('content', []))
        checkouts.append(CirculationOperationInfo(
            operation=operation,
            libcard=libcard
        ))

    return render(request, 'sso_opac/on_hand.html', {
        'checkouts': checkouts
    })
