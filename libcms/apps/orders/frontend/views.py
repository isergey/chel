# -*- coding: utf-8 -*-
import os
import datetime
import json as simplejson
from lxml import etree
import xml.etree.cElementTree as ET

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.shortcuts import HttpResponse, render, get_object_or_404, redirect, resolve_url, reverse
from django.contrib.auth.decorators import login_required

from ..ill import ILLRequest
from ..manager import OrderManager
from zgate.models import ZCatalog
from zgate import zworker


# from urt.models import LibReader
from ..models import UserOrderTimes

from participants.models import Library
#from order_manager.manager import OrderManager
from .forms import DeliveryOrderForm, CopyOrderForm
#from ssearch.models import  Record, Ebook

def set_cookies_to_response(cookies, response, domain=None):
    for key in cookies:
        response.set_cookie(key, cookies[key], domain=domain)
    return response


class MBAOrderException(Exception):
    pass


xslt_bib_draw = etree.parse(os.path.join(settings.BASE_DIR, 'libcms/xsl/full_document.xsl'))
xslt_bib_draw_transformer = etree.XSLT(xslt_bib_draw)


def set_cookies_to_response(cookies, response):
    for key in cookies:
        response.set_cookie(key, cookies[key])
    return response


def ajax_login_required(view_func):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        json = simplejson.dumps({'status': 'error', 'error': 'Необходимо войти в систему'}, ensure_ascii=False)
        return HttpResponse(json, content_type='application/json')

    wrap.__doc__ = view_func.__doc__
    wrap.__dict__ = view_func.__dict__
    return wrap


def json_error(error):
    return simplejson.dumps({'status': 'error',
                             'error': error},
                            ensure_ascii=False)

