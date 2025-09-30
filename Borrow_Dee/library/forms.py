from django.forms import *
from django.forms.widgets import *
from .models import *
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django_tomselect.forms import TomSelectModelMultipleChoiceField
from django_tomselect.app_settings import TomSelectConfig

class BookForm(ModelForm):
    
    author = TomSelectModelMultipleChoiceField(
        config=TomSelectConfig(
            url='author-autocomplete',
            create=True,
            highlight=True,
            close_after_select=False,
            open_on_focus=True,
            placeholder="Select or type new authors...",
        ),
        attrs={
                'class': 'w-full bg-[#424242] border border-gray-600/40 rounded-[15px] px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-[#2C7852] focus:ring-2 focus:ring-[#2C7852]/20 transition-all',
            },
        required=False
    )
    
    category = TomSelectModelMultipleChoiceField(
        config=TomSelectConfig(
            url='category-autocomplete',
            create=True,
            highlight=True,
            close_after_select=False,
            open_on_focus=True,
            placeholder="Select or type new categories...",
        ),
        attrs={
            'class': 'w-full bg-[#424242] border border-gray-600/40 rounded-[15px] px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-[#2C7852] focus:ring-2 focus:ring-[#2C7852]/20 transition-all',
        },
        required=False
    )
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'category', 'published_date', 'isbn_number', 'amount', 'description', 'image']
        widgets = {
            'title': TextInput(attrs={
                'required': True,
                'placeholder': 'Enter book title',
                'class': 'w-full bg-[#424242] border border-gray-600/40 rounded-[15px] px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-[#2C7852] focus:ring-2 focus:ring-[#2C7852]/20 transition-all'
            }),
            'published_date': DateInput(attrs={
                'type': 'date',
                'class': 'w-full bg-[#424242] border border-gray-600/40 rounded-[15px] px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-[#2C7852] focus:ring-2 focus:ring-[#2C7852]/20 transition-all',
                'placeholder': "Select publication date..."
            }),
            'isbn_number': TextInput(attrs={
                'class': 'w-full bg-[#424242] border border-gray-600/40 rounded-[15px] px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-[#2C7852] focus:ring-2 focus:ring-[#2C7852]/20 transition-all',
                'required': True,
                'placeholder': "Enter book ISBN number..."
            }),
            'amount': NumberInput(attrs={
                'class': 'w-full bg-[#424242] border border-gray-600/40 rounded-[15px] px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-[#2C7852] focus:ring-2 focus:ring-[#2C7852]/20 transition-all',
                'required': True,
            }),
            'description': Textarea(attrs={
                'class': 'w-full bg-[#424242] border border-gray-600/40 rounded-[15px] px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-[#2C7852] focus:ring-2 focus:ring-[#2C7852]/20 transition-all',
                'rows': 4,
                'placeholder': "Enter book description..."
            }),
            'image': FileInput(attrs={
                'accept': 'image/*',
                'placeholder': "Upload book image..."
                
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        isbn_number = cleaned_data.get('isbn_number')
        amount = cleaned_data.get('amount')
        published_date = cleaned_data.get('published_date')

        if Book.objects.filter(isbn_number=isbn_number).exclude(pk=self.instance.pk).exists():
            self.add_error('isbn_number', 'ISBN number must be unique.')
            
        if amount <= 0:
            self.add_error('amount', 'Amount must be positive.')

        if published_date and published_date > date.today():
            self.add_error('published_date', 'Published date cannot be in the future.')

        return cleaned_data

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
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'register__form-input bg-white rounded-[1.5rem] w-full p-6 text-[#403D39] text-[1.6rem] border-2 border-[#E07A5F] focus:border-[#ba5e49] focus:outline-none transition-all',
            'placeholder': 'enter your username here.'
        })
    )
    
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'register__form-input bg-white rounded-[1.5rem] w-full p-6 text-[#403D39] text-[1.6rem] border-2 border-[#E07A5F] focus:border-[#ba5e49] focus:outline-none transition-all',
            'placeholder': 'enter your email here.'
        })
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'register__form-input bg-white rounded-[1.5rem] w-full p-6 text-[#403D39] text-[1.6rem] border-2 border-[#E07A5F] focus:border-[#ba5e49] focus:outline-none transition-all',
            'placeholder': 'enter your password here.'
        })
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'register__form-input bg-white rounded-[1.5rem] w-full p-6 text-[#403D39] text-[1.6rem] border-2 border-[#E07A5F] focus:border-[#ba5e49] focus:outline-none transition-all',
            'placeholder': 'confirm your password here.'
        })
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
            'phone_number': TextInput(attrs={
                'class': 'register__form-input bg-white rounded-[1.5rem] w-full p-6 text-[#403D39] text-[1.6rem] border-2 border-[#E07A5F] focus:border-[#ba5e49] focus:outline-none transition-all',
                'placeholder': 'enter your phone number here.',
                'required': True
            }),
            'address': TextInput(attrs={
                'class': 'register__form-input bg-white rounded-[1.5rem] w-full p-6 text-[#403D39] text-[1.6rem] border-2 border-[#E07A5F] focus:border-[#ba5e49] focus:outline-none transition-all',
                'placeholder': 'enter your address here.',
                'required': True
            }),
        }

