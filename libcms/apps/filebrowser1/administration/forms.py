# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django import forms
import os
class UploadFileForm(forms.Form):
    file  = forms.FileField(label="Выберите файл для загрузки")
    path = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_path(self):
        path = self.cleaned_data['path'].strip('/')
        if path == '': return '/'
        if '..' in path or '/.' in path:
            raise forms.ValidationError("Wrong path")

        path = '/%s' % path
        return path

class CreateDirectory(forms.Form):
    name = forms.CharField(label='Название директории', max_length=255)
    path = forms.CharField(widget=forms.HiddenInput, required=False)

    def clean_path(self):
        path = self.cleaned_data['path'].strip('/')
        if path == '': return '/'
        if '..' in path or '/.' in path:
            raise forms.ValidationError("Wrong path")

        path = '/%s' % path
        return path