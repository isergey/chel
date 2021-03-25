# coding=utf-8

from datetime import datetime
from django import forms
from django.contrib.auth.models import Group
from .. import models

RANGE_DATE_FORMAT = '%d.%m.%Y'


class GroupForm(forms.ModelForm):
    class Meta:
        model = models.Group
        exclude = []


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = models.Subscribe
        exclude = []


class LetterForm(forms.ModelForm):
    class Meta:
        model = models.Letter
        exclude = []


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = models.Subscriber
        exclude = []


# RANGE_GROUP_CHOICES = (
#     ('D', u'день'),
#     ('M', u'месяц'),
#     ('Y', u'год')
# )


def get_date_range_form(init_start_date, init_end_date):
    class DateRangeForm(forms.Form):
        start_date = forms.DateTimeField(
            label='начало',
            initial=init_start_date,
            widget=forms.DateInput,
            input_formats=[RANGE_DATE_FORMAT]
        )
        end_date = forms.DateTimeField(
            label='окончание',
            required=False,
            initial=init_end_date,
            widget=forms.DateInput,
            input_formats=[RANGE_DATE_FORMAT]
        )
        user_group = forms.ModelChoiceField(
            label='Группа пользователя',
            queryset=Group.objects.all(),
            required=False,
            widget=forms.Select(attrs={'class': "form-control input-sm"}),
        )

        def clean_start_date(self):
            start_date = self.cleaned_data['start_date']
            now = datetime.now()
            if start_date > now:
                raise forms.ValidationError('Дата начала периода больше текущей даты %s' % (now.strftime(RANGE_DATE_FORMAT),))
            return start_date

        def clean_end_date(self):
            end_date = self.cleaned_data['end_date']
            now = datetime.now()
            if end_date and end_date > now:
                raise forms.ValidationError('Дата окончания периода больше текущей даты %s' % (now.strftime(RANGE_DATE_FORMAT),))
            return end_date

        def clean(self):
            start_date = self.cleaned_data.get('start_date')
            end_date = self.cleaned_data.get('end_date')

            if start_date and end_date and end_date < start_date:
                raise forms.ValidationError('Дата окончания периода должна быть больше даты начала')

    return DateRangeForm