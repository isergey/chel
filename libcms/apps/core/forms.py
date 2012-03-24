from django.conf import settings
from django import forms


class LanguageForm(forms.Form):
    lang = forms.ChoiceField(choices=settings.LANGUAGES, label=u"language")

def get_permissions_form(queryset, initial=list()):
    class PermissionsForm(forms.Form):
        perms = forms.ModelMultipleChoiceField(
            initial=initial,
            queryset=queryset,
            widget=forms.CheckboxSelectMultiple,
            required=False
        )

    return PermissionsForm