# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404, redirect
from guardian.decorators import permission_required_or_403
from common.pagination import get_page
from django.contrib.auth import login, REDIRECT_FIELD_NAME

from pages.models import Page, Translate
from forms import PageForm, TranslateForm

#@permission_required_or_403('accounts.view_users')
def index(request):
    print REDIRECT_FIELD_NAME
    return render(request, 'pages/administration/index.html')





@permission_required_or_403('pages.add_page')
def pages_list(request, parent=None):
    if parent:
        parent = get_object_or_404(Page, id=parent)

    pages_page = get_page(request,  Page.objects.filter(parent=parent))

    return render(request, 'pages/administration/pages_list.html', {
        'parent': parent,
        'pages_page': pages_page,
    })




@permission_required_or_403('auth.add_page')
def create_page(request, parent_id=None):
    if parent_id:
        pass
    if request.method == 'POST':
        page_form = PageForm(request.POST, prefix='page_form')
        if page_form.is_valid():
            page_form.save()
    else:
        page_form = PageForm(prefix='page_form')

    return render(request, 'pages/administration/create_page.html', {
        'page_form': page_form
    })





@permission_required_or_403('auth.change_page')
def edit_page(request, id):
    pass



