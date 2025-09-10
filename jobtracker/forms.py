from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.conf import settings
from datetime import date

from .models import JobApplication


class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = ['company', 'position', 'status', 'applied_date', 'notes', 'resume']
        widgets = {
            'applied_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # remove file field if running in demo mode
        if getattr(settings, "DEMO_MODE", False):
            self.fields.pop("resume", None)

        # add max= today’s date to applied_date
        self.fields['applied_date'].widget.attrs['max'] = date.today().isoformat()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

