# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render, get_object_or_404, get_list_or_404, Http404, HttpResponse
import json as simplejson
from districts import districts_list, find_district
from .models import Library, District
from django.contrib.auth.decorators import login_required


def make_library_dict(library):
    return {
        'code': library.code,
        'title': library.name,
        'address': getattr(library, 'postal_address', "не указан"),
        'phone': getattr(library, 'phone', "не указан"),
        'plans': getattr(library, 'plans', "не указано"),
        'http_service': getattr(library, 'http_service', "не указан"),
        'latitude': library.latitude,
        'longitude': library.longitude,
        }


def index(request):

    library_systems = Library.objects.filter(parent=None).order_by('weight')
    letters = []
    for cbs in library_systems:
        letters.append(cbs.letter)
    letters = list(set(letters))
    return render(request, 'participants/cbs_list.html', {
        'orgs': library_systems,
        'letters': letters
    })

def detail(request, code):
    library = get_object_or_404(Library, code=code)
    # если цбс
    if not library.parent_id:
        libraries = Library.objects.filter(parent=library)
        orgs = []

        for org in libraries:
            orgs.append(make_library_dict(org))

        js_orgs = simplejson.dumps(orgs, ensure_ascii=False)
        return render(request, 'participants/participants_list_by_cbs.html', {
            'cbs_name': library.name,
            'cbs_code': library.code,
            'ldap_orgs': orgs,
            'js_orgs': js_orgs
        })
    else:
        orgs = []

        orgs.append(make_library_dict(library))

        js_orgs = simplejson.dumps(orgs, ensure_ascii=False)
        return render(request, 'participants/participants_detail_by_cbs.html', {
            'cbs_name': getattr(library.parent, 'name', None),
            'cbs_code': getattr(library.parent, 'code', None),
            'library': library,
            'js_orgs': js_orgs
        })
        pass



def detail_by_district(request, code):
    library = get_object_or_404(Library, code=code)

    orgs = [make_library_dict(library)]

    js_orgs = simplejson.dumps(orgs, ensure_ascii=False)
    return render(request, 'participants/participants_detail_by_district.html', {
        'library': library,
        'js_orgs': js_orgs
    })


def districts(request):
    return render(request, 'participants/districts_list.html', {
        'districts': districts_list
    })


def by_district(request, id):
    district = get_object_or_404(District, id=id)
    libraries = Library.objects.filter(district=district).exclude(parent=None)
    orgs = []
    for org in libraries:
        orgs.append(make_library_dict(org))

    js_orgs = simplejson.dumps(orgs, ensure_ascii=False)
    return render(request, 'participants/participants_list_by_districts.html', {
        'ldap_orgs': libraries,
        'district': district,
        'js_orgs': js_orgs
    })


def by_district_json(request):
    if request.method == 'POST' and 'district' in request.POST:
        district = request.POST['district']

        libraries = Library.objects.filter(district=district).exclude(parent=None)

        orgs = []
        for org in libraries:
            orgs.append({'id': org.id, 'title': org.name})

        json = simplejson.dumps(orgs, ensure_ascii=False)
        return HttpResponse(json)
    else:
        return HttpResponse('Only post requests')

@login_required
def xml_dump(request):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<organizations>', '<localization language="rus">']
    libraries = Library.objects.select_related().all()
    for library in libraries:
        if library.parent:
            lines.append('<org id="' + library.code + '">' + library.name + ' (' + library.parent.name + ')</org>')
        else:
            lines.append('<org id="' + library.code + '">' + library.name + '</org>')
    lines.append('</localization>')
    lines.append('</organizations>')
    return HttpResponse('\n'.join(lines))