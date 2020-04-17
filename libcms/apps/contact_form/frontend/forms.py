from django import forms
from .. import models
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV3


class ContactRequestForm(forms.ModelForm):
    captcha = ReCaptchaField(label='', widget=ReCaptchaV3)

    class Meta:
        model = models.ContactRequest
        fields = ['name', 'email', 'phone', 'message']
