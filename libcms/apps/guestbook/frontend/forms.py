# -*- coding: utf-8 -*-
from django import forms
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3
from ..models import Feedback


class FeedbackForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, label='Текст отзыва')
    captcha = ReCaptchaField(label='', widget=ReCaptchaV3(
        attrs={
            'required_score': 0.85,
        }
    ))
    # captcha = CaptchaField(label=u'Введите текст изображенный на картинке')
    class Meta:
        model = Feedback
        exclude = ('comment', 'publicated')
