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
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django_tomselect.autocompletes import AutocompleteModelView

from django.http import Http404, HttpResponseForbidden
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from library.serializers import BookSerializer, CategorySerializer, AuthorSerializer, BorrowSerializer, MemberSerializer

# API
class MemberList(APIView):
    def get(self, request, format=None):
        members = Member.objects.all()
        serializer = MemberSerializer(members, many=True)
        return Response(serializer.data)
    
class MemberDetail(APIView):
    def get_object(self, member_id):
        try:
            return Member.objects.get(id = member_id)
        except Member.DoesNotExist:
            raise Http404

    def get(self, request, member_id, format=None):
        member = self.get_object(member_id)
        serializer = MemberSerializer(member)
        return Response(serializer.data)

class BookList(APIView):
    def get(self, request, format=None):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

class BorrowList(APIView):
    def get(self, request, format=None):
        borrows = Borrow.objects.all()
        serializer = BorrowSerializer(borrows, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        try:
            request.user = Member.objects.get(username = request.user.username)
        except Member.DoesNotExist:
            return Response({"error": "Member not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = BorrowSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(member=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BorrowDetail(APIView):
    def get_object(self, borrow_id):
        try:
            return Borrow.objects.get(id = borrow_id)
        except Borrow.DoesNotExist:
            raise Http404

    def get(self, request, borrow_id, format=None):
        borrow = self.get_object(borrow_id)
        serializer = BorrowSerializer(borrow)
        return Response(serializer.data)
    # def put(self, request):
        
    # def delete(self, request):

# Normal View 
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

class IndexView(UserPassesTestMixin, View):
    def test_func(self):
        return not self.request.user.groups.filter(name = "Librarian").exists()
    
    def get(self, request):
        books = Book.objects.annotate(borrow_count=Count('borrow'), avg_rating=Avg('rating__score'))
        popular_books = books.order_by('-borrow_count')[:14]
        new_books = books.order_by('-published_date')[:14]
        return render(request, "index.html", {"popular_books": popular_books, "new_books": new_books})

class BrowseView(UserPassesTestMixin, View):
    def test_func(self):
        return not self.request.user.groups.filter(name = "Librarian").exists()
    
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
    
class BookDetailView(UserPassesTestMixin, View):
    def test_func(self):
        return not self.request.user.groups.filter(name = "Librarian").exists()
    
    def get(self, request, book_id):
        book = Book.objects.annotate(avg_rating=Avg('rating__score', default=0), borrow_count=Count('borrow'), copies_available=F('amount') - F('borrow_count')).get(id=book_id)
        borrowed = Borrow.objects.filter(member__username = request.user.username, book = book, status = "borrowed").first
        return render(request, "bookDetail.html", {"book": book, "borrowed": borrowed})

class MyBorrowsView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, View):
    login_url = 'login/'
    permission_required = ["library.view_borrow", 'library.change_borrow']

    def test_func(self):
        return not self.request.user.groups.filter(name = "Librarian").exists()
    
    def get(self, request):
            borrows = Borrow.objects.filter(member__username = request.user.username)
            return render(request, 'myborrows.html', {"borrows": borrows})
    
class DashboardView(View):

    def get(self, request):

        return render(request, "dashboard.html")
    
class BookManagementView(View):

    def get(self, request):
        form = BookForm()
        return render(request, "book_management.html", {"form": form})

class CategoryManagementView(View):

    def get(self, request):

        return render(request, "category_management.html")
    
class LoanManagementView(View):

    def get(self, request):

        return render(request, "loan_management.html")
    
class ReservationManagementView(View):

    def get(self, request):

        return render(request, "reservation_management.html")

class UserManagementView(View):

    def get(self, request):

        return render(request, "user_management.html")
    
class UserHistoryView(View):

    def get(self, request):

        return render(request, "user_history.html")

# TomSelect Autocomplete Views
class AuthorAutocompleteView(AutocompleteModelView):
    model = Author
    search_lookups = ['name__icontains']
    value_field = 'name'

class CategoryAutocompleteView(AutocompleteModelView):
    model = Category
    search_lookups = ['name__icontains']
    value_field = 'name'