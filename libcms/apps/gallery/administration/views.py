# -*- encoding: utf-8 -*-
from django.db import transaction
from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from guardian.decorators import permission_required_or_403
from django.contrib.auth.decorators import login_required
from ..models import Album, AlbumImage
from forms import AlbumForm, AlbumImageForm, AlbumImageEditForm
from django.views.decorators.csrf import csrf_exempt

def index(request):
    if not request.user.has_module_perms('gallery'):
        return HttpResponseForbidden()
    return render(request, 'gallery/administration/index.html')

@login_required
def albums_list(request):
    albums = Album.objects.all()

    return render(request, 'gallery/administration/albums_list.html', {
        'albums': albums
    })

@login_required
@permission_required_or_403('gallery.add_album')
def album_create(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            if not request.user.has_perm('gallery.public_album'):
                album.public = False
            album.save()
            return redirect('gallery:administration:albums_list')
    else:
        form = AlbumForm()

    return render(request, 'gallery/administration/album_create.html', {
        'form': form
    })

@login_required
@permission_required_or_403('gallery.change_album')
def album_edit(request, id):
    album = get_object_or_404(Album, id=id)
    if request.method == 'POST':
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            album = form.save(commit=False)
            if not request.user.has_perm('gallery.public_album'):
                album.public = False
            album.save()
            return redirect('gallery:administration:albums_list')
    else:
        form = AlbumForm(instance=album)

    return render(request, 'gallery/administration/album_edit.html', {
        'form': form
    })

@login_required
@permission_required_or_403('gallery.delete_album')
def album_delete(request, id):
    album = get_object_or_404(Album, id=id)
    album.delete()
    return redirect('gallery:administration:albums_list')


def album_view(request, id):
    if not request.user.has_module_perms('gallery'):
        return HttpResponseForbidden()

    album = get_object_or_404(Album, id=id)
    album_images = AlbumImage.objects.filter(album=album)

    return render(request, 'gallery/administration/album_view.html', {
        'album': album,
        'album_images': album_images,
    })




@transaction.commit_on_success
@csrf_exempt
def album_upload(request, id):

    if request.user.is_authenticated():
        user = request.user
    elif request.method == 'POST':
        user = user_from_session_key(request.POST.get('sessionid', 0))

    if not user.is_authenticated():
        return HttpResponseForbidden()

    if not user.has_perm('gallery.add_album'):
        return HttpResponseForbidden()

    album = get_object_or_404(Album, id=id)
    if request.method == 'POST':
        form = AlbumImageForm(request.POST, request.FILES)
        if form.is_valid():
            album_image = form.save(commit=False)
            album_image.album = album
            album_image.save()
            return HttpResponse('True')
    else:
        form = AlbumImageForm()
    return render(request, 'gallery/administration/album_upload.html', {
        'album': album,
        'form': form,
        })

@login_required
@permission_required_or_403('gallery.change_album')
@transaction.commit_on_success
def image_edit(request, id):
    album_image = get_object_or_404(AlbumImage, id=id)
    if request.method == 'POST':
        form = AlbumImageEditForm(request.POST, instance=album_image)
        if form.is_valid():
            form.save()
            return redirect('gallery:administration:album_view', id=album_image.album_id)
    else:
        form = AlbumImageEditForm(instance=album_image)

    return render(request, 'gallery/administration/image_edit.html', {
        'form': form,
        'album_image': album_image
    })



@login_required
@permission_required_or_403('gallery.delete_album')
@transaction.commit_on_success
def image_delete(request, id):
    image = get_object_or_404(AlbumImage, id=id)
    image.delete()
    return redirect('gallery:administration:album_view', id=image.album_id)



from django.conf import settings
from django.contrib.auth import SESSION_KEY, BACKEND_SESSION_KEY, load_backend
from django.contrib.auth.models import AnonymousUser

def user_from_session_key(session_key):


    session_engine = __import__(settings.SESSION_ENGINE, {}, {}, [''])
    session_wrapper = session_engine.SessionStore(session_key)
    session = session_wrapper.load()
    user_id = session.get(SESSION_KEY)
    backend_id = session.get(BACKEND_SESSION_KEY)
    if user_id and backend_id:
        auth_backend = load_backend(backend_id)
        user = auth_backend.get_user(user_id)
        if user:
            return user
    return AnonymousUser()