# -*- encoding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from captcha.fields import ReCaptchaField

class RegistrationForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = User


class RegistrationForm(forms.Form):
    username = forms.CharField(max_length=50, label="Логин", help_text="Разрешены буквы латинского алфавита и цифры")
    password = forms.CharField(min_length=6, max_length=50,
                               label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(min_length=6, max_length=50,
                                label="Повторите пароль", widget=forms.PasswordInput)
    email = forms.EmailField(label="Электронная почта")
    first_name = forms.CharField(max_length=50, label="Имя")
    last_name = forms.CharField(max_length=50, label="Фамилия")
    agree = forms.BooleanField(label="Согласен на обработку персональных данных")
    captcha = ReCaptchaField(label='Введите текст на картинке')
    def clean_username(self):
        import re

        format = re.compile(r"^[a-zA-z0-9]+$")
        if re.match(format, self.cleaned_data["username"]) == None:
            raise forms.ValidationError("Имя пользователя может содержать только латинские символы")

        username = self.cleaned_data["username"]
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise forms.ValidationError("Такой логин уже существует.")

    def clean_email(self):
        email = self.cleaned_data["email"]
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email

        raise forms.ValidationError("Такой email уже зарегистрирован.")

    def clean_password2(self):
        password = self.cleaned_data.get("password", "")
        password2 = self.cleaned_data["password2"]
        if password != password2:
            raise forms.ValidationError('пароли не совпадают')
        return password2

    def clean_agree(self):
        agree = self.cleaned_data.get("agree", False)
        if not agree:
            raise forms.ValidationError('Необходимо дать согласие на обработку персональных данных')
        return agree
