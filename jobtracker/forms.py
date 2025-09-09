from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import JobApplication
from datetime import date

from django.conf import settings  
class JobApplicationForm(forms.ModelForm):
    class Meta:
     #DEMO STUFF=======================
     def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # remove file field in disposable demo
        if getattr(settings, "DEMO_MODE", False):
            self.fields.pop("resume", None)
            #==========================
        model = JobApplication
        fields = ['company', 'position', 'status', 'applied_date', 'notes', 'resume']
        widgets = {
            'applied_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['applied_date'].widget.attrs['max'] = date.today().isoformat()


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']



