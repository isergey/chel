# -*- coding: utf-8 -*-
import os
import cStringIO
from zipfile import ZipFile
from django.conf import settings
from django.shortcuts import render
from django.utils import translation
from django.shortcuts import HttpResponse, Http404
from django.views.decorators.cache import never_cache
from ..models import ViewLog
from  ssearch.frontend.views import get_records, get_content_dict

class AccessDenied(Exception): pass

# def add_to_bookmarc(request):
#     if not request.user.is_authenticated():
#         return HttpResponse(u'Вы должны быть войти на портал', status=401)
#     if request.method == 'POST':


@never_cache
def show(request):
    code = request.GET.get('code', None)
    id = request.GET.get('id', None)

    try:
        book_path = get_book_path(code, request.META.get('REMOTE_ADDR', '0.0.0.0'))
    except AccessDenied as e:
        return HttpResponse(e.message + u' Ваш ip адрес: ' + request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if not book_path:
        raise Http404(u'Книга не найдена')

    if not os.path.isfile(book_path):
        return  HttpResponse(u'Не найден edoc контейнер')

    cur_language = translation.get_language()
    locale_titles = {
        'ru': 'ru_RU',
        'en': 'en_US',
        'tt': 'tt_RU'
    }

    locale_chain = locale_titles.get(cur_language, 'en_US')
    id = request.GET.get('id', u'')
    if id:
        collection = u''
        records = get_records([id])
        if records:
            catalogs = get_content_dict(records[0]['tree']).get('catalog', [])
            if catalogs:
                collection = catalogs[0]
        view_log = ViewLog(doc_id=id, collection=collection)
        if request.user.is_authenticated():
            view_log.user_id = request.user.id
        view_log.save()
    return render(request, 'rbooks/frontend/show.html', {
        'file_name': code,
        'locale_chain': locale_chain,
    })

@never_cache
def book(request, book):
    try:
        book_path = get_book_path(book, request.META.get('REMOTE_ADDR', '0.0.0.0'))
    except AccessDenied as e:
        return HttpResponse(e.message + u' Ваш ip адрес: ' + request.META.get('REMOTE_ADDR', '0.0.0.0'))
    if not book_path or not os.path.isfile(book_path):
        raise Http404(u'Книга не найдена')
    token1 = request.GET.get('token1')
    xml = """\
<Document Version="1.0">\
<Source File="source.xml" URL="http://%s/dl/%s/draw/?part=Part0.zip&amp;book=%s&amp;version=1285566137"/>\
<FileURL>http://%s/dl/%s/draw/?part={part}&amp;book=%s</FileURL>\
<Token1>%s</Token1>\
<Permissions><AllowCopyToClipboard>true</AllowCopyToClipboard><AllowPrint>true</AllowPrint></Permissions>\
</Document>""" % (request.META['HTTP_HOST'],book, book, request.META['HTTP_HOST'], book, book, token1)

    zip_file_content = cStringIO.StringIO()

    zip_file = ZipFile(zip_file_content, 'w')
    zip_file.writestr('doc.xml', xml)
    zip_file.close()

    response = HttpResponse(mimetype="application/zip")
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
        return HttpResponse(e.message)


    if not book_path or not os.path.isfile(book_path):
        raise Http404(u'Книга не найдена')
    zf = ZipFile(book_path)

    response = HttpResponse(mimetype="application/zip")
    response["Content-Disposition"] = "attachment; filename=%s" % part
    response.write(zf.read(part))

    return response


def get_book_path(book, remote_adrr):
     return settings.RBOOKS['documents_directory'] + '/' + book + '.edoc'



def stats(request):

    pass