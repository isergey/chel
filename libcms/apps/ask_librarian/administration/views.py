# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import transaction
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import HttpResponseForbidden
from guardian.decorators import permission_required_or_403
from django.contrib.auth.decorators import login_required
from common.pagination import get_page
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.utils.translation import to_locale, get_language

from core.forms import LanguageForm
#from menu.models import Menu, MenuTitle, MenuItem, MenuItemTitle
#from forms import MenuForm,MenuTitleForm,  CategoryForm, CategoryTitleForm
from ..models import Category, CategoryTitle
from forms import CategoryForm, CategoryTitleForm



#@permission_required_or_403('accounts.view_users')
@login_required
def index(request):
    if not request.user.has_module_perms('ask_librarian'):
        return HttpResponseForbidden()

    return render(request, 'ask_librarian/administration/index.html')


@login_required
def categories_list(request):
    if not request.user.has_module_perms('ask_librarian'):
        return HttpResponseForbidden()
    nodes = list(Category.objects.all())
    lang=get_language()[:2]
    category_titles = CategoryTitle.objects.filter(category__in=nodes, lang=lang)
    nd = {}
    for node in nodes:
        nd[node.id] = node

    for category_title in category_titles:
        nd[category_title.category_id].t_title = category_title

    return render(request, 'ask_librarian/administration/categories_list.html', {
        'nodes': nodes,
#        'menu': menu
    })


@login_required
@permission_required_or_403('ask_librarian.add_category')
@transaction.commit_on_success
def category_create(request, parent=None):

    if  parent:
        parent = get_object_or_404(Category, id=parent)

    if request.method == 'POST':
        category_form = CategoryForm(request.POST,prefix='category_form')

        category_title_forms = []
        for lang in settings.LANGUAGES:
            category_title_forms.append({
                'form':CategoryTitleForm(request.POST,prefix='category_title_' + lang[0]),
                'lang':lang[0]
            })

        if category_form.is_valid():

            category = category_form.save(commit=False)
            category.parent = parent
            category.save()

            valid = False
            for category_title_form in category_title_forms:
                valid = category_title_form['form'].is_valid()
                if not valid:
                    break
            if valid:
                for category_title_form in category_title_forms:
                    category_title = category_title_form['form'].save(commit=False)
                    category_title.lang = category_title_form['lang']
                    category_title.category = category
                    category_title.save()
                return redirect('ask_librarian:administration:categories_list')
    else:
        category_form = CategoryForm(prefix="category_form")
        category_title_forms = []
        for lang in settings.LANGUAGES:
            category_title_forms.append({
                'form':CategoryTitleForm(prefix='category_title_' + lang[0]),
                'lang':lang[0]
            })

    return render(request, 'ask_librarian/administration/create_category.html', {
        'category_form': category_form,
        'category_title_forms': category_title_forms,
    })



@login_required
@permission_required_or_403('ask_librarian.change_category')
@transaction.commit_on_success
def category_edit(request, id):

    category = get_object_or_404(Category, id=id)
    category_titles = CategoryTitle.objects.filter(category=category)

    category_titles_langs = {}
    for lang in settings.LANGUAGES:
        category_titles_langs[lang] = None


    for category_title in category_titles:
        category_titles_langs[category_title.lang] = category_title

    if request.method == 'POST':
        category_form = CategoryForm(request.POST,prefix='category_form', instance=category)

        category_title_forms = []
        for lang in settings.LANGUAGES:
            category_title_forms.append({
                'form':CategoryTitleForm(request.POST,prefix='category_title_' + lang[0]),
                'lang':lang[0]
            })

        if category_form.is_valid():

            category = category_form.save(commit=False)
            category.parent = parent
            category.save()

            valid = False
            for category_title_form in category_title_forms:
                valid = category_title_form['form'].is_valid()
                if not valid:
                    break
                #            print 'valid', valid
            if valid:
                for category_title_form in category_title_forms:
                    category_title = category_title_form['form'].save(commit=False)
                    category_title.lang = category_title_form['lang']
                    category_title.category = category
                    category_title.save()
                return redirect('ask_librarian:administration:categories_list')
    else:
        category_form = CategoryForm(prefix="category_form")
        category_title_forms = []
        for lang in settings.LANGUAGES:
            category_title_forms.append({
                'form':CategoryTitleForm(prefix='category_title_' + lang[0]),
                'lang':lang[0]
            })

    return render(request, 'ask_librarian/administration/create_category.html', {
        'category_form': category_form,
        'category_title_forms': category_title_forms,
        })




@login_required
@permission_required_or_403('menu.change_menucategory')
@transaction.commit_on_success
def category_edit(request, id,):
    category = get_object_or_404(Category, id=id)
    category_titles = CategoryTitle.objects.filter(category=category)

    category_titles_langs = {}
    for lang in settings.LANGUAGES:
        category_titles_langs[lang] = None


    for category_title in category_titles:
        category_titles_langs[category_title.lang] = category_title



    if request.method == 'POST':
        category_form = CategoryForm(request.POST, prefix='category_form', instance=category)
        category_title_forms = []
        for lang in settings.LANGUAGES:
            if lang in category_titles_langs:
                lang = lang[0]
                if lang in category_titles_langs:
                    category_title_forms.append({
                        'form':CategoryTitleForm(request.POST,prefix='category_title_' + lang, instance=category_titles_langs[lang]),
                        'lang':lang
                    })
                else:
                    category_title_forms.append({
                        'form':CategoryTitleForm(request.POST,prefix='category_title_' + lang),
                        'lang':lang
                    })

        valid = False
        for category_title_form in category_title_forms:
            valid = category_title_form['form'].is_valid()
            if not valid:
                break


        if not category_form.is_valid():
            valid = False

        if valid:
            category = category_form.save()
            for category_title_form in category_title_forms:
                category_title = category_title_form['form'].save(commit=False)
                category_title.category = category
                category_title.lang = category_title_form['lang']
                category_title.save()

            if not category.is_leaf_node():
                dcategorys = category.get_descendants()
                for dcategory in dcategorys:
                    dcategory.save()

            return redirect('ask_librarian:administration:categories_list')


    else:
        category_form = CategoryForm(prefix="category_form", instance=category)
        category_title_forms = []
        for lang in settings.LANGUAGES:
            lang = lang[0]
            if lang in category_titles_langs:
                category_title_forms.append({
                    'form':CategoryTitleForm(prefix='category_title_' + lang, instance=category_titles_langs[lang]),
                    'lang':lang
                })
            else:
                category_title_forms.append({
                    'form':CategoryTitleForm(prefix='category_title_' + lang),
                    'lang':lang
                })

    return render(request, 'ask_librarian/administration/edit_category.html', {
        'category_form': category_form,
        'category_title_forms': category_title_forms,
        'category': category
    })



#
@login_required
@permission_required_or_403('menu.delete_menucategory')
def category_delete(request, id):
    category = get_object_or_404(Category, id=id)
    category.delete()
    return redirect('ask_librarian:administration:categories_list')

#
#def category_up(request, menu_id, id):
#    category = get_object_or_404(MenuItem, id=id)
#    category.up()
#    return redirect('menu:administration:category_list', menu_id=menu_id)
#
#def category_down(request, menu_id, id):
#    category = get_object_or_404(MenuItem, id=id)
#    category.down()
#    return redirect('menu:administration:category_list', menu_id=menu_id)


