from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import time, datetime, timedelta
from django.core.validators import RegexValidator

# Create your models here.

class Profile(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=100,null=True)
    last_name=models.CharField(max_length=100,null=True)
    full_name= models.CharField(max_length=100,null=True)
    email= models.EmailField(null=True,unique=True)
    image= models.ImageField(upload_to='profile',default='profile/default_profile_image.jpg')
    blocked = models.BooleanField(default=False) 
    phone_regex = RegexValidator(
        regex=r'^\d+$',
        message="Phone number must contain only digits."
    )
    
    phone_no = models.CharField(
        max_length=13,  # Adjust max_length as needed
        validators=[phone_regex],
        null=True,    # Optional: allows null values in the database
    )

    def __str__(self) -> str:
        return self.user.username

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    total_hours = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2,null=True)
    payment_status = models.BooleanField(default=False)
    booking_time = models.DateTimeField(default=timezone.now)  # Set a default value
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    PAYMENT_METHODS = [
        ('RAZORPAY', 'Razorpay'),
        ('COD', 'Cash on Delivery'),
    ]
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default='COD')

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.start_time} to {self.end_time}"
    
    # @staticmethod
    # def is_slot_available(date, start_time, end_time):
    #     bookings = Booking.objects.filter(date=date)
        

    #     for booking in bookings:
    #         booking_start = datetime.combine(date, booking.start_time)
    #         booking_end = booking_start + timedelta(hours=booking.total_hours)
    #         requested_start = datetime.combine(date, start_time)
    #         requested_end = datetime.combine(date, end_time)

    #         # Check for overlap
    #         if (requested_start < booking_end and requested_end > booking_start):
    #             return False
    #     return True
    
    @staticmethod
    def is_slot_available(date, start_time, end_time):
        bookings = Booking.objects.filter(date=date)
        
        # Convert start_time and end_time to datetime objects
        start_datetime = datetime.combine(date, start_time)
        end_datetime = datetime.combine(date, end_time)
        
        if end_datetime <= start_datetime:
            end_datetime += timedelta(days=1)  # Extend to the next day if the end time is before start time

        for booking in bookings:
            booking_start = datetime.combine(date, booking.start_time)
            booking_end = booking_start + timedelta(hours=booking.total_hours)
            
            if booking_end <= booking_start:
                booking_end += timedelta(days=1)  # Extend to the next day if the booking end time is before start time

            # Check for overlap
            if (start_datetime < booking_end and end_datetime > booking_start):
                return False
        return True
    
class Match(models.Model):
    SPORT_CHOICES = [
        ('cricket', 'Cricket'),
        ('football', 'Football'),
    ]

    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    sport_type = models.CharField(max_length=10, choices=SPORT_CHOICES)
    max_players = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2,default=120)
    players = models.ManyToManyField(User, through='MatchBooking', related_name='matches')

    def __str__(self):
        return f"{self.get_sport_type_display()} Match on {self.date} from {self.start_time} to {self.end_time}"
    
    def available_slots(self):
        return self.max_players - self.bookings.count()

class MatchBooking(models.Model):
    match = models.ForeignKey(Match, related_name='bookings', on_delete=models.CASCADE)
    player = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('match', 'player')

    def __str__(self):
        return f"{self.player} booked for {self.match}"