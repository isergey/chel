# -*- encoding: utf-8 -*-

from django import forms
from ..models import Question, Category, Recomendation
from mptt.forms import TreeNodeChoiceField
from django.forms.extras import widgets


class QuestionForm(forms.ModelForm):
    category = TreeNodeChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label=u"Тематика",
        help_text=u'Выберите тему, к которой относиться задаваемый вопрос. Если подходящей темы нет, оставьте поле темы пустым.'
    )
    class Meta:
        model = Question
        exclude = ('user', 'answer', 'status', 'create_date', 'manager', 'start_process_date', 'end_process_date')


class RecomendationForm(forms.ModelForm):
    class Meta:
        model = Recomendation
        exclude = ('user', 'question', 'public', 'create_date')


class DateFilterForm(forms.Form):
    date = forms.DateField(label=u'', help_text=u'формат даты: дд.мм.гггг')