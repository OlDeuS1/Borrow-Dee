from django.forms import *
from django.forms.widgets import *
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms

class BookForm(ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'published_date', 'isbn_number', 'amount', 'description', 'image']
        widgets = {
            'title': TextInput(),
            'author': SelectMultiple(),
            'category': SelectMultiple(),
            'published_date': DateInput(attrs={'type': 'date'}),
            'isbn_number': TextInput(),
            'amount': NumberInput(),
            'description': Textarea(attrs={'rows': 4}),
            'image': FileInput(),
        }

class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': TextInput(),
        }

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email',
        max_length=255,
        widget=forms.EmailInput(attrs={
            'class': 'login__form-input bg-white rounded-[1.5rem] w-full p-6 text-[#403D39] text-[1.6rem] border-2 border-[#E07A5F] focus:border-[#ba5e49] focus:outline-none transition-all',
            'placeholder': 'enter your email here.',
            'required': True
        })
    )
    
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'login__form-input bg-white rounded-[1.5rem] w-full p-6 text-[#403D39] text-[1.6rem] border-2 border-[#E07A5F] focus:border-[#ba5e49] focus:outline-none transition-all',
            'placeholder': 'enter your password here.',
            'required': True
        })
    )
    
    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if email and password:
            try:
                user = User.objects.get(email=email)
                self.cleaned_data['username'] = user.username
            except User.DoesNotExist:
                raise forms.ValidationError('Invalid email or password.')
        
        return super().clean()
    
class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        max_length=255,
        required=True,
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists() and Member.objects.filter(email=email).exists():
            raise forms.ValidationError('Email address must be unique.')
        return email
    
class MemberForm(ModelForm):
    class Meta:
        model = Member
        fields = ['phone_number', 'address']
        widgets = {
            'phone_number': TextInput(),
            'address': Textarea(attrs={'rows': 4}),
        }
