# -*- coding: utf-8 -*-
from django.conf import settings
from django import forms
from django.contrib.admin import widgets


from ..models import EventContent, Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = []

    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['start_date'].widget = widgets.AdminSplitDateTime()
        self.fields['end_date'].widget = widgets.AdminSplitDateTime()


class EventContentForm(forms.ModelForm):
    class Meta:
        model = EventContent
        exclude = ('event', 'lang')


class EventFilterForm(forms.Form):
    SORT_CHOICES = (
        (u'start_date', u'дате начала'),
        (u'end_date', u'дате окончания'),
    )

    ORDER_CHOICES = (
        (u'desc', u'обратный'),
        (u'asc', u'прямой'),
    )

    sort = forms.ChoiceField(label=u'Сортировать по', choices=SORT_CHOICES, required=False)
    order = forms.ChoiceField(label=u'Порядок', choices=ORDER_CHOICES, required=False)
    active = forms.BooleanField(label=u'Активные', required=False, initial=True)
    ended = forms.BooleanField(label=u'Звершенные',  required=False, initial=False)
    start_date = forms.DateField(label=u'C даты начала (дд.мм.гггг)', required=False)
    end_date = forms.DateField(label=u'По дате окончания (дд.мм.гггг)', required=False)