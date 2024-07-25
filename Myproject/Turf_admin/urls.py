from django.urls import path
from . import views



urlpatterns = [
    path('adlogin/',views.admin_loginpage,name='adlogin'),
    path('adlogout/',views.admin_logoutpage,name='adlogout'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('matches/', views.match_list_admin, name='match_list_admin'),
    path('bookings/', views.booking_list_admin, name='booking_list_admin'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
     path('users/add/', views.add_user, name='add_user'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
     path('bookings/add/', views.add_booking, name='add_booking'),
    path('bookings/<int:booking_id>/edit/', views.edit_booking, name='edit_booking'),
    path('bookings/<int:booking_id>/delete/', views.delete_booking, name='delete_booking'),
    path('matches/add/', views.add_match, name='add_match'),
    path('matches/<int:match_id>/edit/', views.edit_match, name='edit_match'),
    path('matches/<int:match_id>/delete/', views.delete_match, name='delete_match'),
    # path('admin/users/block/<int:user_id>/', views.block_user, name='block_user'),
    # path('admin/users/unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
]