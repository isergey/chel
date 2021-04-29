import datetime
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect

from junimarc.json.opac import record_from_json
from opac_global_client.client import Client
from opac_global_client.entities import ReaderResponse, CirculationOperation, CirculationOrder
from .settings import opac_client, AUTH_SOURCE
from sso import models
from .subscription import create_subscription_letter


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
def orders(request):
    external_user = models.get_external_users(request.user, AUTH_SOURCE).first()
    if not external_user:
        return HttpResponse('Вы не являетесь читателем')

    reader_response = ReaderResponse(**external_user.get_attributes())
    orders = _get_orders(
        opac_client=opac_client,
        reader_response=reader_response
    )
    orders.reverse()
    return render(request, 'sso_opac/orders.html', {
        'orders': orders,
    })


@login_required
def on_hand(request):
    external_user = models.get_external_users(request.user, AUTH_SOURCE).first()
    if not external_user:
        return HttpResponse('Вы не являетесь читателем')

    reader_response = ReaderResponse(**external_user.get_attributes())

    checkouts = _get_checkouts(
        opac_client=opac_client,
        reader_response=reader_response
    )
    checkouts.reverse()
    return render(request, 'sso_opac/on_hand.html', {
        'checkouts': checkouts,
    })


@login_required
def renewal(request):
    external_user = models.get_external_users(request.user, AUTH_SOURCE).first()
    if not external_user:
        return HttpResponse('Вы не являетесь читателем')

    reader_response = ReaderResponse(**external_user.get_attributes())
    place = request.POST.get('place')
    item_code = request.POST.get('item_code')
    response = opac_client.circulation().renewal(place=place, item_codes=[item_code])
    print(response)
    # ye
    return redirect('sso_opac:on_hand')


def incomes(request):
    resoponse = opac_client.databases().get_records(db_id='18')
    for item in resoponse.get('data', []):
        record = record_from_json(item.get('attributes', {}))
        print(record)
        # print(''.join(item.get('attributes', {}).get('SHOTFORM', {}).get('content', [])))
        # print('--------------------')
    return HttpResponse('')


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
    now = datetime.datetime.now()
    past = now - datetime.timedelta(days=30)
    databases = opac_client.databases()
    orders: List[CirculationOrderInfo] = []
    response = opac_client.circulation().get_reader_orders(reader_response.id)
    for order_info in response.data:
        order = order_info.attributes
        if order.operation_time < past:
            continue
        record = databases.get_record(db_id=order.db_id, record_id=order.record_id)
        libcard = '\n'.join(record.get('data', {}).get('attributes', {}).get('SHOTFORM', {}).get('content', []))
        orders.append(CirculationOrderInfo(
            order=order,
            libcard=libcard
        ))

    return orders



def subscription(request):
    create_subscription_letter([])
    return HttpResponse('ok')