#
#@login_required
#def index(request):
#    links = LibReader.objects.select_related('library').filter(user=request.user)
#    return render(request, 'orders/frontend/index.html',{
#        'links':links,
#    })
#
#
#
#@login_required
#def lib_orders(request, id):
#    library = get_object_or_404(Library, id=id)
#    if not library.z_service:
#        return HttpResponse(u'Отсутвуют параметры связи с базой заказаов библиотеки. Если Вы видите это сообщение, пожалуйста, сообщите администратору портала.')
#
#    ruslan_order_urls = settings.RUSLAN_ORDER_URLS
#
#    lib_reader = get_object_or_404(LibReader, library=library, user=request.user)
#
#    urls = [
#        ruslan_order_urls['orders'] % (lib_reader.lib_login, lib_reader.lib_password, library.z_service ,lib_reader.lib_login),
#        ruslan_order_urls['books'] % (lib_reader.lib_login, lib_reader.lib_password, library.z_service, lib_reader.lib_login),
#    ]
#    results = ThreadWorker(_get_content,urls).do()
#    for result in results:
#        if isinstance(result, BaseException):
#            raise result
##    print results[0].value
#    orders = _get_orders(results[1].value)
#    books = _get_books(results[0].value)
#
#    return render(request, 'orders/frontend/lib_orders.html',{
#        'orders':orders,
#        'books': books,
#        'library':library
#    })
#
#@login_required
#def zorder(request, library_id):
#
#    record_id = request.GET.get('id', None)
#    if not record_id:
#        raise Http404()
#    library = get_object_or_404(Library, id=library_id)
#
#    # проверяем, привязан ли zgate к библиотеке чтобы можно было перенаправить на него
#    try:
#        zcatalog = ZCatalog.objects.get(latin_title=library.code)
#    except ZCatalog.DoesNotExist:
#        return HttpResponse(u'Библиотека не может принимать электронные заказы')
#
#    # ищем связь пользователя с библиотекой, чтобы автоматически авторизовать для заказа
#    # иначе перенаправляем для установления связи
#
#    try:
#        lib_reader = LibReader.objects.get(user=request.user, library=library)
#    except LibReader.DoesNotExist:
#        back =  request.get_full_path()
#        return redirect(urlresolvers.reverse('urt:frontend:auth',args=[library_id])+'?back='+back)
#
#
#    (zgate_form, cookies) = zworker.get_zgate_form(
#        zgate_url=zcatalog.url,
#        xml=zcatalog.xml,
#        xsl=zcatalog.xsl,
#        cookies=request.COOKIES,
#        username=lib_reader.lib_login,
#        password=lib_reader.lib_password,
#    )
#    session_id = zworker.get_zgate_session_id(zgate_form)
#    form_params =  zworker.get_form_dict(zgate_form)
#    del(form_params['scan']) # удаляем, иначе происходит сканирование :-)
#    form_params['use_1']='12:1.2.840.10003.3.1'
#    form_params['term_1']= record_id
#    (result, cookies) = zworker.request(zcatalog.url, data=form_params, cookies=cookies)
#
#    # анализируем полученный html на содержание текса с идентификатором записи - значит нашли
#    if  result.decode('utf-8').find(u'id="%s' % (record_id,)) >= 0:
#    #        link = reverse('zgate_index', args=(catalog.id,)) + '?zstate=preorder+%s+1+default+1+1.2.840.10003.5.28+rus' % session_id
#        link = zcatalog.url + '?preorder+%s+1+default+1+1.2.840.10003.5.28+rus' % session_id
#        resp =  redirect(link)
#        set_cookies_to_response(cookies, resp, domain='.kitap.tatar.ru')
#        return resp
#    return HttpResponse(u'Zgate order')
#
#
#
#
#def _get_content(url):
#    # необходимо чтобы функция имела таймаут
#    uh = urllib2.urlopen(url, timeout=10)
#    result = uh.read()
#    #    print result
#    return result
#
#
#def _get_orders(xml):
##    url='http://www.unilib.neva.ru/cgi-bin/zurles?z39.50r://%s:%s@ruslan.ru/ir-extend-1?8003330' % (lib_login, lib_password)
##    opener = urllib2.build_opener()
##    result = opener.open(url)
##    results = result.read()
#    print 'xml', xml
#    try:
#        orders_root = etree.XML(xml)
#    except etree.XMLSyntaxError:
#        return []
#
#    order_trees = orders_root.xpath('/result/eSTaskPackage')
#    orders = []
#    for order_tree in order_trees:
#        order = {}
#        record_tree = order_tree.xpath('taskSpecificParameters/targetPart/itemRequest/record')
#        if record_tree:
#            try:
#                bib_record = xslt_bib_draw_transformer(record_tree[0],abstract='false()')
#                order['record'] = etree.tostring(bib_record, encoding='utf-8').replace('<b/>', '')
#            except etree.XSLTApplyError as e:
#                order['record'] = e.message
#
#        status_or_error_report =  order_tree.xpath('taskSpecificParameters/targetPart/statusOrErrorReport')
#        if status_or_error_report:
#            order['status_or_error_report'] = status_or_error_report[0].text
#        else:
#            order['status_or_error_report'] = u'undefined'
#
#        target_reference =  order_tree.xpath('targetReference')
#        if target_reference:
#            order['target_reference'] = target_reference[0].text
#        else:
#            order['target_reference'] = u'undefined'
#
#        task_status =  order_tree.xpath('taskStatus')
#        if task_status:
#            status_titles = {
#                '0': u'Не выполнен',
#                '3': u'Отказ',
#                '1': u'Выполнен',
#                '2': u'Выдан'
#            }
#            order['task_status'] = status_titles.get(task_status[0].text,task_status[0].text)
#        else:
#            order['task_status'] = u'undefined'
#
#        creation_date_time =  order_tree.xpath('creationDateTime')
#        if creation_date_time:
#            try:
#                date =  datetime.datetime.strptime(creation_date_time[0].text, '%Y%m%d%H%M%S')
#            except ValueError:
#                date = u'value error'
#            order['creation_date_time'] = date
#        else:
#            order['creation_date_time'] = u'undefined'
#
#
#        orders.append(order)
#    return orders
#
#def _get_books(xml):
##    url='http://www.unilib.neva.ru/cgi-bin/zurlcirc?z39.50r://%s:%s@ruslan.ru/circ?8003330' % (lib_login, lib_password)
##    opener = urllib2.build_opener()
##    result = opener.open(url)
##    results = result.read()
#    try:
#        rcords_root = etree.XML(xml)
#    except etree.XMLSyntaxError:
#        return []
#    books = []
#    record_trees = rcords_root.xpath('/records/*')
#    for record_tree in record_trees:
#        book = {}
#        try:
#            bib_record = xslt_bib_draw_transformer(record_tree, abstract='false()')
#            book['record'] = etree.tostring(bib_record, encoding='utf-8')
#        except etree.XSLTApplyError as e:
#            book['record'] = e.message
#
#        description_tree = record_tree.xpath('field[@id="999"]/subfield[@id="z"]')
#        if description_tree:
#            book['description'] = description_tree[0].text
#        else:
#            book['description'] = u''
#        books.append(book)
#    return books
#
#
#
#
#

