# -*- coding: utf-8 -*-
from django.conf import settings
from django import forms


from ..models import Category, CategoryTitle



class CategoryForm(forms.ModelForm):
    class Meta:
        model=Category
        exclude = ('parent')



class CategoryTitleForm(forms.ModelForm):
    class Meta:
        model=CategoryTitle
        exclude = ('category', 'lang')



