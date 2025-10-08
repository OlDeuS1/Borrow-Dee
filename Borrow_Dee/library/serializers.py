from rest_framework import serializers
from library.models import Borrow, Reservation
from datetime import date

class BorrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['id', 'book', 'member', 'borrow_date', 'due_date', 'return_date', 'status', 'renew']

class BorrowAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrow
        fields = ['id', 'book', 'member', 'borrow_date', 'due_date', 'return_date', 'status', 'renew']

        def update(self, instance, validated_data):
            new_status = validated_data.get('status')
            old_status = instance.status
            instance.status = new_status
            
            if(new_status == Borrow.choices.RETURNED):
                if old_status == Borrow.choices.BORROWED or old_status == Borrow.choices.OVERDUE:
                    instance.return_date = date.today()
                    waiting_reserve = Reservation.objects.filter(book=instance.book, status=Reservation.choices.WAITING).order_by('reservation_date')
                
                    if waiting_reserve.exists():
                        first_queue = waiting_reserve.first()
                        first_queue.status = Reservation.choices.READY
                        first_queue.save()
            instance.save()
            return instance

class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['id', 'book', 'member', 'reservation_date', 'status']

    def update(self, instance, validated_data):
        new_status = validated_data.get('status')
        old_status = instance.status

        if(new_status == Reservation.choices.CANCELLED):
            if old_status in [Reservation.choices.WAITING, Reservation.choices.READY]:
                instance.status = new_status

                if old_status == Reservation.choices.READY:
                    waiting_reserve = Reservation.objects.filter(book=instance.book, status=Reservation.choices.WAITING).order_by('reservation_date')
                    
                    if waiting_reserve.exists():
                        first_queue = waiting_reserve.first()
                        first_queue.status = Reservation.choices.READY
                        first_queue.save()

        elif new_status == Reservation.choices.COMPLETED:
            if old_status == Reservation.choices.READY:
                instance.status = new_status

                Borrow.objects.create(
                    book=instance.book,
                    member=instance.member,
                    status='borrowed',
                )

                waiting_reserve = Reservation.objects.filter(book=instance.book, status=Reservation.choices.WAITING).order_by('reservation_date')
                
                if waiting_reserve.exists():
                    first_queue = waiting_reserve.first()
                    first_queue.status = Reservation.choices.READY
                    first_queue.save()
        instance.save()
        return instance