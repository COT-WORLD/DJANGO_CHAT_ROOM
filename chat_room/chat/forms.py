from django.forms import ModelForm
from .models import Room, User
from django import forms
from allauth.account.forms import SignupForm, LoginForm
from django.core.exceptions import ValidationError
import bleach


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

    def clean_description(self):
        description = self.cleaned_data.get('description', '')

        allowed_tags = ['p', 'b', 'i', 'ul', 'ol', 'li', 'a', 'strong', 'em']
        allowed_attrs = {'a': ['href', 'title', 'rel']}

        sanitized_description = bleach.clean(
            description, tags=allowed_tags, attributes=allowed_attrs)

        return sanitized_description


class UserForm(ModelForm):
    avatar = forms.FileField(required=False)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "bio", "avatar",]

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if not avatar:
            return avatar

        max_size = 2 * 1024 * 1024
        if avatar.size > max_size:
            raise ValidationError("Avatar file size must be under 2MB.")

        valid_mime_types = ['image/jpeg', 'image/png', 'image/webp']
        if avatar.content_type not in valid_mime_types:
            raise ValidationError("Only JPG, PNG, or WebP files are allowed.")

        return avatar

    def clean_bio(self):
        bio = self.cleaned_data.get("bio", "")
        return bleach.clean(bio, tags=["p", "b", "i", "ul", "li", "a"], attributes={"a": ["href", "rel"]})
