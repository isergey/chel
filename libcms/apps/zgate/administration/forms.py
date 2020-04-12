# -*- coding: utf-8 -*-
import datetime

from django import forms
from django.contrib.admin import widgets
from common.forms import CoolForm
from ..models import ZCatalog
from ..models import get_search_attributes_in_log

#
# from common.access.choices import get_groups_choices
# from common.access.shortcuts import  check_perm_for_model
#
#
#
# class ZCatalogForm(forms.ModelForm):
#
#     view_catalog_groups = forms.MultipleChoiceField(choices=get_groups_choices(),
#                                        label=u"Группы пользователей, имеющие доступ к каталогу",
#                                        widget=forms.CheckboxSelectMultiple)
#
#     def clean_view_page_groups(self):
#         groups = self.cleaned_data['view_catalog_groups']
#         if check_perm_for_model('view_zcatalog', ZCatalog):
#             return groups
#
#         raise forms.ValidationError(u'Model ZCatalog not have "view_zcatalog" perm')
#     class Meta:
#         model = ZCatalog
#
#
#     def __init__(self, *args, **kwargs):
#         super(ZCatalogForm, self).__init__(*args, **kwargs)
#         self.fields['title'].widget = forms.TextInput(attrs={'class':'text span-18'})
#         self.fields['description'].widget = forms.Textarea(attrs={'class':'text span-18'})
#         self.fields['help'].widget = forms.Textarea(attrs={'class':'text span-18'})
#         self.fields['url'].widget = forms.TextInput(attrs={'class':'text span-18'})
#         self.fields['xml'].widget = forms.TextInput(attrs={'class':'text span-18'})
#         self.fields['xsl'].widget = forms.TextInput(attrs={'class':'text span-18'})



GROUP_CHOICES = (
    ('2', 'По дням'),
    ('1', 'По месяцам'),
    ('0', 'По годам'),
)




class PeriodForm(CoolForm):
    start_date = forms.DateTimeField(
        label='Дата начала периода',widget=widgets.AdminDateWidget,
        initial=datetime.datetime.now()
    )

    end_date = forms.DateTimeField(
        label='Дата конца периода',widget=widgets.AdminDateWidget,
        initial=datetime.datetime.now()
    )



class GroupForm(CoolForm):
    group = forms.ChoiceField(label='Группировка', choices=GROUP_CHOICES, initial=2)



class AttributesForm(CoolForm):
    attributes = forms.MultipleChoiceField(
        label='Отображаемые атрибуты',
        choices=get_search_attributes_in_log(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )

class ZCatalogForm(CoolForm):
    catalogs = forms.ModelMultipleChoiceField(
        label='Каталоги',
        queryset=ZCatalog.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
        required=False
    )