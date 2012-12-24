# encoding: utf-8
from django.db import transaction
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from guardian.decorators import permission_required_or_403
from django.contrib.auth.decorators import login_required
from common.pagination import get_page

from ..models import ImportantDate
from forms import TypeForm, ImportantDateForm

@login_required
def index(request):
    return render(request, 'cid/administration/index.html')

@login_required
def id_list(request):
    idates_page =  get_page(request, ImportantDate.objects.select_related('theme').all().order_by('-id'))
    return render(request, 'cid/administration/id_list.html', {
        'idates_page': idates_page
    })

@login_required
@transaction.commit_on_success
def create_id(request):
    if request.method == 'POST':
        form = ImportantDateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cid:administration:id_list')
    else:
        form = ImportantDateForm()
    return render(request, 'cid/administration/create_id.html', {
        'form': form
    })

@login_required
@transaction.commit_on_success
def edit_id(request, id):
    idate = get_object_or_404(ImportantDate, id=id)
    if request.method == 'POST':
        form = ImportantDateForm(request.POST, instance=idate)
        if form.is_valid():
            form.save()
            return redirect('cid:administration:id_list')
    else:
        form = ImportantDateForm(instance=idate)
    return render(request, 'cid/administration/edit_id.html', {
        'form': form
    })

@login_required
@transaction.commit_on_success
def delete_id(request, id):
    idate = get_object_or_404(ImportantDate, id=id)
    idate.delete()
    return redirect('cid:administration:id_list')

#def theme_list(request):
#    themes_page = get_page(request, Theme.objects.all().order_by('-id'))
#    return render(request, 'cid/administration/theme_list.html', {
#        'themes_page': themes_page
#    })

#def create_theme(request):
#
#    if request.method == 'POST':
#        form = ThemeForm(request.POST)
#        if form.is_valid():
#            form.save()
#            return redirect('cid:administration:theme_list')
#    else:
#        form = ThemeForm()
#
#    return render(request, 'cid/administration/create_theme.html', {
#        'form': form
#    })


#def edit_theme(request, id):
#    theme = get_object_or_404(Theme, id=id)
#    if request.method == 'POST':
#        form = ThemeForm(request.POST, instance=theme)
#        if form.is_valid():
#            form.save()
#            return redirect('cid:administration:theme_list')
#    else:
#        form = ThemeForm(instance=theme)
#
#    return render(request, 'cid/administration/edit_theme.html', {
#        'form': form
#    })