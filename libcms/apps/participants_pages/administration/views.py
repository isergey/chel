# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext as _
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import HttpResponseForbidden
from guardian.decorators import permission_required_or_403
from django.contrib.auth.decorators import login_required
from common.pagination import get_page
from django.contrib.auth import login, REDIRECT_FIELD_NAME
from django.utils.translation import to_locale, get_language

from core.forms import LanguageForm
from ..models import Page, Content
from .forms import get_content_form, get_page_form
from participants.models import Library, LibraryContentEditor
from ..version import save_content_version


def get_cbs(library_node):
    if library_node.parent_id:
        return library_node.get_root()
    else:
        return library_node

def check_owning(user, library):
    if user.is_superuser:
        return True
    else:
        if LibraryContentEditor.objects.filter(user=user, library=library).count():
            return True
        else:
            return False

#@permission_required_or_403('accounts.view_users')
def index(request, code):
    return redirect('participants_pages:administration:pages_list', code=code)


@login_required
def pages_list(request, code, parent=None):
    if not request.user.has_module_perms('participants_pages'):
        return HttpResponseForbidden()
    library = get_object_or_404(Library, code=code)


    if parent:
        parent = get_object_or_404(Page, id=parent)

    pages_page = get_page(request, Page.objects.filter(parent=parent, library=library).exclude(deleted=True))
    pages_page.object_list = list(pages_page.object_list)
    pages = pages_page.object_list
    contents = list(Content.objects.filter(page__in=pages, lang=get_language()[:2]))

    pages_dict = {}
    for page in pages:
        pages_dict[page.id] = {'page':page}

    for content in contents:
        pages_dict[content.page_id]['page'].content = content

#    pages = [page['page'] for page in pages_dict.values()]
#    pages = pages_page.object_list

    return render(request, 'participants_pages/administration/pages_list.html', {
        'parent': parent,
        'pages': pages,
        'pages_page': pages_page,
        'library': library
    })

@login_required
@permission_required_or_403('participants_pages.add_page')
def create_page(request, code, parent=None):
    library = get_object_or_404(Library, code=code)
    cbs = get_cbs(library)
    if not check_owning(request.user, cbs):
        return HttpResponse('У Вас нет прав на создание страниц в этой ЦБС')
    if parent:
        parent = get_object_or_404(Page, id=parent)
    PageForm = get_page_form(library, parent)
    if request.method == 'POST':
        page_form = PageForm(request.POST, prefix='page_form')
        if page_form.is_valid():
            page = page_form.save(commit=False)
            if parent:
                page.parent = parent

            if not request.user.has_perm('participants_pages.public_page'):
                page.public = False
            page.library = library
            page.save()
            return redirect('participants_pages:administration:create_page_content', page_id=page.id, code=code)
    else:
        page_form = PageForm(prefix='page_form')

    return render(request, 'participants_pages/administration/create_page.html', {
        'parent': parent,
        'page_form': page_form,
        'library': library
     })

@login_required
@permission_required_or_403('participants_pages.change_page')
def edit_page(request, code, id):

    library = get_object_or_404(Library, code=code)
    cbs = get_cbs(library)
    if not check_owning(request.user, cbs):
        return HttpResponse('У Вас нет прав на редактирование страницы в этой ЦБС')

    langs = []
    for lang in settings.LANGUAGES:
        langs.append({
            'code': lang[0],
            'title': _(lang[1])
        })

    page = get_object_or_404(Page, id=id, deleted=False)
    PageForm = get_page_form(library, page.parent_id)
    if request.method == 'POST':
        page_form = PageForm(request.POST, prefix='page_form', instance=page)
        page_form.is_valid()
        if page_form.is_valid():
            page = page_form.save(commit=False)
            if not request.user.has_perm('participants_pages.public_page'):
                page.public = False
            page.save()
            return redirect('participants_pages:administration:pages_list', code=code)

    else:
        page_form = PageForm(prefix='page_form', instance=page)

    return render(request, 'participants_pages/administration/edit_page.html', {
        'page': page,
        'langs': langs,
        'page_form': page_form,
        'library': library
    })

