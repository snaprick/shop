from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Product


class ProductForm(forms.ModelForm):
    def clean_price(self):
        value = self.cleaned_data['price']
        if value < 0:
            raise ValidationError("Not valid")

        return value

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock']


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
