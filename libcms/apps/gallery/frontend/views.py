# -*- encoding: utf-8 -*-
from django.shortcuts import HttpResponse, render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from guardian.decorators import permission_required_or_403

from ..models import Album, AlbumImage



def index(request):
    albums = Album.objects.all()

    return render(request, 'gallery/frontend/albums_list.html', {
        'albums': albums
    })


def album_view(request, id):
    if not request.user.has_module_perms('gallery'):
        return HttpResponseForbidden()

    album = get_object_or_404(Album, id=id)
    album_images = AlbumImage.objects.filter(album=album)

    return render(request, 'gallery/frontend/album_view.html', {
        'album': album,
        'album_images': album_images,
    })

