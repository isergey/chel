# encoding: utf-8
from django import forms
from django.contrib.admin import widgets
from ..models import Type, ImportantDate


class TypeForm(forms.Form):
    types = forms.ModelMultipleChoiceField(
        label=u'Тип записи',
        queryset=Type.objects.all(),
        widget=forms.CheckboxSelectMultiple()
    )


# class ThemeForm(forms.ModelForm):
#    class Meta:
#        model = Theme


class ImportantDateForm(forms.ModelForm):
    type = forms.ModelMultipleChoiceField(
        queryset=Type.objects.all(),
        label=u'Тип знаменательной даты:',
        widget=forms.CheckboxSelectMultiple()
    )

    class Meta:
        exclude = []
        model = ImportantDate

    def __init__(self, *args, **kwargs):
        super(ImportantDateForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = widgets.AdminDateWidget()


ATTRIBUTES = (
    ('all_t', u'Везде'),
    ('fio_t', u'Персоналия'),
    ('org_title_t', u'Организация'),
    ('event_title_t', u'Мероприятие'),
    ('geo_title_t', u'Географический объект'),
    ('theme_t', u'Тема'),
)


class FilterForm(forms.Form):
    type = forms.ModelChoiceField(
        label='Тип',
        queryset=Type.objects.all(),
        required=False
    )

    attribute = forms.ChoiceField(
        label='Атрибут',
        choices=ATTRIBUTES,
        required=False
    )
    value = forms.CharField(
        label='Искомый текст',
        max_length=512,
        required=False
    )
