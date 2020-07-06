from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Input a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', )


class VerifierTokenForm(forms.Form):
    verifier_code = forms.CharField(label='Enter Your Verifier code:', max_length=100)

class UserSettingsForm(forms.Form):
    auto_manager = forms.BooleanField()