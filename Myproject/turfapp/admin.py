from django.contrib import admin
from .models import Profile,Booking,Match,MatchBooking
# Register your models here.

admin.site.register(Profile)
admin.site.register(Booking)
admin.site.register(Match)
admin.site.register(MatchBooking)
