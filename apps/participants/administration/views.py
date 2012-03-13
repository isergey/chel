# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from guardian.decorators import permission_required_or_403
from common.pagination import get_page
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.utils.translation import to_locale, get_language

from participants.models import Library, LibraryType
from forms import LibraryForm, LibraryTypeForm
#@permission_required_or_403('accounts.view_users')
def index(request):
    return render(request, 'participants/administration/index.html')



@permission_required_or_403('participants.add_library')
def list(request, parent=None):
    if parent:
        parent = get_object_or_404(Library, id=parent)

    libraries_page = get_page(request, Library.objects.filter(parent=parent))

    return render(request, 'participants/administration/libraries_list.html', {
        'parent': parent,
        'libraries_page': libraries_page,
        })


@permission_required_or_403('participants.add_library')
def create(request, parent=None):
    if parent:
        parent = get_object_or_404(Library, id=parent)

    if request.method == 'POST':
        library_form = LibraryForm(request.POST, prefix='library_form')

        if library_form.is_valid():
            library = library_form.save(commit=False)
            if parent:
                library.parent = parent
            library.save()
            if parent:
                return redirect('participants:administration:list', parent=parent.id)
            else:
                return redirect('participants:administration:list')
    else:
        library_form = LibraryForm(prefix='library_form')

    return render(request, 'participants/administration/create_library.html', {
        'parent': parent,
        'library_form': library_form,
        })

@permission_required_or_403('participants.change_library')
def edit(request, id):
    library =  get_object_or_404(Library, id=id)
    parent = library.parent

    if request.method == 'POST':
        library_form = LibraryForm(request.POST, prefix='library_form', instance=library)

        if library_form.is_valid():
            library = library_form.save(commit=False)

            library.save()
            if parent:
                return redirect('participants:administration:list', parent=parent.id)
            else:
                return redirect('participants:administration:list')
    else:
        library_form = LibraryForm(prefix='library_form', instance=library)

    return render(request, 'participants/administration/edit_library.html', {
        'parent': parent,
        'library_form': library_form,
        })



@permission_required_or_403('participants.delete_library')
def delete(request, id):
    library = get_object_or_404(Library, id=id)
    parent = library.parent
    library.delete()
    if parent:
        return redirect('participants:administration:list', parent=parent.id)
    else:
        return redirect('participants:administration:list')



@permission_required_or_403('participants.add_library')
def library_types_list(request):

    library_types_page = get_page(request, LibraryType.objects.all())

    return render(request, 'participants/administration/library_types_list.html', {
        'library_types_page': library_types_page,
        })



@permission_required_or_403('participants.add_library')
def library_type_create(request):

    if request.method == 'POST':
        library_types_form = LibraryTypeForm(request.POST)

        if library_types_form.is_valid():
            library_types_form.save()
            return redirect('participants:administration:library_types_list')
    else:
        library_types_form = LibraryTypeForm()

    return render(request, 'participants/administration/create_library_type.html', {
        'library_form': library_types_form,
        })


@permission_required_or_403('participants.add_library')
def library_type_edit(request, id):
    library_type =  get_object_or_404(LibraryType, id=id)
    if request.method == 'POST':
        library_types_form = LibraryTypeForm(request.POST, instance=library_type)

        if library_types_form.is_valid():
            library_types_form.save()
            return redirect('participants:administration:library_types_list')
    else:
        library_types_form = LibraryTypeForm(instance=library_type)

    return render(request, 'participants/administration/edit_library_type.html', {
        'library_form': library_types_form,
        })


@permission_required_or_403('participants.add_library')
def library_type_delete(request, id):
    library_type =  get_object_or_404(LibraryType, id=id)
    library_type.delete()
    return redirect('participants:administration:library_types_list')