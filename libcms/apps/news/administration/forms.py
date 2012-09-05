# -*- coding: utf-8 -*-
from django import forms

from ..models import NewsContent, News

class NewsForm(forms.ModelForm):
    class Meta:
        model=News
        exclude = ('avatar_img_name',)

class NewsContentForm(forms.ModelForm):
    class Meta:
        model=NewsContent
        exclude = ('news', 'lang')



