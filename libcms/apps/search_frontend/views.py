import json
from typing import Union, Dict, List, Any

from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect, resolve_url
from django.utils.translation import get_language

from core.rest import endpoint
from .detail import services as detail_services
from .record_services import local_number_to_record_id
from .saved_request import entities as saved_request_entities
from .saved_request import services as saved_request_services
from .search import entities as search_entities
from .search.deps import get_search_service, get_ui_config
from .statistics import services as statistics_services


DEFAULT_CATALOG = 'default'


def index(request):
    return render(request, 'new/search/frontend/index.html')


def detail_tpl(request):
    local_number = request.GET.get('ln')

    if local_number:
        record_id = local_number_to_record_id(local_number=local_number)
        if record_id:
            return redirect(resolve_url('search_frontend:detail_tpl') + '?id=' + record_id)
    return render(request, 'new/search/frontend/detail.html')


@endpoint
def search(request):
    catalog_code = request.GET.get('cc') or DEFAULT_CATALOG
    lang = get_language()
    json_request = json.loads(request.body)
    search_request = search_entities.SearchRequest.from_json(json_request)

    search_service = get_search_service(
        catalog_code=catalog_code,
        lang=lang,
        is_superuser=request.user.is_superuser
    )

    response = search_service.search(search_request)
    return __json_response(response)


@endpoint
def facets(request):
    catalog_code = request.GET.get('cc') or DEFAULT_CATALOG
    lang = get_language()

    json_request = json.loads(request.body)
    facet_request = search_entities.FacetsRequest.from_json(json_request)
    search_service = get_search_service(
        catalog_code=catalog_code,
        lang=lang,
        is_superuser=request.user.is_superuser
    )

    response = search_service.get_facets(facet_request)
    return __json_response(response)


@endpoint
def facet(request):
    catalog_code = request.GET.get('cc') or DEFAULT_CATALOG
    lang = get_language()

    json_request = json.loads(request.body)
    facet_request = search_entities.FacetRequest.from_json(json_request)

    search_service = get_search_service(
        catalog_code=catalog_code,
        lang=lang,
        is_superuser=request.user.is_superuser
    )

    response = search_service.get_facet(facet_request)
    return __json_response(response)


@endpoint
def detail(request):
    session_id = __get_session_id(request)

    record_id = request.GET.get('id')

    bib_record_detail = detail_services.detail(
        record_id=record_id,
        user=request.user
    )

    if bib_record_detail is None:
        raise Http404('Record not found')

    from_subscribe = request.GET.get('fscr', None) is not None

    statistics_services.log_record_detail(
        record_id=record_id,
        user=request.user,
        session_id=session_id,
        from_subscribe=from_subscribe,
    )
    return __json_response(bib_record_detail)


@endpoint
def more_like_this(request):
    record_id = request.GET.get('record_id')
    response = detail_services.get_more_like_this_records(record_id=record_id)
    return __json_response(response)


@endpoint
def linked_records(request):
    record_id = request.GET.get('record_id')
    response = detail_services.get_linked_records(record_id)
    return __json_response(response)


@endpoint
def related_issues(request):
    record_id = request.GET.get('record_id')
    response = detail_services.get_related_issues(record_id)
    return __json_response(response)


@endpoint
def ui_config(request):
    lang = get_language()

    config = get_ui_config(
        lang=lang,
        is_staff=request.user.is_superuser or request.user.is_staff
    )

    if config is None:
        raise Http404('config not found')

    return __json_response(config)


@endpoint
def statistics(request):
    record_id = request.GET.get('record_id')
    statistics = statistics_services.get_record_statistics(record_id=record_id)
    return __json_response(statistics)


@endpoint
def record_dump(request):
    record_id = request.GET.get('record_id')
    result = detail_services.get_record_dump(record_id=record_id)
    return __json_response(result)


@endpoint
def save_request(request):
    json_request = json.loads(request.body)
    saved_request = saved_request_entities.SavedRequest.from_json(json_request)

    saved_request_services.save_request(
        saved_request=saved_request,
        user=request.user
    )

    return __ok_response()


def __json_response(data: Union[Dict, List, Any]):
    if type(data) == dict or type(data) == list:
        return JsonResponse(data, json_dumps_params=dict(ensure_ascii=False))
    return JsonResponse(data.to_json(), json_dumps_params=dict(ensure_ascii=False))


def __id_response(oid: str, created=False):
    status = 201 if created else 200
    return JsonResponse({'id': str(oid)}, json_dumps_params=dict(ensure_ascii=False), status=status)


def __ok_response():
    return __json_response({'status': 'ok'})


def __string_response(value: str):
    return HttpResponse(value, content_type='text/plain; charset=utf-8')

def __get_session_id(request):
    return ''