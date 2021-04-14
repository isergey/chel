from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from opac_global_client.client import Client
from opac_global_client.entities import ReaderResponse, CirculationOperation, CirculationOrder
from .settings import opac_client, AUTH_SOURCE
from sso import models


@dataclass
class CirculationOrderInfo:
    order: CirculationOrder
    libcard: str = ''

    def __str__(self):
        return self.libcard


@dataclass
class CirculationOperationInfo:
    operation: CirculationOperation
    libcard: str = ''


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

    with ThreadPoolExecutor(max_workers=1) as executor:
        orders_future = executor.submit(_get_orders, opac_client, reader_response)
        checkouts_future = executor.submit(_get_checkouts, opac_client, reader_response)
        orders = orders_future.result()
        checkouts = checkouts_future.result()
    return render(request, 'sso_opac/on_hand.html', {
        'checkouts': checkouts,
        'orders': orders
    })


def _get_checkouts(opac_client: Client, reader_response: ReaderResponse) -> List[CirculationOperationInfo]:
    databases = opac_client.databases()
    checkouts: List[CirculationOperationInfo] = []
    response = opac_client.circulation().get_reader_checkouts(reader_response.id)
    for checkout in response.data:
        operation = checkout.attributes
        record = databases.get_record(db_id=operation.db_id, record_id=operation.record_id)
        libcard = '\n'.join(record.get('data', {}).get('attributes', {}).get('SHOTFORM', {}).get('content', []))
        checkouts.append(CirculationOperationInfo(
            operation=operation,
            libcard=libcard
        ))

    return checkouts


def _get_orders(opac_client: Client, reader_response: ReaderResponse) -> List[CirculationOrderInfo]:
    databases = opac_client.databases()
    orders: List[CirculationOrderInfo] = []
    response = opac_client.circulation().get_reader_orders(reader_response.id)
    for order_info in response.data:
        order = order_info.attributes
        record = databases.get_record(db_id=order.db_id, record_id=order.record_id)
        libcard = '\n'.join(record.get('data', {}).get('attributes', {}).get('SHOTFORM', {}).get('content', []))
        orders.append(CirculationOrderInfo(
            order=order,
            libcard=libcard
        ))

    return orders