order_statuses_titles = {
    'new': 'принят на обработку',
    'recall': 'отказ',
    'conditional': 'в обработке',
    'shipped': 'доставлен',
    'pending': 'в ожидании',  #Доставлен
    'notsupplied': 'выполнение невозможно',
}

apdy_type_titles = {
    'ILLRequest': 'Заказ',
    'ILLAnswer': 'Ответ',
    'Shipped': 'Доставлен',
    'Recall': 'Задолженность',
}

apdu_reason_will_supply = {
    '1': 'Заказ будет выполнен позднее',
    '2': 'Необходимо повторить запрос позднее',
    '3': 'Отказ',
    '4': 'Получена информация о местонахождении документа',
    '5': 'Заказ будет выполнен позднее',
    '6': 'Запрос поставлен в очередь',
    '7': 'Получена информация о стоимости выполнения заказа',
}
apdu_unfilled_results = {
    '1': 'Документ выдан',
    '2': 'Документ в обработке',
    '3': 'Документ утерян и/или списан',
    '4': 'Документ не выдается',
    '5': 'Документа нет в фонде',
    '6': 'Документ заказан, но еще не получен ',
    '7': 'Том / выпуск еще не приобретен',
    '8': 'Документ в переплете',
    '9': 'Отсутствуют необходимые части / страницы документа',
    '10': 'Нет на месте',
    '11': 'Документ временно не выдается',
    '12': 'Документ в плохом состоянии',
    '13': 'Недостаточно средств для выполнения заказа',
    #'14':u'',
    #'15':u'Документ в плохом состоянии',
}

#Вид и статусы заказов, в зависимоти от которых можно удалять заказ
can_delete_statuses = {
    '1': ['shipped', 'received', 'notsupplied', 'checkedin'],  #document
    '2': ['shipped', 'received', 'notsupplied', 'checkedin'],  #copy
    '5': ['shipped', 'notsupplied', 'checkedin']  #reserve
}


def check_for_can_delete(transaction):
    """
    return True or False
    """
    for apdu in transaction.illapdus:
        if isinstance(apdu.delivery_status, ILLRequest):
            if apdu.delivery_status.ill_service_type in can_delete_statuses and \
                            transaction.status in can_delete_statuses[apdu.delivery_status.ill_service_type]:
                return True
    return False


import time
from ..templatetags.order_tags import org_by_id


