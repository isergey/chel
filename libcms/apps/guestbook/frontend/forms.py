# -*- coding: utf-8 -*-
from django import forms
from captcha.fields import CaptchaField

from ..models import Feedback


class FeedbackForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, label='Текст отзыва')
    captcha = CaptchaField(label='Введите текст с картинки')
    # captcha = CaptchaField(label=u'Введите текст изображенный на картинке')
    class Meta:
        model = Feedback
        exclude = ('comment', 'publicated')
