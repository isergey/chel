# -*- encoding: utf-8 -*-
from django import forms

from ..models import Album, AlbumImage

class AlbumForm(forms.ModelForm):
    class Meta:
        model=Album


class AlbumImageForm(forms.ModelForm):
    class Meta:
        model=AlbumImage
        exclude=('album','comments')


class AlbumImageEditForm(forms.ModelForm):
    comments = forms.CharField(label=u'Коментарии к изображению', widget=forms.Textarea, required=False)
    class Meta:
        model=AlbumImage
        exclude=('album','image')