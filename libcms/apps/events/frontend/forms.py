# -*- encoding: utf-8 -*-
from django import forms
from datetime import date
from .. import models


class EventsFilterForm(forms.Form):
    # library = forms.ModelChoiceField(
    #     empty_label=u'выберите из списка',
    #     label=u'Укажите библиотеку',
    #     queryset=Library.objects.filter(parent=None), required=False, widget=forms.Select)

    keywords = forms.CharField(
        required=False,
        label='Ключевые слова',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )

    start_date = forms.DateField(
        label='Дата начала',
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )

    end_date = forms.DateField(
        label='Дата окончания',
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        )
    )

    category = forms.ModelMultipleChoiceField(
        label=u'Категория события',
        queryset=models.Category.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    age_category = forms.ModelChoiceField(
        label=u'Возрастная категория',
        queryset=models.AgeCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    address = forms.ModelChoiceField(
        label=u'Место проведения',
        queryset=models.Address.objects.all(),
        required=False,
    )


class ParticipantForm(forms.Form):
    last_name = forms.CharField(
        label='Фамилия',
        max_length=256
    )

    first_name = forms.CharField(
        label='Имя Отчество',
        max_length=256
    )

    reader_id = forms.CharField(
        label='№ читательского билета',
        max_length=256
    )

    email = forms.EmailField(
        label='Email',
        max_length=256
    )



DAY_CHOISE = (
    ('1', 'За один день'),
    ('3', 'За три дня'),
    ('5', 'За пять дней'),
)

REMEMBER_SYSTEMS_CHOISE = (
    ('0', 'email'),
    # (u'1', u'sms'),
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
        choices.append((y, y))
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
                              widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))
    year = forms.ChoiceField(choices=get_years_choice(),
                             label="Год",
                             widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))
    # Возвращаем список из предыдущего текущего и следующего года
