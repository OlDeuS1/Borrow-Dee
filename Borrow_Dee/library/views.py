from multiprocessing import context
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
            print(f" {user} login successful")
            return redirect("home")
        
        return render(request, "login.html", {"form": form})
    
class Logout(View):
    def get(self, request):
        logout(request)
        print("User logged out successfully")
        return redirect('home')

class RegisterView(View):

    def get(self, request):
        form = RegisterForm()
        mem_form = MemberForm()
        return render(request, "register.html", {"form": form, "mem_form": mem_form})

    def post(self, request):
        form = RegisterForm(data=request.POST)
        mem_form = MemberForm(data=request.POST)
        if form.is_valid() and mem_form.is_valid():
            user = form.save()
            mem = mem_form.save(commit=False)
            mem.username = user.username
            mem.email = user.email
            mem.save()

            member_group = Group.objects.get(name='Member')
            user.groups.add(member_group)

            login(request, user)
            print(f" {user} registration successful")
            return redirect("home")
        
        return render(request, "register.html", {"form": form, "mem_form": mem_form})

class IndexView(View):
    def get(self, request):
        books = Book.objects.annotate(borrow_count=Count('borrow'), avg_rating=Avg('rating__score'))
        popular_books = books.order_by('-borrow_count')[:14]
        new_books = books.order_by('-published_date')[:14]
        return render(request, "index.html", {"popular_books": popular_books, "new_books": new_books})

class BrowseView(View):
    def get(self, request):
        search_query = request.GET.get('search', '')
        sort = request.GET.get('sort', '')
        filter_categories = request.GET.getlist('category')
        filter_authors = request.GET.getlist('author')
        filter_availability = request.GET.get('available', '')

        books = Book.objects.annotate(borrow_count=Count('borrow'), available_count=F('amount') - F('borrow_count'), avg_rating=Avg('rating__score', default=0))
        authors = Author.objects.all()
        categories = Category.objects.all()

        if sort:
            if sort == 'newest':
                books = books.order_by('-published_date')
            elif sort == 'oldest':
                books = books.order_by('published_date')
            elif sort == 'rating-up':
                books = books.order_by('-avg_rating')
            elif sort == 'rating-down':
                books = books.order_by('avg_rating')

        if search_query:
            books = books.filter(title__icontains=search_query)
        if filter_categories:
            books = books.filter(category__name__in=filter_categories)
        if filter_authors:
            books = books.filter(author__name__in=filter_authors)

        if filter_availability == 'true':
            books = books.filter(available_count__gt=0)

        context = {
            "books": books,
            "authors": authors,
            "categories": categories,
            "search_query": search_query,
            "sort": sort,
            "filter_categories": filter_categories,
            "filter_authors": filter_authors,
            "filter_availability": filter_availability,
        }

        return render(request, "browse.html", context)
    
class BookDetailView(View):
    def get(self, request, book_id):
        book = Book.objects.annotate(avg_rating=Avg('rating__score', default=0), borrow_count=Count('borrow'), copies_available=F('amount') - F('borrow_count')).get(id=book_id)
        return render(request, "bookDetail.html", {"book": book})
    
class DashboardView(View):

    def get(self, request):

        return render(request, "dashboard.html")
    
class BookManagementView(View):

    def get(self, request):
        
        return render(request, "book_management.html")
    
class CategoryManagementView(View):

    def get(self, request):

        return render(request, "category_management.html")
    
class LoanManagementView(View):

    def get(self, request):

        return render(request, "loan_management.html")