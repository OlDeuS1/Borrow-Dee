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
from django_tomselect.autocompletes import AutocompleteModelView

from django.http import Http404, HttpResponseForbidden
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from library.serializers import BorrowSerializer, ReservationSerializer

# API

# api/borrows/
class BorrowList(APIView):
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

# api/borrows/<int:borrow_id>/
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

# api/reservations/
class ReservationList(APIView):
    def post(self, request, format=None):
        try:
            request.user = Member.objects.get(username = request.user.username)
        except Member.DoesNotExist:
            return Response({"error": "Member not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ReservationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(member=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# api/reservations/<int:reserve_id>/
class ReservationDetail(APIView):
    def get_object(self, reserve_id):
        try:
            return Reservation.objects.get(id = reserve_id)
        except Reservation.DoesNotExist:
            raise Http404

    def patch(self, request, reserve_id, format=None):
        try:
            request.user = Member.objects.get(username = request.user.username)
        except Member.DoesNotExist:
            return Response({"error": "Member not found."}, status=status.HTTP_404_NOT_FOUND)
        
        reservation = self.get_object(reserve_id)
        serializer = ReservationSerializer(reservation, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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

# Home page
class IndexView(View):
    def get(self, request):
        books = Book.objects.annotate(borrow_count=Count('borrow'), avg_rating=Avg('rating__score'))
        popular_books = books.order_by('-borrow_count')[:14]
        new_books = books.order_by('-published_date')[:14]
        return render(request, "index.html", {"popular_books": popular_books, "new_books": new_books})

# Browse page
class BrowseView(View):
    def get(self, request):
        search_query = request.GET.get('search', '')
        sort = request.GET.get('sort', '')
        filter_categories = request.GET.getlist('category')
        filter_authors = request.GET.getlist('author')
        filter_availability = request.GET.get('available', '')

        books = Book.objects.annotate(
                                        borrow_count=Count('borrow', filter=~Q(borrow__status='returned'), distinct=True),
                                        reservation_count=Count('reservation', filter=Q(reservation__status__in = ['ready', 'waiting']), distinct=True),
                                        available_count=F('amount') - F('borrow_count') - F('reservation_count'), 
                                        avg_rating=Avg('rating__score', default=0)
                                    )
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
            books = books.filter(available_count__gte=1)

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

# BookDetail page
class BookDetailView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["library.can_borrow_book", 'library.can_reserve_book', 'library.view_book']
    
    def get(self, request, book_id):
        book = Book.objects.annotate(avg_rating=Avg('rating__score', default=0)).get(id=book_id)
        borrowed = Borrow.objects.filter(Q(member__username = request.user.username), Q(book = book), ~Q(status = "returned")).exists()
        reserved = Reservation.objects.filter(member__username = request.user.username, book = book, status__in = ['ready', 'waiting']).exists()
        return render(request, "bookDetail.html", {"book": book, "borrowed": borrowed, "reserved": reserved})

# MyBorrows page
class MyBorrowsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["library.can_renew_own_borrow", 'library.can_view_own_borrow']
    
    def get(self, request):
            borrows = Borrow.objects.filter(member__username = request.user.username).order_by('-borrow_date')
            return render(request, 'myborrows.html', {"borrows": borrows})

# MyReservations page
class MyReservationsView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = 'login'
    permission_required = ["library.can_cancel_own_reservation", 'library.can_view_own_reservation', 'library.can_borrow_book']
    
    def get(self, request):
        reservations = Reservation.objects.filter(member__username = request.user.username).exclude(status = 'completed').order_by('-reservation_date')
        return render(request, 'myreservations.html', {"reservations": reservations})
    
class DashboardView(View):

    def get(self, request):
        user_total = Member.objects.count()
        book_total = Book.objects.count()
        category_total = Category.objects.count()
        loan_total = Borrow.objects.count()
        reserve_total = Reservation.objects.count()
        context = {
            "user_total": user_total,
            "book_total": book_total,
            "category_total": category_total,
            "loan_total": loan_total,
            "reserve_total": reserve_total,
        }
        return render(request, "dashboard.html", context)

class BookManagementView(View):

    def get(self, request):
        search_query = request.GET.get('search', '')
        books = Book.objects.all()
        if search_query:
            books = books.filter(title__icontains=search_query)
        book_total = books.count()
        
        context = {
            "books": books.order_by('id'),
            "book_total": book_total,
            "search_query": search_query,
        }
        return render(request, "book_management.html", context)

class AddBookView(View):
    
    def get(self, request):
        form = BookForm()
        return render(request, "add_book.html", {"form": form})
    
    def post(self, request):
        post_data = request.POST.copy()
        
        post_data.pop('author', None)
        post_data.pop('category', None)
        
        form = BookForm(post_data, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.save()
            
            author_list = request.POST.getlist('author')
            for author_value in author_list:
                try:
                    author_id = int(author_value)
                    author_obj = Author.objects.get(id=author_id)
                    book.author.add(author_obj)
                except (ValueError, Author.DoesNotExist):
                    if author_value.strip():
                        author_obj, created = Author.objects.get_or_create(name=author_value.strip())
                        book.author.add(author_obj)

            category_list = request.POST.getlist('category')
            for category_value in category_list:
                try:
                    category_id = int(category_value)
                    category_obj = Category.objects.get(id=category_id)
                    book.category.add(category_obj)
                except (ValueError, Category.DoesNotExist):
                    if category_value.strip():
                        category_obj, created = Category.objects.get_or_create(name=category_value.strip())
                        book.category.add(category_obj)
            
            print(f"Book '{book.title}' created successfully")
            return redirect("book_management")
        else:
            form.data = request.POST
            return render(request, "add_book.html", {"form": form})
    
class EditBookView(View):
    
    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        form = BookForm(instance=book)
        return render(request, "edit_book.html", {"form": form, "book": book})
    
    def post(self, request, book_id):
        post_data = request.POST.copy()

        post_data.pop('author', None)
        post_data.pop('category', None)
        
        book = get_object_or_404(Book, id=book_id)
        form = BookForm(post_data, request.FILES, instance=book)
        if form.is_valid():
            book = form.save(commit=False)
            book.save()
            
            book.author.clear()
            book.category.clear()
            
            author_list = request.POST.getlist('author')
            for author_value in author_list:
                try:
                    author_id = int(author_value)
                    author_obj = Author.objects.get(id=author_id)
                    book.author.add(author_obj)
                except (ValueError, Author.DoesNotExist):
                    if author_value.strip():
                        author_obj, created = Author.objects.get_or_create(name=author_value.strip())
                        book.author.add(author_obj)

            category_list = request.POST.getlist('category')
            for category_value in category_list:
                try:
                    category_id = int(category_value)
                    category_obj = Category.objects.get(id=category_id)
                    book.category.add(category_obj)
                except (ValueError, Category.DoesNotExist):
                    if category_value.strip():
                        category_obj, created = Category.objects.get_or_create(name=category_value.strip())
                        book.category.add(category_obj)
            
            print(f"Book '{book.title}' updated successfully")
            return redirect("book_management")
        else:
            form.data = request.POST
            return render(request, "edit_book.html", {"form": form, "book": book})

class BookDelete(View):
    
    def get(self, request, book_id):
        book = get_object_or_404(Book, id=book_id)
        book.delete()
        return redirect('book_management')
    
class CategoryManagementView(View):

    def get(self, request):
        search_query = request.GET.get('search', '')
        categories = Category.objects.all()
        if search_query:
            categories = categories.filter(name__icontains=search_query)
        category_total = categories.count()

        context = {
            "categories": categories.order_by('id'),
            "category_total": category_total,
            "search_query": search_query,
        }
        return render(request, "category_management.html", context)

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