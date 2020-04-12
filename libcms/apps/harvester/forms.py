# coding=utf-8
from django import forms
from . import models

POSITION_TYPE_CHOICES = (
    ('index', 'Порядковый номер'),
    ('offset', 'Позиция в файле'),
)

VIEW_CHOICES = (
    ('html', 'HTML'),
    ('text', 'Текст')
)


class SourceForm(forms.ModelForm):
    class Meta:
        model = models.Source
        exclude = []


class SourceFileForm(forms.ModelForm):
    class Meta:
        model = models.SourceRecordsFile
        exclude = ['source']


class IndexTransformationRuleForm(forms.ModelForm):
    class Meta:
        model = models.IndexTransformationRule
        exclude = []

    def clean_content(self):
        content = self.cleaned_data['content'].strip()
        try:
            compile(content.strip(), 'content', 'exec')
        except SyntaxError as e:
            raise forms.ValidationError(str(e))
        return content


class HarvestingRuleForm(forms.ModelForm):
    class Meta:
        model = models.HarvestingRule
        exclude = ['source']


class IndexingRuleForm(forms.ModelForm):
    class Meta:
        model = models.IndexingRule
        exclude = ['source']
