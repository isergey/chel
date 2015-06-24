# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group

from participants.models import Library, LibraryType, District


def get_library_form(exclude_fields=list('parent')):
    class LibraryForm(forms.ModelForm):
        class Meta:
            model = Library
            exclude = exclude_fields

    return LibraryForm


class LibraryTypeForm(forms.ModelForm):
    class Meta:
        model = LibraryType
        exclude = []


class DistrictForm(forms.ModelForm):
    class Meta:
        model = District
        exclude = []

# from pages.models import Page, Content
#
# class PageForm(forms.ModelForm):
#    class Meta:
#        model=Page
#        exclude = ('parent',)
#
# class ContentForm(forms.ModelForm):
#    class Meta:
#        model=Content
#        exclude = ('page',)
#
#
#
# def get_content_form(exclude_list = ('page',)):
#    class ContentForm(forms.ModelForm):
#        class Meta:
#            model=Content
#            exclude = exclude_list
#    return ContentForm
