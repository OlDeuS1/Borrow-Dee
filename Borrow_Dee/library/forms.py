from django.forms import *
from django.forms.widgets import *
from .models import *

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