#@login_required
#@permission_required_or_403('pages.public_page')
#def toggle_page_public(request, id):
#    page = get_object_or_404(Page, id=id)
#    if page.public:
#        page.public = False
#    else:
#        page.public = True
#    page.save()
#    return redirect('pages:administration:pages_list')



@login_required
@permission_required_or_403('participants_pages.delete_page')
def delete_page(request, code, id):
    library = get_object_or_404(Library, code=code)
    cbs = get_cbs(library)
    if not check_owning(request.user, cbs):
        return HttpResponse('У Вас нет прав на удаление страницы в этой ЦБС')
    page = get_object_or_404(Page, id=id, deleted=False)
    page.deleted = True
    page.save()
    return redirect('participants_pages:administration:pages_list', code=code)



@login_required
@permission_required_or_403('participants_pages.add_page')
def create_page_content(request, code, page_id):
    library = get_object_or_404(Library, code=code)
    cbs = get_cbs(library)
    if not check_owning(request.user, cbs):
        return HttpResponse('У Вас нет прав на создание страницы в этой ЦБС')
    page = get_object_or_404(Page, id=page_id)
    ContentForm = get_content_form(('page',))
    if request.method == 'POST':
        content_form = ContentForm(request.POST, prefix='content_form')

        if content_form.is_valid():
            content = content_form.save(commit=False)
            content.page = page
            content.save()
            save_content_version(content, request.user)
            save = request.POST.get('save', 'save_edit')
            if save == 'save':
                return redirect('participants_pages:administration:edit_page', id=page_id, code=code)
            else:
                return redirect('participants_pages:administration:edit_page_content', page_id=page_id, lang=content.lang)
    else:
        content_form = ContentForm(prefix='content_form')
    return render(request, 'participants_pages/administration/create_page_content.html', {
        'page': page,
        'content_form': content_form,
        'library': library
    })

@login_required
@permission_required_or_403('participants_pages.change_page')
def edit_page_content(request, code,  page_id, lang):
    library = get_object_or_404(Library, code=code)
    cbs = get_cbs(library)
    if not check_owning(request.user, cbs):
        return HttpResponse('У Вас нет прав на редактирование страницы в этой ЦБС')
    lang_form = LanguageForm({'lang': lang})
    if not lang_form.is_valid():
        return HttpResponse(_('Language is not registered in system.') + _(" Language code: ") + lang)

    page = get_object_or_404(Page, id=page_id)

    try:
        content = Content.objects.get(page=page_id, lang=lang)
    except Content.DoesNotExist:
        content = Content(page=page, lang=lang)

    ContentForm = get_content_form(('page', 'lang'))

    if request.method == 'POST':
        content_form = ContentForm(request.POST, prefix='content_form', instance=content)

        if content_form.is_valid():
            content = content_form.save(commit=False)
            content.page = page
            content.save()
            save_content_version(content, request.user)
        save = request.POST.get('save', 'save_edit')
        if save == 'save':
            return redirect('participants_pages:administration:edit_page', id=page_id, code=code)

    else:
        content_form = ContentForm(prefix='content_form', instance=content)
    return render(request, 'participants_pages/administration/edit_page_content.html', {
        'page': page,
        'content': content,
        'content_form': content_form,
        'library': library

    })


def page_up(request, code, id):
    library = get_object_or_404(Library, code=code)
    cbs = get_cbs(library)
    if not check_owning(request.user, cbs):
        return HttpResponse('У Вас нет прав на редактирование страниц в этой ЦБС')
    page = get_object_or_404(Page, id=id)
    page.up()

    if page.parent_id:
        return redirect('participants_pages:administration:pages_list', code=code, parent=page.parent_id)
    else:
        return redirect('participants_pages:administration:pages_list', code=code)


def page_down(request, code, id):
    library = get_object_or_404(Library, code=code)
    cbs = get_cbs(library)
    if not check_owning(request.user, cbs):
        return HttpResponse('У Вас нет прав на редактирование страниц в этой ЦБС')

    page = get_object_or_404(Page, id=id)
    page.down()
    if page.parent_id:
        return redirect('participants_pages:administration:pages_list', code=code, parent=page.parent_id)
    else:
        return redirect('participants_pages:administration:pages_list', code=code)



