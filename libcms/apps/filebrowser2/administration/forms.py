# -*- coding: utf-8 -*-
import os
from django import forms
from .import app_settings
from .. import models


def get_upload_file_form(pathes):
    class UploadFileForm(forms.Form):
        file = forms.FileField(label="Выберите файл для загрузки")
        def clean_file(self):
            file = self.cleaned_data['file'].name
            upload_dir = pathes['upload_dir'].encode(app_settings.FILE_NAME_ENCODING)
            save_file_path = os.path.join(pathes['upload_dir'], file).encode(app_settings.FILE_NAME_ENCODING)

            if not os.path.isdir(upload_dir):
                raise forms.ValidationError('Попытка загрузки в несуществующую директирю')

            if os.path.exists(save_file_path):
                raise forms.ValidationError('Файл с именем %s уже существует' % (file, ))

            if not os.access(upload_dir, os.W_OK):
                raise forms.ValidationError('Файл не может быть сохранен. Обратитесь к администратору системы.')

            return file

    return UploadFileForm


def get_create_directory_form(pathes):
    class CreateDirectoryForm(forms.Form):
        name = forms.CharField(label='Название директории', max_length=255)

        def clean_name(self):
            name = self.cleaned_data['name']
            create_dir_path = os.path.join(pathes['upload_dir'], name).encode(app_settings.FILE_NAME_ENCODING)
            if os.path.exists(create_dir_path):
                raise forms.ValidationError('Элемент с именем %s уже существует' % (name, ))

            if not os.access(pathes['upload_dir'].encode(app_settings.FILE_NAME_ENCODING), os.W_OK):
                raise forms.ValidationError('Файл не может быть сохранен. Обратитесь к администратору системы.')

            return name
    return CreateDirectoryForm


class FileForm(forms.ModelForm):
    class Meta:
        model = models.File
        exclude = []