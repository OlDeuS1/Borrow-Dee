from django.db import models
from datetime import timedelta, date
from django.db.models import Max

class Author(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    published_date = models.DateField()
    isbn_number = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    amount = models.IntegerField(default=1)
    author = models.ManyToManyField(Author)
    category = models.ManyToManyField(Category)
    image = models.FileField(upload_to="image/", blank=True, null=True)

    def __str__(self):
        return self.title
    
    class Meta:
        permissions = [
            # Member
            ('can_view_all_book', 'Can view all book'),
            ('can_search_books', 'Can search books'),
            ('can_filter_books', 'Can filter books'),
            ('can_borrow_book', 'Can borrow book'),
            ('can_reserve_book', 'Can reserve book'),
            ('can_rating_book', 'Can rating book'),
        ]
    
class Member(models.Model):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
    
    class Meta:
        permissions = [
            # Librarian
            ('can_view_all_member', 'Can view all member'),
            ('can_view_member_history', 'Can view member history'),
        ]
    
class Borrow(models.Model):

    class choices(models.TextChoices):
        BORROWED = 'borrowed', 'Borrowed'
        RETURNED = 'returned', 'Returned'
        OVERDUE = 'overdue', 'Overdue'

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, null=True, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True, null=True)
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=choices.choices, default=choices.BORROWED)
    renew = models.BooleanField(default=False) # ใช้ boolean แทน int เพราะให้ต่ออายุได้ครั้งเดียว

    # ให้ due_date มีค่าเริ่มต้นเป็น borrow_date + กี่วัน
    def save(self, *args, **kwargs):
        if not self.borrow_date:
            self.borrow_date = date.today()

        if not self.due_date:
            self.due_date = self.borrow_date + timedelta(days=7) # กำหนดเลขวันได้
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.username} borrowed {self.book.title}"
    
    class Meta:
        permissions = [
            # Member
            ('can_renew_own_borrow', 'Can renew own borrow'),
            ('can_view_own_borrow', 'Can view own borrow'),
            ('can_view_own_borrow_history', 'Can view own borrow history'),

            # Librarian
            ('can_view_all_borrow', 'Can view all borrow'),
            ('can_update_borrow_status', 'Can update borrow status'),
        ]
    
class Rating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    score = models.IntegerField()

    def __str__(self):
        return f"{self.member.username} rated {self.book.title} with {self.score} stars"

class Reservation(models.Model):

    class choices(models.TextChoices):
        WAITING = 'waiting', 'Waiting'
        READY = 'ready', 'Ready'
        CANCELLED = 'cancelled', 'Cancelled'
        COMPLETED = 'completed', 'Completed'
        
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, null=True, on_delete=models.CASCADE)
    reservation_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=choices.choices, default=choices.WAITING)
    queue_order = models.IntegerField(blank=True, null=True) # ลำดับคิวการจองของหนังสือแต่ละเล่ม
            
    def update_queue_all(self):
        reservations = Reservation.objects.filter(status = self.choices.WAITING, book=self.book).order_by('-reservation_date')
        count = 0
        for r in reservations:
            count += 1
            r.queue_order = count
            r.save()

    def save(self, *args, **kwargs):
        if not self.queue_order:
            # หาลำดับถัดไปสำหรับหนังสือเล่มนี้
            last_order = Reservation.objects.filter(
                book=self.book, status=self.choices.WAITING
            ).aggregate(
                Max('queue_order')
            )['queue_order__max']
            
            self.queue_order = (last_order or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.member.username} reserved {self.book.title} (Queue: {self.queue_order})"
    
    class Meta:
        permissions = [
            # Member
            ('can_cancel_own_reservation', 'Can cancel own reservation'),
            ('can_view_own_reservation', 'Can view own reservation'),

            # Librarian
            ('can_view_all_reservation', 'Can view all reservation'),
            ('can_update_reservation_status', 'Can update reservation status'),
        ]