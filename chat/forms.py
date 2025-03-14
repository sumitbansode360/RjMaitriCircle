from django.forms import ModelForm
from django import forms
from chat.models import GroupMessage

class ChatMessageCreateForm(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']

        widgets = {
            'body': forms.TextInput(attrs={
                'placeholder': 'Type your message...',
                'class': 'form-control msg-chat-input',
                'maxlength': '3000'
            }),
        }
