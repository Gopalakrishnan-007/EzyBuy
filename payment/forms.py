from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name','last_name', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
        }
    def clean(self):
        pw = str(self.cleaned_data.get('password1'))
        special_char = '!@#$%^&*()?'
        num = '1234567890'
        fs=0
        fn=0
        for i in pw:
            if i in special_char:
                fs=1
            if i in num:
                fn=1
        if not fs:
            raise ValidationError("Password must contain atleast one special character")
        if not fn:
            raise ValidationError("Password must contain atleast one number")
        
        
