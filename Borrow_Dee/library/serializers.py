from rest_framework import serializers
from library.models import Borrow, Reservation

class BorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['id', 'book', 'member', 'borrow_date', 'due_date', 'return_date', 'status', 'renew']

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'book', 'member', 'reservation_date', 'status']