@login_required
def index(request):
    user_id = request.user.username

    def format_time(datestr='', timestr=''):
        if datestr:
            datestr = time.strptime(datestr, "%Y%m%d")
            datestr = time.strftime("%d.%m.%Y", datestr)
        if timestr:
            timestr = time.strptime(timestr, "%H%M%S")
            timestr = time.strftime("%H:%M:%S", timestr)
        return datestr + ' ' + timestr

    order_manager = OrderManager(settings.ORDERS['db_catalog'], settings.ORDERS['rdx_path'])
    transactions = order_manager.get_orders(user_id)
    orgs = {}
    #for org_id in transactions_by_org:
    orders = []
    for transaction in transactions:
        #print ET.tostring(transaction.illapdus[0].delivery_status.supplemental_item_description, encoding="UTF-8")
        try:
            doc = etree.XML(etree.tostring(transaction.illapdus[0].delivery_status.supplemental_item_description,
                                           encoding="UTF-8"))
            result_tree = xslt_bib_draw_transformer(doc)
            res = str(result_tree)
        except Exception as e:
            raise e
        res = res.replace('– –', '—')
        res = res.replace('\n', '</br>')
        order = {}

        if transaction.status in order_statuses_titles:
            order['status'] = order_statuses_titles[transaction.status]
        else:
            order['status'] = transaction.status
        order['type'] = ''
        order['copy_info'] = ''
        order['apdus'] = []

        for apdu in transaction.illapdus:
            apdu_map = {}

            apdu_map['type'] = apdu.delivery_status.type
            if apdu.delivery_status.type in apdy_type_titles:
                apdu_map['type_title'] = apdy_type_titles[apdu.delivery_status.type]
            else:
                apdu_map['type_title'] = apdu.delivery_status.type

            apdu_map['datetime'] = format_time(apdu.delivery_status.service_date_time['dtots']['date'],
                                               apdu.delivery_status.service_date_time['dtots']['time'])

            if isinstance(apdu.delivery_status, ILLRequest):

                order['order_id'] = apdu.delivery_status.transaction_id['tq']
                order['org_info'] = org_by_id(apdu.delivery_status.responder_id['pois']['is'])
                if apdu.delivery_status.third_party_info_type['tpit']['stl']['stlt']['si']:
                    order['org_info'] = org_by_id(
                        apdu.delivery_status.third_party_info_type['tpit']['stl']['stlt']['si'])
                apdu_map['requester_note'] = apdu.delivery_status.requester_note
                order['record'] = res
                order['user_comments'] = apdu.delivery_status.requester_note
                apdu_map['record'] = res
                if apdu.delivery_status.ill_service_type == '1':
                    apdu_map['service_type'] = 'доставка'
                    order['type'] = 'doc'

                elif apdu.delivery_status.ill_service_type == '2':
                    apdu_map['service_type'] = 'копия'
                    order['type'] = 'copy'
                    order['copy_info'] = apdu.delivery_status.item_id['pagination']

                order['type_title'] = apdu_map['service_type']
                order['can_delete'] = check_for_can_delete(transaction)

            else:
                #print apdu.delivery_status.type
                apdu_map['responder_note'] = getattr(apdu.delivery_status, 'responder_note', None)
                if apdu.delivery_status.type == 'ILLAnswer':
                    apdu_map['reason_will_supply'] = apdu.delivery_status.results_explanation['wsr']['rws']
                    apdu_map['reason_will_supply_title'] = ''
                    if apdu_map['reason_will_supply'] in apdu_reason_will_supply:
                        apdu_map['reason_will_supply_title'] = apdu_reason_will_supply[apdu_map['reason_will_supply']]

                    apdu_map['unfilled_results'] = apdu.delivery_status.results_explanation['ur']['ru']
                    apdu_map['unfilled_results_title'] = ''
                    if apdu_map['unfilled_results'] in apdu_unfilled_results:
                        apdu_map['unfilled_results_title'] = apdu_unfilled_results[apdu_map['unfilled_results']]



            #apdu_map['record'] = res
            order['apdus'].append(apdu_map)
        orders.append(order)
        #if org_id in settings.LIBS:
    #    orgs[org_id] = settings.LIBS[org_id]
    #else:
    #    orgs[org_id] = org_id
    #orders_by_org[org_id] = orders



    return render(request, 'orders/frontend/mba_orders_list.html', {
        'orders': orders,
        'orgs': orgs
    })


def mba_order_reserve(request):
    if not request.user.is_authenticated:
        return HttpResponse('Вы должны быть войти на портал', status=401)

    if request.method == "POST":
        form = CopyOrderForm(request.POST, prefix='copy')
        if form.is_valid():
            try:
                _make_mba_order(
                    gen_id=form.cleaned_data['gen_id'],
                    user_id=request.user.id,
                    order_type='copy',
                    order_manager_id=form.cleaned_data['manager_id'],
                    copy_info=form.cleaned_data['copy_info'],
                    comments=form.cleaned_data['comments'],
                )
            except MBAOrderException as e:
                return HttpResponse('{"status":"error", "error":"%s"}' % e.message)

            return HttpResponse('{"status":"ok"}')
        else:
            response = {
                'status': 'error',
                'errors': form.errors
            }
            return HttpResponse(simplejson.dumps(response, ensure_ascii=False))
    else:
        return HttpResponse('{"status":"error", "error":"Only POST requests"}')


def mba_order_copy(request):
    if not request.user.is_authenticated:
        return HttpResponse('Вы должны быть войти на портал', status=401)

    if request.method == "POST":
        form = CopyOrderForm(request.POST, prefix='copy')
        if form.is_valid():
            try:
                _make_mba_order(
                    gen_id=form.cleaned_data['gen_id'],
                    user_id=request.user.id,
                    order_type='copy',
                    order_manager_id=form.cleaned_data['manager_id'],
                    copy_info=form.cleaned_data['copy_info'],
                    comments=form.cleaned_data['comments'],
                )
            except MBAOrderException as e:
                return HttpResponse('{"status":"error", "error":"%s"}' % e.message)

            return HttpResponse('{"status":"ok"}')
        else:
            response = {
                'status': 'error',
                'errors': form.errors
            }
            return HttpResponse(simplejson.dumps(response, ensure_ascii=False))
    else:
        return HttpResponse('{"status":"error", "error":"Only POST requests"}')


