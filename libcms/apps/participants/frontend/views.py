# -*- coding: utf-8 -*-
import json as simplejson
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, Http404
from django.utils import translation
from django.utils.translation import get_language
from common.pagination import get_page
from django.db.models import Q
from ..models import Library, District, LibraryType

def make_library_dict(library):

    lib_dict =  {
        'id': library.id,
        'code': library.code,
        'name': library.name,
        'postal_address': library.postal_address,
        'phone': library.phone,
        'plans': library.plans,
        'http_service': library.http_service,
        'latitude': library.latitude,
        'longitude': library.longitude,
    }
    if not lib_dict['postal_address']:
        lib_dict['postal_address'] = 'не указан'

    if not lib_dict['phone']:
        lib_dict['phone'] = 'не указан'

    if not lib_dict['plans']:
        lib_dict['plans'] = 'не указано'

    if not lib_dict['latitude']:
        lib_dict['latitude'] = 0

    if not lib_dict['longitude']:
        lib_dict['longitude'] = 0

    return lib_dict


def index(request):
    filter = False
    filter_title = ''
    letter = request.GET.get('letter')
    district = request.GET.get('district')
    ftype = request.GET.get('type')

    q = ()

    if letter:
        q &= Q(letter=letter)

    if district:
        q &=Q(district_id=district)

    if ftype:
        q &=Q(type_id=ftype)

#     if request.GET.get('letter', None):
#         filter = True
#         cbs_list = Library.objects.filter(letter=request.GET.get('letter')).order_by('name').exclude(parent=None)
#         filter_title = 'библиотеки на букву: ' + request.GET.get('letter')
#     if request.GET.get('district', None):
#         try:
#             int(request.GET.get('district'))
#         except ValueError:
#             pass
#         else:
#             filter = True
#             cbs_list = Library.objects.filter(district_id=request.GET.get('district')).order_by('name').exclude(parent=None)
#             filter_title = 'библиотеки района: '
#             try:
#                 district = District.objects.get(id=request.GET.get('district'))
#                 district_title = str(district)
#             except District.DoesNotExist:
#                 district_title = 'район не найден'
#             filter_title +=  district_title
#
#     if request.GET.get('type', None):
#         try:
#             int(request.GET.get('type'))
#         except ValueError:
#             pass
#         else:
#             filter = True
#             types = LibraryType.objects.filter(id=request.GET.get('type'))
#             cbs_list = Library.objects.filter(types__in=types).order_by('name').exclude(parent=None)
#             filter_title = 'библиотеки типа: '
# #            types = LibraryType.objects.filter(id__in=request.GET.get('type'))
#             type_titles = []
#             for type in types:
#                 type_titles.append(type.name)
#             filter_title +=  ', '.join(type_titles)


    if not q:
        cbs_list = Library.objects.filter(parent=None).order_by('name')
    else:
        cbs_list = Library.objects.filter(q).order_by('name').exclude(parent=None)

    js_orgs = []


    cbs_page = get_page(request, cbs_list)

    for org in cbs_page.object_list:
        js_orgs.append(make_library_dict(org))
    letters = []
    letters_libs = Library.objects.all().values('letter')
    for org in letters_libs:
        letters.append(org['letter'])

    js_orgs = simplejson.dumps(js_orgs, ensure_ascii=False)
    letters = list(set(letters))
    letters.sort()

    districts = District.objects.all()
    types = LibraryType.objects.all()
    return render(request, 'participants/frontend/cbs_list.html',{
        'cbs_list': cbs_page.object_list,
        'js_orgs': js_orgs,
        'letters': letters,
        'districts': districts,
        'types': types,
        'cbs_page': cbs_page,
        'filter': filter,
        'filter_title': filter_title
    })


def branches(request, code=None):
    if request.method == "POST":
        code = request.POST.get('code', None)
    library = None
    if code:
        library = get_object_or_404(Library, code=code)
    libraries = Library.objects.filter(parent=library).order_by('name')

    js_orgs = []
    for org in libraries:
        js_orgs.append(make_library_dict(org))

    js_orgs = simplejson.dumps(js_orgs, ensure_ascii=False)

    if request.is_ajax():
        return HttpResponse(js_orgs)

    return render(request, 'participants/frontend/branch_list.html',{
        'library': library,
        'libraries': libraries,
        'js_orgs': js_orgs
    })


def detail(request, code):
    library = get_object_or_404(Library, code=code)
    js_orgs = []
    js_orgs.append(make_library_dict(library))

    js_orgs = simplejson.dumps(js_orgs, ensure_ascii=False)

    return render(request, 'participants/frontend/detail.html',{
        'library': library,
        'js_orgs': js_orgs
    })


def get_branches_by_district(request):
    district_id = request.GET.get('district_id', None)
    if not district_id:
        return HttpResponse('[]')

    libraries = Library.objects.filter(district=int(district_id)).order_by('name').exclude(parent=None)
    js_orgs = []
    for library in libraries:
        js_orgs.append(make_library_dict(library))

    return  HttpResponse(simplejson.dumps(js_orgs, ensure_ascii=False))


def districts(request):
    filter = False
    filter_title = ''
    letter = request.GET.get('letter')
    district = request.GET.get('district')
    ftype = request.GET.get('type')

    q = Q()

    if letter:
        q &= Q(letter=letter)

    if district:
        q &= Q(district_id=district)

    if ftype:
        q &= Q(types__in=[ftype])
    cbs_list = None
    if not q:
        cbs_list = Library.objects.filter(q).order_by('weight', 'name')
    else:
        cbs_list = Library.objects.filter(q).order_by('weight', 'name').exclude(parent=None)
    # else:
    #     cbs_list = Library.objects.filter(parent=None).order_by('weight')

   # if not filter:
   #     cbs_list = Library.objects.filter(parent=None).order_by('weight')
    js_orgs = []

    cbs_page = None
    if cbs_list:
        cbs_page = get_page(request, cbs_list)
        cbs_list = cbs_page.object_list
        for org in cbs_page.object_list:
            js_orgs.append(make_library_dict(org))



    districts = District.objects.all().order_by('name')
    letters = []
    letters_libs = Library.objects.all().values('letter')
    for org in letters_libs:
        letters.append(org['letter'])
    letters = list(set(letters))
    letters.sort()
    types = LibraryType.objects.all()

    main_branches = []
    if cbs_list is None:
        main_branches = Library.objects.filter(main=True).order_by('name').exclude(parent=None)

    return render(request, 'participants/frontend/districts.html', {
        'cbs_list': cbs_list,
        'main_branches': main_branches,
        'js_orgs': js_orgs,
        'letters': letters,
        'districts': districts,
        'types': types,
        'cbs_page': cbs_page,
        'filter': filter,
        'filter_title': filter_title
    })