from django import forms


class DateRangeForm(forms.Form):
    start_date = forms.DateField(required=False)
    end_date = forms.DateField(required=False)
