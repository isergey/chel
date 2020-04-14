from django import forms
from .. import models


class ContactRequestForm(forms.ModelForm):
    class Meta:
        model = models.ContactRequest
        fields = ['name', 'email', 'phone', 'message']