from django.urls import path
from . import views 
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('home',views.home,name='home'), 
    path('register', views.register, name="register"),
    path('login',views.loginpage,name='login'),
    path('logout',views.logoutpage,name='logout'),
    path('profile',views.profilepage,name='profile'),
    path('update',views.updateprofile,name='update'),
    path('book', views.book_slot, name='book_slot'),
    path('payment', views.payment, name='payment'),
    path('history', views.booking_history, name='booking_history'),
    path('confirm_cancel_booking/<int:booking_id>', views.confirm_cancel_booking, name='confirm_cancel_booking'),
    path('cancel_booking/<int:booking_id>', views.cancel_booking, name='cancel_booking'),
    path('matches/', views.match_list, name='match_list'),
    path('bookmatch/<int:id>/', views.book_match, name='book_match'),
    path('matchpayment/<int:id>/', views.match_payment, name='match_payment'),
    path('bookingsuccess/<int:id>/', views.booking_success, name='booking_success'),
    path('cod-booking-complete/', views.cod_booking_complete, name='cod_booking_complete'),
    path('payment-failed/', views.payment_failed, name='payment_failed'),
    path('payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
    path('razorpay/callback/', views.razorpay_callback, name='razorpay_callback'),
]

urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
