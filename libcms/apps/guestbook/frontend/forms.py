# -*- coding: utf-8 -*-
from django import forms
from captcha.fields import ReCaptchaField

from ..models import Feedback


class FeedbackForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, label='Текст отзыва')
    captcha = ReCaptchaField(label='Введите текст с картинки')
    # captcha = CaptchaField(label=u'Введите текст изображенный на картинке')
    class Meta:
        model = Feedback
        exclude = ('comment', 'publicated')
