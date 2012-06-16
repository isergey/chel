# -*- coding: utf-8 -*-
import random
from django.conf import settings
from django import template
from ..models import  Album, AlbumImage
register = template.Library()

@register.inclusion_tag('gallery/tags/gallery_slider.html')
def gallery_slider():
    album = None
    album_images = []
    try:
        album = Album.objects.get(slug='slider')
        album_images = AlbumImage.objects.filter(album=album)
    except Album.DoesNotExist:
        pass

    return {
        'album':album,
        'album_images': album_images,
    }

@register.inclusion_tag('gallery/tags/gallery_carusel.html')
def gallery_carusel():
    album = None
    album_images = []
    try:
        album = Album.objects.get(slug='carousel')
        album_images = AlbumImage.objects.filter(album=album)
    except Album.DoesNotExist:
        pass

    return {
        'album':album,
        'album_images': album_images,
    }