from rest_framework import serializers
from library.models import Book, Category, Author, Borrow, Member, Reservation

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['id', 'username', 'email', 'phone_number', 'address']

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'published_date', 'isbn_number', 'description', 'amount', 'author', 'category', 'image']

class BorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['id', 'book', 'member', 'borrow_date', 'due_date', 'return_date', 'status', 'renew']

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'book', 'member', 'reservation_date', 'status', 'queue_order']