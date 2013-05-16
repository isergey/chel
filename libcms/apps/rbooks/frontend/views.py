# encoding: utf-8
from lxml import etree
import urllib
from hashlib import md5
from django.conf import settings
from django.shortcuts import render, HttpResponse, urlresolvers, Http404, redirect
from django.views.decorators.cache import cache_control
import rbooks_client
from in_memory_zip import InMemoryZip

RBOOKS_SETTINGS = settings.RBOOKS

def index(request):
    code = request.GET.get('code', None)
    if not code:
        raise Http404(u'Файл книги не найден')
    # li = rbooks_client.LinkInfo('weded', 'edwed')
    # pi = rbooks_client.PermissionsInfo(True, True, 'ewdwed')
    # di = rbooks_client.DownloadInfo('gergerg', 'rferf', 1212, 'wefwef')
    # doc_info = rbooks_client.DocumentInfo(li, 'wefweffg', 'wefwef', 'rgergrg', pi, 'token1', 'token2', 'provider_key1', [di])

    # print etree.tostring(doc_info.to_xml_element())

    return render(request, 'rbooks/frontend/index.html', {
        'code': code
    })

@cache_control(must_revalidate=True, max_age=86400)
def edoc(request):
    code = request.GET.get('code', None)
    if not code:
        raise Http404(u'Файл книги не найден')
    token1 = request.GET.get('token1', None)

    # if not token1:
    #     return HttpResponse(u'Нет параметра token1', status=400)

    part = request.GET.get('part', None)

    if not part:
        return create_content_result_document_read_head(token1, code)
    else:
        return create_content_result_document_read_part_x(code, part)



def key(request):
    code = request.GET.get('code', None)
    if not code:
        return HttpResponse(u'Нет параметра code', status=400)

    dh = request.GET.get('dh', None)
    if not dh:
        return HttpResponse(u'Нет параметра dh', status=400)

    sign = request.GET.get('sign', None)
    if not dh:
        return HttpResponse(u'Нет параметра sign', status=400)

    rbclient = rbooks_client.RBooksWebServiceClient(
        RBOOKS_SETTINGS['service_url'],
        RBOOKS_SETTINGS['documents_directory'],
        code, extension=''
    )
    responce = HttpResponse(content_type=u'text/plain')
    responce.write(rbclient.get_document_key(dh, sign))
    return responce


from django.views.decorators.http import condition
import time
@condition(etag_func=None)
def edoc_stream(request):
    code = request.GET.get('code', None)
    if not code:
        return HttpResponse(u'Нет параметра code', status=400)

    part = request.GET.get('part', None)
    if not part:
        return HttpResponse(u'Нет параметра part', status=400)

    resp = HttpResponse( stream_response_generator(code, part), mimetype='application/octet-stream')
    return resp

def stream_response_generator(code, part):
    rbclient = rbooks_client.RBooksWebServiceClient(
        RBOOKS_SETTINGS['service_url'],
        RBOOKS_SETTINGS['documents_directory'],
        code
    )
    iter_lines = rbclient.get_document_part_stream(part)
    for line in iter_lines:
        if line:
            yield line

    # yield "<html><body>\n"
    # for x in range(1,11):
    #     yield "<div>%s</div>\n" % x
    #     yield " " * 1024  # Encourage browser to render incrementally
    #     time.sleep(1)
    # yield "</body></html>\n"


def create_content_result_document_read_head(token1, code):
    rbclient = rbooks_client.RBooksWebServiceClient(
        RBOOKS_SETTINGS['service_url'],
        RBOOKS_SETTINGS['documents_directory'],
        code
    )
    fd = rbclient.get_document_file_info()
    document_info = create_document_info(rbclient, code, fd, token1)
    sign = rbclient.sign_data(document_info)
    imz = InMemoryZip()
    imz.append("doc.xml", document_info).append("doc.sig", sign)
    responce = HttpResponse(content_type='application/zip')
    responce.write(imz.read())
    return responce

def create_content_result_document_read_part_x(code, part):
    rbclient = rbooks_client.RBooksWebServiceClient(
        RBOOKS_SETTINGS['service_url'],
        RBOOKS_SETTINGS['documents_directory'],
        code
    )
    part = rbclient.get_document_part(part)
    #return redirect(part)
    response = HttpResponse(content_type='application/octet-stream')
    response.write(part)
    response['Cache-Control'] = 'private, max-age = 86400'
    return response



def create_document_info(rbclient, code, fd, token1):
    edoc_path =  urlresolvers.reverse('rbooks:frontend:edoc')
    key_path = urlresolvers.reverse('rbooks:frontend:key')


    ver = md5(fd).hexdigest()
    li = rbooks_client.LinkInfo(
        file='source.xml',
        url= edoc_path + '?code=%s&part=part0.zip&version=%s' % (code, ver)
    )

    file_url = edoc_path + '?code=%s&part={part}&version=%s' % (
        code,
        ver
    )

    pi = rbooks_client.PermissionsInfo(True, True)


    token2 = '1234567890'

    provider_key1 = rbclient.get_public_key1_string()

    key_url = key_path + '?code={code}&dh={dh}&sign={sign}'


    #di = rbooks_client.DownloadInfo('gergerg', 'rferf', 1212, 'wefwef')


    doc_info = rbooks_client.DocumentInfo(
        link_info=li,
        file_url=file_url,
        permissions_info=pi,
        token1=token1,
        token2=token2,
        provider_key1=provider_key1,
        key_url=key_url,
        print_url='111',
        downloads=[]
    )

    return etree.tostring(doc_info.to_xml_element(), encoding='utf-8', xml_declaration=True)