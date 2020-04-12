# -*- encoding: utf-8 -*-
from django import forms
from datetime import date


DAY_CHOISE = (
    ('1', 'За один день'),
    ('3', 'За три дня'),
    ('5', 'За пять дней'),
    )

REMEMBER_SYSTEMS_CHOISE = (
    ('0', 'email'),
    #(u'1', u'sms'),
    )
class CommentEventForm(forms.Form):
    text = forms.CharField(min_length=6, max_length=255,
        label="Текст комментария", widget=forms.Textarea)

class AddToFavoriteForm(forms.Form):
    days_for_remember = forms.MultipleChoiceField(choices=DAY_CHOISE,
        widget=forms.CheckboxSelectMultiple(),
        label="Напомнить")
    remember_system = forms.ChoiceField(choices=REMEMBER_SYSTEMS_CHOISE, initial='0',
        label="Выслать напоминания по")


def get_years_choice():
    year = date.today().year
    choices = []
    for i, y in enumerate(range(year - 1, year + 2)):
        choices.append((y,y))
    return choices


def get_current_year_choice():
    year = date.today().year
    return year

MONTH_CHOICES = (
    ('1', "Январь"),
    ('2', "Февраль"),
    ('3', "Март"),
    ('4', "Апрель"),
    ('5', "Май"),
    ('6', "Июнь"),
    ('7', "Июль"),
    ('8', "Август"),
    ('9', "Сентябрь"),
    ('10', "Октябрь"),
    ('11', "Ноябрь"),
    ('12', "Декабрь"),
    )

def get_current_month_choice():
    month = date.today().month
    return month


class CalendarFilterForm(forms.Form):
    month = forms.ChoiceField(choices=MONTH_CHOICES,
        label="Месяц",
        widget=forms.Select(attrs={'onchange':'this.form.submit();'}))
    year = forms.ChoiceField(choices=get_years_choice(),
        label="Год",
        widget=forms.Select(attrs={'onchange':'this.form.submit();'}))
    #Возвращаем список из предыдущего текущего и следующего года