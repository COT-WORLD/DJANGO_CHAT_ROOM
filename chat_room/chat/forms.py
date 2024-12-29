from django.forms import ModelForm
from .models import Room, User
from django import forms
from allauth.account.forms import SignupForm, LoginForm


class MyCustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='First Name', required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'Firstname'}))
    last_name = forms.CharField(max_length=30, label='Last Name', required=True,
                                widget=forms.TextInput(attrs={'placeholder': 'Lastname'}))

    def save(self, request):
        user = super(MyCustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


class MyCustomLoginForm(LoginForm):
    def login(self, *args, **kwargs):
        return super(MyCustomLoginForm, self).login(*args, **kwargs)


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = "__all__"
        exclude = ['host', 'participants']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "bio", "avatar",]
