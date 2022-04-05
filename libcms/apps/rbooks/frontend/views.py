# -*- coding: utf-8 -*-
import os
import io
import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs
from zipfile import ZipFile
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.utils import translation
from django.shortcuts import HttpResponse, Http404
from django.views.decorators.cache import never_cache
from ..models import ViewLog
from ssearch.frontend.views import get_content_dict, init_solr_collection
from ssearch.models import get_records


# from ssearch.models import get_records

class AccessDenied(Exception): pass


# def add_to_bookmarc(request):
#     if not request.user.is_authenticated:
#         return HttpResponse(u'Вы должны быть войти на портал', status=401)
#     if request.method == 'POST':


@never_cache
def show(request):
    if not request.user.is_authenticated:
        return redirect('rbooks:frontend:auth_required')

    code = request.GET.get('code', None)
    id = request.GET.get('id', None)

    if not code:
        raise Http404('Book not found')

    if not id:
        uc = init_solr_collection('uc')
        url = request.build_absolute_uri()
        result = uc.search(query='elink_s:"{url}"'.format(url=url.replace('\'', '\\\\')), rows=1)
        docs = result.get_docs()

        if docs:
            id = docs[0]['id']

    if not id:
        referer = request.META.get('HTTP_REFERER')
        if referer:
            ref_url = urlparse.urlparse(referer)
            q = parse_qs(ref_url.query)
            id = q.get('id', [''])[0]

    try:
        edoc2_path = get_edoc2_path(code)
        book_path = get_book_path(code, request.META.get('REMOTE_ADDR', '0.0.0.0'))
    except AccessDenied as e:
        return HttpResponse(str(e) + ' Ваш ip адрес: ' + request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if not book_path and not edoc2_path:
        raise Http404('Книга не найдена')

    # if not os.path.isfile(book_path):
    #     return  HttpResponse(u'Не найден edoc контейнер')

    cur_language = translation.get_language()
    locale_titles = {
        'ru': 'ru_RU',
        'en': 'en_US',
        'tt': 'tt_RU'
    }

    locale_chain = locale_titles.get(cur_language, 'en_US')

    if id:
        collection = ''
        records = get_records([id])
        if records:
            catalogs = get_content_dict(records[0]['tree']).get('catalog', [])
            if catalogs:
                collection = catalogs[0]
        view_log = ViewLog(doc_id=id, collection=collection)
        if request.user.is_authenticated:
            view_log.user_id = request.user.id
        ViewLog.objects.bulk_create([view_log])

    if edoc2_path and os.path.isfile(edoc2_path):
        return rbooks2(request, id)

    return render(request, 'rbooks/frontend/show.html', {
        'file_name': code,
        'locale_chain': locale_chain,
        'id': id,
    })

@never_cache
def book(request, book):
    try:
        book_path = get_book_path(book, request.META.get('REMOTE_ADDR', '0.0.0.0'))
    except AccessDenied as e:
        return HttpResponse(str(e) + ' Ваш ip адрес: ' + request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if not book_path or not os.path.isfile(book_path):
        raise Http404('Книга не найдена')
    token1 = request.GET.get('token1')
    xml = """\
<Document Version="1.0">\
<Source File="source.xml" URL="https://%s/dl/%s/draw/?part=Part0.zip&amp;book=%s&amp;version=1285566137"/>\
<FileURL>https://%s/dl/%s/draw/?part={part}&amp;book=%s</FileURL>\
<Token1>%s</Token1>\
<Permissions><AllowCopyToClipboard>true</AllowCopyToClipboard><AllowPrint>true</AllowPrint></Permissions>\
</Document>""" % (request.META['HTTP_HOST'], book, book, request.META['HTTP_HOST'], book, book, token1)

    zip_file_content = io.BytesIO()

    zip_file = ZipFile(zip_file_content, 'w')
    zip_file.writestr('doc.xml', xml.encode('utf-8'))
    zip_file.close()

    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=%s.zip" % book
    zip_file_content.seek(0)
    response.write(zip_file_content.read())

    return response


@never_cache
def draw(request, book):
    part = request.GET.get('part')

    try:
        book_path = get_book_path(book, request.META.get('REMOTE_ADDR', '0.0.0.0'))
    except AccessDenied as e:
        return HttpResponse(str(e))

    if not book_path or not os.path.isfile(book_path):
        raise Http404('Книга не найдена')

    zf = ZipFile(book_path)

    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=%s" % part
    response.write(zf.read(part))

    return response


def get_book_path(book, remote_adrr):
    return settings.RBOOKS['documents_directory'] + '/' + book + '.edoc'


def get_edoc2_path(book):
    return settings.RBOOKS['edoc2_directory'] + '/' + book + '.edoc2'


def stats(request):
    pass


def rbooks2(request, id=None):
    code = request.GET.get('code')
    if not code:
        raise Http404('Book not found')

    rbooks_session_server = 'http://localhost:9000/rbooks2'

    resp = requests.post(rbooks_session_server + '/session', params={
        'code': code,
        'key': '123456',
        'p': '1',
        't': '1'
    })

    rbooks_server = 'https://chelreglib.ru/rbooks2'

    file = '{rbooks_server}/edoc2?session={session}'.format(
        rbooks_server=rbooks_server,
        session=resp.text,

    )

    settings = '{rbooks_server}/rbooks2/rbooks2-settings.zip'.format(
        rbooks_server=rbooks_server,
    )

    return render(request, 'rbooks/frontend/rbooks2.html', {
        'file': file,
        'id': id,
        'rbooks_server': rbooks_server,
        'settings': settings
    })