def mba_order_delivery(request):
    if not request.user.is_authenticated:
        return HttpResponse('Вы должны быть войти на портал', status=401)

    if request.method == "POST":
        form = DeliveryOrderForm(request.POST, prefix='delivery')
        if form.is_valid():
            try:
                _make_mba_order(
                    gen_id=form.cleaned_data['gen_id'],
                    user_id=request.user.id,
                    order_type='delivery',
                    order_manager_id=form.cleaned_data['manager_id'],
                    comments=form.cleaned_data['comments'],
                )
            except MBAOrderException as e:
                return HttpResponse('{"status":"error", "error":"%s"}' % e.message)
            return HttpResponse('{"status":"ok"}')
        else:
            response = {
                'status': 'error',
                'errors': form.errors
            }
            return HttpResponse(simplejson.dumps(response, ensure_ascii=False))
    else:
        return HttpResponse('{"status":"error", "error":"Only POST requests"}')


def _check_order_times(user, order_manager_id, order_type):
    order_time = datetime.datetime.now()

    order_copy_limit = 10
    order_document_limit = 10

    user_order_times = UserOrderTimes.objects.filter(
        user=user,
        order_manager_id=order_manager_id,
        order_type=order_type,
        order_time__year=order_time.year,
        order_time__month=order_time.month,
        order_time__day=order_time.day
    ).count()

    if order_type == 'delivery':
        if user_order_times >= order_document_limit:
            return False
    elif order_type == 'copy':
        if user_order_times >= order_copy_limit:
            return False
    else:
        raise ValueError('Wrong order type' + str(order_type))

    return True


def _save_order_time(user):
    user_order_times = UserOrderTimes(user=user, order_type=order_type, order_manager_id=order_manager_id)
    user_order_times.save()


def _make_mba_order(gen_id, user_id, order_type, order_manager_id, copy_info='', comments=''):
    user_id = str(user_id)
    order_types = ('delivery', 'copy')
    if order_type not in order_types:
        raise ValueError('Wrong order type ' + str(order_type))

    doc = None
    try:
        doc = Record.objects.using('records').get(gen_id=gen_id)
    except Record.DoesNotExist:
        pass
    if not doc:
        try:
            doc = Ebook.objects.using('records').get(gen_id=gen_id)
        except Ebook.DoesNotExist:
            raise MBAOrderException('Record not founded')

    order_manager = OrderManager(settings.ORDERS['db_catalog'], settings.ORDERS['rdx_path'])

    library = None
    try:
        library = Library.objects.get(id=order_manager_id)
    except Library.DoesNotExist:
        raise MBAOrderException('Library not founded')


    def get_first_recivier_code(library):
        ancestors = library.get_ancestors()
        for ancestor in ancestors:
            if ancestor.ill_service and ancestor.ill_service.strip():
                return ancestor.code
        return None

    # если у библиотеки указан ill адрес доставки, то пересылаем заказ ей
    if library.ill_service and library.ill_service.strip():
        manager_id = ''
        reciver_id = library.code

    # иначе ищем родителя, у которого есть адрес доставки
    else:
        manager_id = library.code
        reciver_id = get_first_recivier_code(library)

        if not reciver_id:
            raise MBAOrderException('Library cant manage orders')

    sender_id = user_id
    copy_info = copy_info

    order_manager.order_document(
        order_type=order_type,
        sender_id=sender_id,
        reciver_id=reciver_id,
        manager_id=manager_id,
        xml_record=doc.content,
        comments=comments,
        copy_info=copy_info
    )


@login_required
def delete_order(request, order_id):
    order_manager = OrderManager(settings.ORDERS['db_catalog'], settings.ORDERS['rdx_path'])
    transactions = order_manager.get_order(order_id=order_id.encode('utf-8'), user_id=str(request.user.id))
    if len(transactions):
        if check_for_can_delete(transactions[0]):
            pass
    order_manager.delete_order(order_id=order_id.encode('utf-8'), user_id=str(request.user.id))

    return redirect(reverse('orders:frontend:index'))


@csrf_exempt
def org_by_code(request):
    if request.method == 'POST' and 'code' in request.POST:
        library = get_object_or_404(Library, code=request.POST['code'])

        org = {
            'code': library.code,
            'title': library.name,
            'postal_address': getattr(library, 'postal_address', 'не указан'),
            'phone': getattr(library, 'phone', 'не указан'),
            'email': getattr(library, 'mail', 'не указан')
        }

        json = simplejson.dumps({'status': 'ok', 'org_info': org}, ensure_ascii=False)
        return HttpResponse(json)

    else:
        return HttpResponse('Only post requests')

