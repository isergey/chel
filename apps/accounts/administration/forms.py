# -*- coding: utf-8 -*-
from django import forms
from common.forms import CoolModelForm
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    class Meta:
        model=User
        exclude = ['password', 'is_staff', 'last_login', 'date_joined']