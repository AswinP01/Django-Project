from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserForm,MatchForm
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import time, datetime, timedelta
from django.contrib.auth import login,logout,authenticate
import json
from django.http import JsonResponse

# Create your views here.
from turfapp.forms import BookingForm
from turfapp.models import Profile,Booking,Match,MatchBooking

# Check if the user is an admin
def is_admin(user):
    return user.is_superuser

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_users = Profile.objects.count()
    total_bookings = Booking.objects.count()
    total_matches = Match.objects.count()
      # Revenue from Bookings
    total_booking_revenue = Booking.objects.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Revenue from Matches
    total_match_revenue = Match.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Combined Total Revenue
    total_revenue = total_booking_revenue + total_match_revenue
    upcoming_matches = Match.objects.filter(date__gte=timezone.now()).order_by('date')[:5]

    recent_activities = Booking.objects.order_by('-booking_time')[:10]
    match_bookings = MatchBooking.objects.all()[:10]
    user_registrations = Profile.objects.order_by('-user__date_joined')[:10]
    
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    # Bookings Data
    bookings_data = Booking.objects.filter(booking_time__gte=last_30_days) \
        .extra({'day': "date(booking_time)"}) \
        .values('day') \
        .annotate(count=Count('id')) \
        .order_by('day')
    
    bookings_chart_data = {
        'labels': [entry['day'].strftime('%Y-%m-%d') for entry in bookings_data],
        'data': [float(entry['count']) for entry in bookings_data]
    }
    
    # Revenue Data for Bookings
    revenue_data_bookings = Booking.objects.filter(booking_time__gte=last_30_days) \
        .extra({'day': "date(booking_time)"}) \
        .values('day') \
        .annotate(total_revenue=Sum('total_price')) \
        .order_by('day')
    
    revenue_chart_data_bookings = {
        'labels': [entry['day'].strftime('%Y-%m-%d') for entry in revenue_data_bookings],
        'data': [float(entry['total_revenue']) for entry in revenue_data_bookings]
    }
    
    # Revenue Data for Matches
    revenue_data_matches = Match.objects.filter(date__gte=last_30_days) \
        .extra({'day': "date(date)"}) \
        .values('day') \
        .annotate(total_revenue=Sum('amount')) \
        .order_by('day')
    
    revenue_chart_data_matches = {
        'labels': [entry['day'].strftime('%Y-%m-%d') for entry in revenue_data_matches],
        'data': [float(entry['total_revenue']) for entry in revenue_data_matches]
    }
     # Combine Revenue Chart Data
    combined_revenue_chart_data = {
        'labels': revenue_chart_data_bookings['labels'],
        'data_bookings': revenue_chart_data_bookings['data'],
        'data_matches': revenue_chart_data_matches['data']
    }

    context = {
        'total_users': total_users,
        'total_bookings': total_bookings,
        'total_matches': total_matches,
        'total_booking_revenue': total_booking_revenue,
        'total_match_revenue': total_match_revenue,
        'total_revenue': total_revenue,
        'upcoming_matches': upcoming_matches,
        'recent_activities': recent_activities,
        'match_bookings' : match_bookings,
        'user_registrations': user_registrations,
        'bookings_chart_data': json.dumps(bookings_chart_data),
        'revenue_chart_data_bookings': json.dumps(revenue_chart_data_bookings),
        'revenue_chart_data_matches': json.dumps(revenue_chart_data_matches),
        'combined_revenue_chart_data': json.dumps(combined_revenue_chart_data),
    }

    return render(request, 'dashboard.html', context)

def admin_loginpage(request):
    if request.method=='POST':
        username=request.POST.get('usern')
        password=request.POST.get('passw')
        user=authenticate(request,username=username,password=password)
        if user:
            login(request,user)
            return redirect(admin_dashboard)
    else:
            print('no such user')
    return render(request,'admin_login.html')

def admin_logoutpage(request):
    logout(request)
    return redirect(admin_loginpage) 

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def user_list(request):
    users = Profile.objects.all()
    return render(request, 'user_list.html', {'users': users})

# @login_required(login_url='adlogin')
# @user_passes_test(is_admin)
# def block_user(request, user_id):
#     try:
#         user = User.objects.get(id=user_id)
#         user.profile.blocked = True
#         user.profile.save()
#         messages.success(request, f'User {user.username} has been blocked.')
#     except User.DoesNotExist:
#         messages.error(request, 'No User matches the given query.')
#     return redirect('user_list')

# @login_required(login_url='adlogin')
# @user_passes_test(is_admin)
# def unblock_user(request, user_id):
#     try:
#         user = User.objects.get(id=user_id)
#         user.profile.blocked = False
#         user.profile.save()
#         messages.success(request, f'User {user.username} has been unblocked.')
#     except User.DoesNotExist:
#         messages.error(request, 'No User matches the given query.')
#     return redirect('user_list')

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def user_detail(request, user_id):
    user = get_object_or_404(Profile, id=user_id)
    return render(request, 'user_detail.html', {'user': user})

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Set the user's password
            user.save()
            messages.success(request, 'User added successfully.')
            return redirect('user_list')
    else:
        form = UserForm()
    return render(request, 'add_user.html', {'form': form})

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def edit_user(request, user_id):
    user = get_object_or_404(Profile, id=user_id)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User details updated successfully.')
            return redirect('user_list')
    else:
        form = UserForm(instance=user.user)
    return render(request, 'edit_user.html', {'form': form})

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(Profile, id=user_id)
    if request.method == 'POST':
        user.user.delete()
        messages.success(request, 'User deleted successfully.')
        return redirect('user_list')
    return render(request, 'delete_user.html', {'user': user})


@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def booking_list_admin(request):
    bookings = Booking.objects.all().order_by('-booking_time')
    return render(request, 'booking_list_admin.html', {'bookings': bookings})


@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def add_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking added successfully.')
            return redirect(booking_list_admin)
    else:
        form = BookingForm()
    return render(request, 'add_booking.html', {'form': form})

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking updated successfully.')
            return redirect(booking_list_admin)
    else:
        form = BookingForm(instance=booking)
    return render(request, 'edit_booking.html', {'form': form})

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == 'POST':
        booking.delete()
        messages.success(request, 'Booking deleted successfully.')
        return redirect(booking_list_admin)
    return render(request, 'delete_booking.html', {'booking': booking})

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def match_list_admin(request):
    matches = Match.objects.all()
    matchb = MatchBooking.objects.all()
    return render(request, 'match_list_admin.html', {'matches': matches,'matchb': matchb})

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def add_match(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match added successfully.')
            return redirect(match_list_admin)
    else:
        form = MatchForm()
    return render(request, 'add_match.html', {'form': form})

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def edit_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            form.save()
            messages.success(request, 'Match updated successfully.')
            return redirect(match_list_admin)
    else:
        form = MatchForm(instance=match)
    return render(request, 'edit_match.html', {'form': form})

@login_required(login_url='adlogin')
@user_passes_test(is_admin)
def delete_match(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    if request.method == 'POST':
        match.delete()
        messages.success(request, 'Match deleted successfully.')
        return redirect(match_list_admin)
    return render(request, 'delete_match.html', {'match': match})




