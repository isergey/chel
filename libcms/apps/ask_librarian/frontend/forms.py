# -*- encoding: utf-8 -*-

from django import forms
from ..models import Question, Category
from mptt.forms import TreeNodeChoiceField
class QuestionForm(forms.ModelForm):
    category = TreeNodeChoiceField(queryset=Category.objects.all(), required=False, label="Тематика")
    class Meta:
        model = Question
        exclude = ('user', 'answer', 'status')