# coding=utf-8
from django import forms
from ..models import DETAIL_ACTIONS_CHOICES, DETAIL_ACTIONS_REFERENCE


class DateRangeForm(forms.Form):
    start_date = forms.DateField(
        label='Начало периода',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        label='Конец периода',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def clean(self):
        start_date = self.cleaned_data.get('start_date')
        end_date = self.cleaned_data.get('end_date')
        if start_date and end_date:
            if start_date > end_date:
                forms.ValidationError('Дата начала должна быть меньше даты окончания периода')

class ActionFrom(forms.Form):
    ACTION_CHOICES = [
        (DETAIL_ACTIONS_REFERENCE['VIEW_DETAIL']['code'], DETAIL_ACTIONS_REFERENCE['VIEW_DETAIL']['title']),
        (DETAIL_ACTIONS_REFERENCE['VIEW_FULL_TEXT']['code'], DETAIL_ACTIONS_REFERENCE['VIEW_FULL_TEXT']['title']),
        (DETAIL_ACTIONS_REFERENCE['SOCIAL_SHARE']['code'], DETAIL_ACTIONS_REFERENCE['SOCIAL_SHARE']['title']),
    ]
    action = forms.ChoiceField(
        label='Действие',
        choices=ACTION_CHOICES,
        initial=DETAIL_ACTIONS_REFERENCE['VIEW_DETAIL']['code'],
        required=False
    )