def make_order(request):
    if not request.user.is_authenticated:
        return HttpResponse('Вы должны быть войти на портал', status=401)
    if request.method != 'POST':
        return HttpResponse('Only post requests');
    order_type = request.POST.get('type')
    order_manager_id = request.POST.get('org_id')  # организация, которая получит заказ
    order_time = datetime.datetime.now()

    order_copy_limit = 5
    order_document_limit = 5
    order_reserve_limit = 5

    # user_order_times = UserOrderTimes.objects.filter(
    #     user=request.user,
    #     order_manager_id=order_manager_id,
    #     order_type=order_type,
    #     order_time__year=order_time.year,
    #     order_time__month=order_time.month,
    #     order_time__day=order_time.day
    # ).count()
    user_order_times = 0
    if order_type == 'document':
        if user_order_times >= order_document_limit:
            return HttpResponse(simplejson.dumps(
                {'status': 'error', 'error': 'На сегодня Ваш лимит заказов на доставку в эту библиотеку исчерпан'},
                ensure_ascii=False))
    elif order_type == 'copy':
        if user_order_times >= order_copy_limit:
            return HttpResponse(simplejson.dumps(
                {'status': 'error', 'error': 'На сегодня Ваш лимит заказов на копию в эту библиотеку исчерпан'},
                ensure_ascii=False))
    elif order_type == 'reserve':
        if user_order_times >= order_reserve_limit:
            return HttpResponse(simplejson.dumps({'status': 'error',
                                                  'error': 'На сегодня Ваш лимит заказов на бронирование в эту библиотеку исчерпан'}
                                                 ,
                                                 ensure_ascii=False))

    else:
        return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Неизвестный тип заказа'},
                                             ensure_ascii=False))

    catalog = get_object_or_404(ZCatalog, latin_title=request.POST['catalog_id'])
    zgate_url = catalog.url

    zstate = 'present+' + request.POST['zsession'] + \
             '+default+' + request.POST['zoffset'] + \
             '+1+X+1.2.840.10003.5.28+' + catalog.default_lang

    (xml_record, cookies) = zworker.request(zgate_url + '?' + zstate, cookies=request.COOKIES)

    #определяем, сколько раз пользователь сдлела заказ за сегодня


    try:
        tree = ET.XML(xml_record)
    except SyntaxError as e:
        return HttpResponse(json_error('Заказ не выполнен. Возможно, время сессии истекло'))

    order_manager = OrderManager(settings.ORDERS['db_catalog'], settings.ORDERS['rdx_path'])

    library = None
    try:
        library = Library.objects.get(code=order_manager_id)
    except Library.DoesNotExist:
        return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Организация не найдена'}))

    def get_first_recivier_code(library):
        ancestors = library.get_ancestors()
        for ancestor in ancestors:
            if ancestor.ill_service and ancestor.ill_service.strip():
                return ancestor.code
        return None

    # если у библиотеки указан ill адрес доставки, то пересылаем заказ ей
    if library.ill_service and library.ill_service.strip():
        manager_id = ''
        reciver_id = library.code

    # иначе ищем родителя, у которого есть адрес доставки
    else:
        manager_id = library.code
        reciver_id = get_first_recivier_code(library)

        if not reciver_id:
            return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Организация не может получать заявки'}))

    sender_id = request.user.username  #id отправителя
    copy_info = request.POST.get('copy_info', '')

    # try:
    order_manager.order_document(
        order_type=order_type,
        sender_id=sender_id,
        reciver_id=reciver_id,
        manager_id=manager_id,
        xml_record=xml_record,
        comments=request.POST.get('comments', ''),
        copy_info=copy_info
    )
    user_order_times = UserOrderTimes(user=request.user, order_type=order_type, order_manager_id=order_manager_id)
    user_order_times.save()
    # except Exception as e:
    #     if settings.DEBUG == True:
    #         return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Ошибка при обработке заказа' + str(e)},
    #                                              ensure_ascii=False))
    #     else:
    #         return HttpResponse(simplejson.dumps({'status': 'error', 'error': 'Ошибка при обработке заказа'},
    #                                              ensure_ascii=False))
            #result = u'Заказ сделан '+ order_type +'<br/>'+xml_record.decode('utf-8')

    return HttpResponse(simplejson.dumps({'status': 'ok'}, ensure_ascii=False));
