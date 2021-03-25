# encoding: utf-8
from django import forms
from .. import models


class EmailForm(forms.Form):
    email = forms.EmailField(label='Адрес e-mail', help_text='* На этот адрес будут приходить письма рассылки')

    def clean_email(self):
        return self.cleaned_data['email'].strip().lower()


def get_subscriber_form(subscribes_qs):
    class SubscriberForm(forms.Form):
        subscribes = forms.ModelMultipleChoiceField(
            queryset=subscribes_qs,
            widget=forms.CheckboxSelectMultiple,
            required=False,
            label=''
        )
    return SubscriberForm
