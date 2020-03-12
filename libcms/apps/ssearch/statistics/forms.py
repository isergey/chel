# coding=utf-8
from django import forms


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label=u'Начало периода',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label=u'Конец периода',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
