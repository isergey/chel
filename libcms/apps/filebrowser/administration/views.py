# -*- coding: utf-8 -*-
import os
import datetime
import shutil
from hashlib import md5
from django.http import HttpResponseForbidden
from django.shortcuts import HttpResponse, Http404, render, redirect, reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from guardian.decorators import permission_required_or_403
from django.contrib.contenttypes.models import ContentType

from .forms import get_upload_file_form, get_create_directory_form, FileForm
from . import app_settings
from .. import models

mtypes = {
    'gif': 'image',
    'jpg': 'image',
    'png': 'image',
    'pdf': 'pdf',
    'doc': 'doc',
    'xls': 'xsl',
}


def chek_or_create_dir(path):
    if not os.path.isdir(path):
        try:
            os.makedirs(path, 0o755)
        except Exception as e:
            return False

    return True


def get_mtype(file_name):
    file_name_ext = file_name.split('.')

    if len(file_name_ext) > 1 and file_name_ext[1] in mtypes:
        return mtypes[file_name_ext[1]]

    return 'file'


def get_file_map(path, upload_to, current_path):

    file_name = os.path.basename(path)
    item_map = {}

    item_map['type'] = 'file'
    item_map['mtype'] = get_mtype(file_name)
    item_map['name'] = file_name

    full_path_hash = models.File.generate_full_path_hash(current_path, file_name)
    item_map['full_path_hash'] = full_path_hash

    file_stat = os.stat(path.encode(app_settings.FILE_NAME_ENCODING))
    size = file_stat.st_size / 1024
    if size < 1:
        item_map['size'] = {
            'bytes': file_stat.st_size,
            'title': 'bytes'
        }
    else:
        item_map['size'] = {
            'bytes': size,
            'title': 'Kbytes'
        }

    item_map['create_time'] = datetime.datetime.fromtimestamp(file_stat.st_ctime)
    item_map['url'] = app_settings.MEDIA_URL + upload_to + '/' + current_path + '/' + file_name
    item_map['related_path'] = current_path + '/' + file_name

    return item_map


def get_dir_map(path, current_dir):
    dir_name = os.path.basename(path.encode(app_settings.FILE_NAME_ENCODING)).decode(app_settings.FILE_NAME_ENCODING)
    item_map = {}

    item_map['type'] = 'dir'
    item_map['mtype'] = 'dir'
    item_map['name'] = dir_name

    dir_stat = os.stat(path.encode(app_settings.FILE_NAME_ENCODING))

    item_map['size'] = {
        'bytes': 0,
        'title': 'bytes'
    }

    item_map['create_time'] = datetime.datetime.fromtimestamp(dir_stat.st_ctime)
    item_map['url'] = current_dir + '/' + dir_name + '/'
    return item_map


