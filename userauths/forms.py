from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from userauths.models import Profile, STUDENT_TYPE, GENDER
from django import forms
from django.forms import ModelForm
from django_ckeditor_5.widgets import CKEditor5Widget

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Enter full name", "class":"form-control"}))
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder':"Enter username", "class":"form-control"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'placeholder':"Enter email address", "class":"form-control"}))
    gender = forms.ChoiceField(choices=GENDER,  widget=forms.Select(attrs={'class': 'form-control'}), required=True)
    valid_doc = forms.FileField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':"Enter password", "class":"form-control"}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':"Confirm Password", "class":"form-control"}))

    class Meta:
        model = User
        fields = ["full_name", "username", "email", 'gender', 'valid_doc', "password1", "password2"]
        
class EditProfile(ModelForm):
    image = forms.FileField(required=False)
    full_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Enter full name", "class": "form-control"}))
    bio = forms.CharField(
        widget=CKEditor5Widget(
            attrs={"class": "django_ckeditor_5"},
            config_name="extends"
        )
    )

    dob = forms.DateField(widget=forms.DateInput(attrs={'placeholder': "Date of birth", "class": "form-control", "type": "date"}), required=False)
    location = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Enter location", "class": "form-control"}), required=False)
    
    student_type = forms.ChoiceField(choices=STUDENT_TYPE, widget=forms.Select(attrs={'class': 'form-control'}), required=True)
    year_of_join = forms.DateField(widget=forms.DateInput(attrs={'placeholder': "Date of join", "class": "form-control", "type": "date"}), required=False)
    year_of_passout = forms.DateField(widget=forms.DateInput(attrs={'placeholder': "Date of passout", "class": "form-control", "type": "date"}), required=False)
    
    experience = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "eg: 2 years", "class": "form-control"}), required=False)
    skills = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "eg: leadership, communication", "class": "form-control"}), required=False)
    education = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "eg: Masters in Computer Science", "class": "form-control"}), required=False)
    instagram = forms.URLField(widget=forms.TextInput(attrs={'placeholder': "Enter Instagram profile", "class": "form-control"}), required=False)
    git = forms.URLField(widget=forms.TextInput(attrs={'placeholder': "Enter GitHub profile", "class": "form-control"}), required=False)
    linkdn = forms.URLField(widget=forms.TextInput(attrs={'placeholder': "Enter LinkedIn profile", "class": "form-control"}), required=False)

    class Meta:
        model = Profile
        fields = ['image', 'full_name', 'bio', 'location', 'student_type', 'year_of_join', 'year_of_passout', 'experience', 'skills', 'education', 'instagram', 'git', 'linkdn']
