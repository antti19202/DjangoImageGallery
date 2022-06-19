from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import *


# Käyttäjätietojen päivittämisen sivu
class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user']  # Käyttäjäniemä ei pysty muuttamaan käyttäjänimeä


# Määritellään mitä käyttäjän luonnissa kysytään
class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Määritellään mitä kuvan lataamisessta kysytään
class UploadImage(ModelForm):
    def __init__(self, current_user=None, *args, **kwargs):
        super(UploadImage, self).__init__(*args, **kwargs)
        if current_user:
            self.fields['album'].queryset = self.fields['album'].queryset.filter(user=current_user.id)

    class Meta:
        model = Photo
        # Määritellään mitä tietoja kysytään
        fields = ['user','title', 'description', 'album', 'tags', 'image']
        # Käyttäjää käyttäjä ei voi valita
        widgets = {'user': forms.HiddenInput()}


# Määritellään mitä albumin luomisessa kysytään
class CreateAlbum(ModelForm):
    class Meta:
        model = Album
        # Määritellään mitä tietoja kysytään
        fields = ['user', 'title', 'description']
        # Käyttäjää käyttäjä ei voi valita
        widgets = {'user': forms.HiddenInput()}