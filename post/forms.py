from django.forms import ModelForm
from post.models import Post
from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget



class NewPostModelForm(ModelForm):
    image = forms.FileField(required=True)
    caption =  forms.CharField(
        widget=CKEditor5Widget(
            attrs={"class": "django_ckeditor_5"},
            config_name="extends"
        )
    )
    tag = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Seprated with comma", 'name':"tag"}))

    class Meta:
        model = Post
        fields = ['image', 'caption', 'tag']
