from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("browse/", views.BrowseView.as_view(), name="browse"),
    path("books/<int:book_id>/", views.BookDetailView.as_view(), name="book_detail"),
    path("myborrows/", views.MyBorrowsView.as_view(), name="myborrows"),
    path("myreservations/", views.MyReservationsView.as_view(), name="myreservations"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/books/", views.BookManagementView.as_view(), name="book_management"),
    path("dashboard/books/add/", views.AddBookView.as_view(), name="add_book"),
    path("dashboard/books/edit/<int:book_id>/", views.EditBookView.as_view(), name="edit_book"),
    path('dashboard/books/delete/<int:book_id>/', views.BookDelete.as_view(), name="book-delete"),
    path("dashboard/categories/", views.CategoryManagementView.as_view(), name="category_management"),
    path('dashboard/categories/delete/<int:category_id>/', views.CategoryDelete.as_view(), name="category-delete"),
    path("dashboard/loans/", views.LoanManagementView.as_view(), name="loan_management"),
    path("dashboard/reservations/", views.ReservationManagementView.as_view(), name="reservation_management"),
    path("dashboard/users/", views.UserManagementView.as_view(), name="user_management"),
    path("dashboard/users/history/", views.UserHistoryView.as_view(), name="user_history"),

    # API
    path('api/borrows/', views.BorrowList.as_view(), name="borrow-list"),
    path('api/borrows/<int:borrow_id>/', views.BorrowDetail.as_view(), name="borrow-detail"),
    path('api/reservations/', views.ReservationList.as_view(), name="reservation-list"),
    path('api/reservations/<int:reserve_id>/', views.ReservationDetail.as_view(), name="reservation-detail"),

    # TomSelect autocomplete URLs
    path("author-autocomplete/", views.AuthorAutocompleteView.as_view(), name="author-autocomplete"),
    path("category-autocomplete/", views.CategoryAutocompleteView.as_view(), name="category-autocomplete"),
]