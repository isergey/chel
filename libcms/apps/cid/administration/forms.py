# encoding: utf-8
from django import forms
from django.contrib.admin import widgets
from ..models import Type,  ImportantDate

class TypeForm(forms.Form):
    types = forms.ModelMultipleChoiceField(
        label=u'Тип записи',
        queryset=Type.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )


#class ThemeForm(forms.ModelForm):
#    class Meta:
#        model = Theme



class ImportantDateForm(forms.ModelForm):
    type = forms.ModelMultipleChoiceField(
        queryset=Type.objects.all(),
        label=u'Тип знаменательной даты:',
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = ImportantDate


    def __init__(self, *args, **kwargs):
        super(ImportantDateForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget = widgets.AdminDateWidget()