from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
from django.forms import PasswordInput, EmailInput

from members.models import User


class RegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your unique nickname'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your first name'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your last name'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Confirm your password'
        })
        self.fields['gender'].widget.attrs.update({
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your gender'
        })
        self.fields['birthday'].widget.attrs.update({
            'class': 'form-control datepicker',
            'placeholder': 'Enter your birthday date',
            'type': 'text'
        })

    username = forms.CharField(min_length=1, max_length=100)
    first_name = forms.CharField(min_length=1, max_length=100)
    last_name = forms.CharField(min_length=1, max_length=100)
    password1 = forms.CharField(widget=PasswordInput)
    password2 = forms.CharField(widget=PasswordInput)
    email = forms.CharField(validators=[validators.EmailValidator(message="Invalid Email")])
    gender = forms.CharField(min_length=1, max_length=20)
    birthday = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")

        return password2

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'password1', 'password2', 'email', 'gender', 'birthday')
