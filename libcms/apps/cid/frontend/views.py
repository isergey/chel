# encoding: utf-8
import datetime
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from common.pagination import get_page
from ..models import ImportantDate, Type, Theme

def index(request):
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    day = request.GET.get('day', None)
    theme = request.GET.get('theme', None)
    type = request.GET.get('type', None)
    events = []
    errors = []



    q = Q()
    try:
        if year:
            errors += int_validator(year, u'Год')
            errors += max_validator(int(year), 9999, u'Год')
            errors += min_validator(int(year), 1, u'Год')
            q = q & Q(date__year=year)

        if month:
            errors += int_validator(month, u'Месяц')
            errors += max_validator(int(month), 12, u'Месяц')
            errors += min_validator(int(month), 1, u'Месяц')
            q = q & Q(date__month=month)

        if day:
            errors += int_validator(day, u'День')
            errors += max_validator(int(day), 31, u'День')
            errors += min_validator(int(day), 1, u'День')
            q = q & Q(date__day=day)

        if theme:
            errors += int_validator(theme, u'Тема')
            q = q & Q(theme_id=int(theme))

        if type:
            errors += int_validator(type, u'Тип')
            q = q & Q(type__id=int(type))

    except ValueError as e:
        pass

    if not errors:
        events_page = get_page(request, ImportantDate.objects.select_related('theme').filter(q).order_by('-date'))

    now = datetime.datetime.now()

    themes = Theme.objects.all()
    types = Type.objects.all()

    return render(request, 'cid/frontend/index.html', {
        'now': now,
        'events': events,
        'events_page': events_page,
        'themes': themes,
        'types': types,
        'errors': errors
    })



def detail(request, id):
    idate = get_object_or_404(ImportantDate, id=id)
    return render(request, 'cid/frontend/show.html', {
        'idate': idate
    })


def int_validator(value, label=u'Аргумент'):
    errors = []
    try:
        int(value)
    except ValueError as e:
        errors.append(label + u' не является целым числом')
    return errors


def min_validator(value, min_value, label=u'Аргумент'):
    errors = []
    if value < min_value:
        errors.append(label + u' не может быть меньше ' + unicode(min_value))
    return errors


def max_validator(value, max_value, label=u'Аргумент'):
    errors = []
    if value > max_value:
        errors.append(label + u' не может быть больше ' + unicode(max_value))
    return errors