def handle_uploaded_file(f, path):
    destination = open(os.path.join(path,f.name).encode(app_settings.FILE_NAME_ENCODING), 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


def _is_correct_path(path):
    wrong_elements = ['..', './', '.\\']
    for wrong_element in wrong_elements:
        if wrong_element in path:
            return False
    return True


def _get_init_pathes(request):
    base_dir = os.path.join(app_settings.MEDIA_ROOT, app_settings.UPLOAD_TO)
    current_dir = request.GET.get('path', '').strip('/').strip('\\')

    upload_dir = os.path.join(base_dir, current_dir)

    if not _is_correct_path(current_dir):
        raise Http404("Некорректный путь")

    if not os.path.isdir(upload_dir.encode(app_settings.FILE_NAME_ENCODING)):
        raise Http404("Путь не является директорией")

    return {
        'base_dir': base_dir,
        'current_dir': current_dir,
        'upload_dir': upload_dir
    }


def _make_breadcrumbs(pathes):
    breadcrumbs = []
    path_dirs = pathes['current_dir'].strip('/').strip('\\').split('/')

    for i, path_dir in enumerate(path_dirs):
        breadcrumbs.append({
            'title': path_dir,
            'url': '/' + '/'.join(path_dirs[:i + 1]),
        })
    return breadcrumbs


@login_required
def index(request):
    if not request.user.has_module_perms('filebrowser'):
        return HttpResponseForbidden('У вас нет права для доступа')

    pathes = _get_init_pathes(request)

    current_dir_items = [x.decode(app_settings.FILE_NAME_ENCODING) for x in os.listdir(pathes['upload_dir'].encode(app_settings.FILE_NAME_ENCODING))]
    CreateDirectory = get_create_directory_form(pathes)

    files = []
    dirs = []

    if request.method == 'POST':
        create_dir_form = CreateDirectory(request.POST, prefix='cdf')
        if create_dir_form.is_valid():
            create_dir_path = os.path.join(pathes['upload_dir'], create_dir_form.cleaned_data['name']).encode(app_settings.FILE_NAME_ENCODING)
            os.mkdir(create_dir_path)
            dir = '%s/%s' % (pathes.get('current_dir', ''), create_dir_form.cleaned_data['name'])
            # journal_models.log_action(
            #     'filebrowser',
            #     'create_dir',
            #     user_id=request.user.id,
            #     content_id=md5(dir.encode('utf-8')).hexdigest(),
            #     message=dir
            # )
            return redirect(reverse('filebrowser:administration:index') + '?path=' + pathes['current_dir'])
    else:
        create_dir_form = CreateDirectory(prefix='cdf')


        for current_dir_item in current_dir_items:
            current_dir_item_path = os.path.join(pathes['upload_dir'], current_dir_item)
            if os.path.isfile(current_dir_item_path.encode(app_settings.FILE_NAME_ENCODING)):
                files.append(get_file_map(current_dir_item_path, app_settings.UPLOAD_TO, pathes['current_dir']))

            elif os.path.isdir(current_dir_item_path.encode(app_settings.FILE_NAME_ENCODING)):
                dirs.append(get_dir_map(current_dir_item_path, pathes['current_dir']))


        full_path_hashes = []
        for file_item in files:
            full_path_hashes.append(file_item.get('full_path_hash', ''))

        file_models = models.File.objects.filter(full_path_hash__in=full_path_hashes)

        file_models_index= {}

        for file_model in file_models:
            file_models_index[file_model.full_path_hash] = file_model

        for file_item in files:
            file_model = file_models_index.get(file_item.get('full_path_hash', ''), None)
            if file_model:
                file_item['model'] = file_model

    dir_map = sorted(dirs, key=lambda x: x['create_time'], reverse=True) +\
              sorted(files, key=lambda x: x['create_time'], reverse=True)

    breadcrumbs = _make_breadcrumbs(pathes)

    return render(request, 'filebrowser/administration/list.html', {
        'dir_map': dir_map,
        'breadcrumbs': breadcrumbs,
        'create_dir_form': create_dir_form
    })



@login_required
@permission_required_or_403('filebrowser.add_file')
@transaction.atomic()
def upload_file(request):
    pathes = _get_init_pathes(request)
    UploadFileForm = get_upload_file_form(pathes)

    if request.method == 'POST':
        file_info_form = FileForm(request.POST, prefix='fif')
        upload_form = UploadFileForm(request.POST, request.FILES)
        if upload_form.is_valid() and file_info_form.is_valid():
            handle_uploaded_file(f=request.FILES['file'], path=pathes['upload_dir'])
            file_model = file_info_form.save(commit=False)
            file_model.path = pathes['current_dir']
            file_model.name = str(upload_form.cleaned_data['file'])
            try:
                exist_file_model = models.File.objects.get(full_path_hash=file_model.full_path_hash)
                exist_file_model.delete()
            except models.File.DoesNotExist:
                pass
            file_model.save()
            content_type = ContentType.objects.get_for_model(models.File)
            # journal_models.log_action(
            #     'filebrowser',
            #     'upload_file',
            #     user_id=request.user.id,
            #     content_type=content_type,
            #     content_id=file_model.full_path_hash,
            #     message='%s/%s' %(file_model.path, file_model.name)
            # )
            return redirect(reverse('filebrowser:administration:index') + '?path=' + pathes['current_dir'])
    else:
        upload_form = UploadFileForm(initial={'path': pathes['current_dir']})
        file_info_form = FileForm(prefix='fif')

    breadcrumbs = _make_breadcrumbs(pathes)

    return render(request, 'filebrowser/administration/upload_file.html', {
        'form': upload_form,
        'breadcrumbs': breadcrumbs,
        'file_info_form': file_info_form
    })



@login_required
@permission_required_or_403('filebrowser.delete_file')
@transaction.atomic()
def delete(request):
    name = request.GET.get('name').replace('..', '').replace('/', '').replace('\\', '')
    pathes = _get_init_pathes(request)

    item_path = os.path.join(pathes['upload_dir'], name).encode(app_settings.FILE_NAME_ENCODING)
    if os.path.isfile(item_path):
        os.remove(item_path)
    elif os.path.isdir(item_path):
        shutil.rmtree(item_path)

    full_path_hash = models.File.generate_full_path_hash(pathes['current_dir'], name)
    try:
        file_model = models.File.objects.get(full_path_hash=full_path_hash)
        file_model.delete()
        content_type = ContentType.objects.get_for_model(models.File)
        # journal_models.log_action(
        #     'filebrowser',
        #     'delete_file',
        #     user_id=request.user.id,
        #     content_type=content_type,
        #     content_id=file_model.full_path_hash,
        #     message='%s/%s' %(file_model.path, file_model.name)
        # )
    except models.File.DoesNotExist:
        pass

    return redirect(reverse('filebrowser:administration:index') + '?path=' + pathes['current_dir'])


def ajax_file_info(request):
    hash = request.GET.get('hash', '')

    try:
        file_info = models.File.objects.get(full_path_hash=hash)
    except models.File.DoesNotExist:
        return HttpResponse('Описание файла не найдено')

    return render(request, 'filebrowser/administration/ajax_file_info.html', {
        'file_info': file_info
    });
