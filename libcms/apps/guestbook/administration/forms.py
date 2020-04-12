# -*- coding: utf-8 -*-
from django import forms

from ..models import Feedback


class FeedbackForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, label='Текст отзыва')
    comment = forms.CharField(widget=forms.Textarea, label='Текст комментария')

    class Meta:
        model = Feedback
        exclude = []
