from django.conf import settings
from django import forms


class LanguageForm(forms.Form):
    lang = forms.ChoiceField(choices=settings.LANGUAGES, label=u"language")

