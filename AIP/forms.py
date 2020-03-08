from django.db import models

from django import forms
from .models import Answer

class TakeQuizForm(forms.ModelForm):
    class Meta:
        model = Answer
        labels = {
            'question': 'Question Topic'
        }
        fields = '__all__'
