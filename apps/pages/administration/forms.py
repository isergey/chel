# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group

from pages.models import Page, Translate

class PageForm(forms.ModelForm):
    class Meta:
        model=Page

class TranslateForm(forms.ModelForm):
    class Meta:
        model=Translate