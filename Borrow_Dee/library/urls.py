from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("browse/", views.BrowseView.as_view(), name="browse"),
    path("books/<int:book_id>/", views.BookDetailView.as_view(), name="book_detail"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/books/", views.BookManagementView.as_view(), name="book_management"),
    path("dashboard/categories/", views.CategoryManagementView.as_view(), name="category_management"),
    path("dashboard/loans/", views.LoanManagementView.as_view(), name="loan_management"),
    path("dashboard/reservations/", views.ReservationManagementView.as_view(), name="reservation_management"),
    path("dashboard/users/", views.UserManagementView.as_view(), name="user_management"),
]