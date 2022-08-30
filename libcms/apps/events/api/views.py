import json
from typing import List, Optional
from django.conf import settings
from django.http import HttpResponse
from pydantic import BaseModel

from .. import models
from . import schema

LIMIT = 20
MEDIA_URL = settings.MEDIA_URL


def index(request):
    req = _get_request(request)
    event_model = models.Event.objects.all().first()
    event = event_from_model(event_model)
    return HttpResponse('')


def events(request):
    req = _get_request(request)
    items: List[schema.Event] = []
    for event_model in models.Event.objects.filter(id__gt=req.from_id).order_by('id')[:LIMIT].iterator():
        items.append(event_from_model(event_model))
    return schema_response(schema.Response(items=items))


def categories(request):
    items: List[schema.Category] = []
    for category in models.Category.objects.all().iterator():
        items.append(category_from_mode(category))
    return schema_response(schema.Response(items=items))


def age_categories(request):
    items: List[schema.AgeCategory] = []
    for age_category in models.AgeCategory.objects.all().iterator():
        items.append(age_category_from_mode(age_category))
    return schema_response(schema.Response(items=items))


def addresses(request):
    items: List[schema.Address] = []
    for address in models.Address.objects.all().iterator():
        items.append(address_from_model(address))
    return schema_response(schema.Response(items=items))


def schema_response(model: BaseModel):
    return HttpResponse(model.json(ensure_ascii=False), content_type='application/json')


def _get_request(request):
    from_id = request.GET.get('from_id', 0)
    return schema.Request(from_id=from_id)


def category_from_mode(category_model: models.Category):
    return schema.Category(
        code=category_model.code,
        parent=category_model.parent_id,
        title=category_model.title,
        order=category_model.order
    )


def age_category_from_mode(age_category_model: models.AgeCategory):
    return schema.AgeCategory(
        id=age_category_model.pk,
        age=age_category_model.age,
    )


def address_from_model(address_model: models.Address):
    return schema.Address(
        id=address_model.pk,
        parent=address_model.parent_id,
        title=address_model.title,
        address=address_model.address,
        contacts=address_model.contacts,
        geo_latitude=address_model.geo_latitude,
        geo_longitude=address_model.geo_latitude
    )


def event_from_model(event_model: models.Event):
    return schema.Event(
        id=event_model.pk,
        avatar=MEDIA_URL + str(event_model.avatar) if event_model.avatar else '',
        start_date=event_model.start_date,
        end_date=event_model.end_date,
        address=event_model.address,
        address_reference=event_model.address_reference_id,
        active=event_model.active,
        need_registration=event_model.need_registration,
        category=[category['code'] for category in event_model.category.values('code').all()],
        age_category=event_model.age_category_id,
        keywords=event_model.keywords,
        translation_html=event_model.translation_html,
        content=event_model.content.content,
        create_date=event_model.create_date
    )
