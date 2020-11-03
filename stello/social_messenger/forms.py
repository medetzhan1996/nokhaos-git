from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('lead', 'message')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.fromMe = True
        if commit:
            instance.save()
        return instance
