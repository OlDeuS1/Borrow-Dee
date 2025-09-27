from django.shortcuts import render, redirect
from django.views import View
from .models import *
from django.db.models import *
from django.db.models.functions import *
from django.shortcuts import redirect, get_object_or_404
from .forms import *
from django.db import transaction
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group
    
class LoginView(View):

    def get(self, request):
        form = LoginForm()
        return render(request, "login.html", {"form": form})

    def post(self, request):
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user() 
            login(request, user)
            return redirect("home")
        
        return render(request, "login.html", {"form": form})
    
class Logout(View):
    def get(self, request):
        logout(request)
        return redirect('index')

class RegisterView(View):

    def get(self, request):
        form = RegisterForm()
        return render(request, "register.html", {"form": form})

    def post(self, request):
        form = RegisterForm(data=request.POST)
        if form.is_valid():
            user = form.save()

            member_group = Group.objects.get(name='Member')
            user.groups.add(member_group)

            login(request, user)
            return redirect("home")
        
        return render(request, "register.html", {"form": form})

class IndexView(View):
    def get(self, request):
        books = Book.objects.annotate(borrow_count=Count('borrow'), avg_rating=Avg('rating__score'))
        popular_books = books.order_by('-borrow_count')[:14]
        new_books = books.order_by('-published_date')[:14]
        return render(request, "index.html", {"popular_books": popular_books, "new_books": new_books})

class BrowseView(View):
    def get(self, request):
        search_query = request.GET.get('search', '')
        print(search_query)
        books = Book.objects.filter(title__icontains=search_query)
        return render(request, "browse.html", {"books": books})