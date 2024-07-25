from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login,logout,authenticate,login as auth_login
from django.contrib.auth.decorators import login_required
from .models import Profile,Booking,Match,MatchBooking
from .forms import Addprofile,BookingForm,PaymentForm,MatchPaymentForm
from django.core.mail import send_mail
from datetime import datetime,timedelta,time
from django.conf import settings
from django.utils import timezone
import pytz
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.core.exceptions import MultipleObjectsReturned
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.urls import reverse
import razorpay
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# @login_required(login_url='logout')
def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile  # Ensure profile is created
            profile.phone_no = form.cleaned_data['phone_no']
            profile.save()
            return redirect(loginpage) #redirect to loginpage
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})



def loginpage(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')
        user = authenticate(username=username_or_email, password=password)
        if not username_or_email or not password:
            messages.error(request, 'Username/email and password are required.')
            return redirect('login')

        # Try to authenticate using username
        user = authenticate(username=username_or_email, password=password)
        
        if user is None:
            # If username-based authentication fails, try email-based authentication
            try:
                user = User.objects.get(email=username_or_email)
                if User.check_password(password):
                    user = authenticate(username=user.username, password=password)
            except User.DoesNotExist:
                user = None
            except MultipleObjectsReturned:
                messages.error(request, 'Multiple accounts found with this email address.')
                return redirect('login')
        
        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Redirect to your desired post-login page
        else:
            messages.error(request, 'Invalid username/email or password.')

    return render(request,'login.html')

def logoutpage(request):
    logout(request)
    return redirect(loginpage) 

@login_required(login_url='logout')
def profilepage(request):
    usr=request.user
    try:
        pro = Profile.objects.get(user=usr)
    except Profile.DoesNotExist:
        pro = None
        print('profile not exist')
    return render(request,'profile.html',{'pro':pro})


@login_required(login_url='logout')
def updateprofile(request):
    usr=request.user
    print(usr)
    pro=Profile.objects.get(user=usr)
    if request.method=='POST':
        form=Addprofile(request.POST,request.FILES,instance=pro)
        if form.is_valid():
            a=form.save(commit=False)
            a.user=request.user
            a.save()
            return redirect(profilepage)
    else:
        form=Addprofile(instance=pro)
    return render(request,'pro_update.html',{'form':form})

@login_required(login_url='logout')
def book_slot(request):
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            total_hours = form.cleaned_data['total_hours']
            if total_hours <= 0:
                form.add_error('total_hours', 'You must book for at least one hour.')
            else:
                # Use the converted start time from the hidden input field
                start_time_str = request.POST.get('start_time_24')
                start_time = datetime.strptime(start_time_str, '%H:%M:%S').time()
                date = form.cleaned_data['date']

                # Combine date and start time, and make it timezone-aware for IST
                ist = pytz.timezone('Asia/Kolkata')
                booking_datetime = datetime.combine(date, start_time)
                booking_datetime = ist.localize(booking_datetime)

               # Get the current datetime in IST and one hour from now
                current_datetime = timezone.now().astimezone(ist)
                one_hour_from_now = current_datetime + timedelta(hours=1)

                if booking_datetime <= current_datetime:
                    form.add_error('start_time', 'The selected time has already passed. Please choose a future time.')
                elif booking_datetime < one_hour_from_now:
                    form.add_error('start_time', 'You can only book the turf at least one hour in advance.')
                else:
                    end_time = calculate_end_time(start_time, total_hours)
                    # Calculate the total booked hours for the user on the selected date
                    user_bookings = Booking.objects.filter(user=request.user, date=date)
                    user_total_hours = sum(booking.total_hours for booking in user_bookings)
                
                    if user_total_hours + total_hours > 12:
                        form.add_error(None, 'You cannot book more than 12 hours in a single day.')
                    elif not Booking.is_slot_available(date, start_time, end_time):
                        form.add_error(None, 'The selected time slot is already booked. Please choose another slot.')
                        # Check if the slot is available
                    else:
                        total_price = calculate_price(start_time,end_time)
                        # Pass the booking data to the payment view, converting date and time to strings
                        request.session['booking_data'] = {
                            'date': date.strftime('%Y-%m-%d'),
                            'start_time': start_time.strftime('%H:%M:%S'),
                            'end_time': end_time.strftime('%H:%M:%S'),
                            'total_hours': total_hours,
                            'total_price': total_price,
                        }
                        return redirect('payment')
    else:
        form = BookingForm()
    
    return render(request, 'book_slot.html', {'form': form})



@login_required(login_url='logout')
def payment(request):
    if 'booking_data' not in request.session:
        return redirect('book_slot')

    booking_data = request.session['booking_data']
    date = datetime.strptime(booking_data['date'], '%Y-%m-%d').date()
    start_time = datetime.strptime(booking_data['start_time'], '%H:%M:%S').time()
    end_time = datetime.strptime(booking_data['end_time'], '%H:%M:%S').time()

    if request.method == 'POST':
        if 'cancel' in request.POST:
            # If the user clicks cancel, clear the session and redirect
            del request.session['booking_data']
            messages.info(request, "Your booking has been cancelled.")
            return redirect('book_slot')
        
        form = PaymentForm(request.POST)
        if form.is_valid():
            print(f"Total price submitted: {form.cleaned_data['total_price']}")
            payment_method = form.cleaned_data['payment_method']
            print(f"Form data: {form.cleaned_data}")
            
            if payment_method == 'cod':
                # Handle COD booking
                booking = Booking.objects.create(
                    user=request.user,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    total_hours=booking_data['total_hours'],
                    total_price=booking_data['total_price'],
                    payment_status=False,  # Payment not received yet
                    payment_method='COD'
                )
                del request.session['booking_data']
                send_confirmation_email(request.user.email, booking)
                messages.success(request, "Your COD booking has been confirmed.")
                # Store booking ID in the session
                request.session['booking_id'] = booking.id
                return redirect(cod_booking_complete)
            
            elif payment_method == 'razorpay':
                # Create Razorpay order
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                order_amount = int(float(booking_data['total_price']) * 100)  # Amount in paise
                order_currency = 'INR'
                order_receipt = f"booking_{request.user.id}_{date}_{start_time}"
                razorpay_order = client.order.create(
                    {'amount': order_amount, 'currency': order_currency, 'receipt': order_receipt}
                )
                request.session['razorpay_order_id'] = razorpay_order['id']
                return render(request, 'razorpay_payment.html', {
                    'razorpay_key': settings.RAZORPAY_KEY_ID,
                    'order_id': razorpay_order['id'],
                    'amount': order_amount,
                    'currency': order_currency,
                    'booking_data': booking_data,
                })
        else:
            print(f"Form errors: {form.errors}")
        
    else:
        form = PaymentForm(initial={'total_price': booking_data['total_price']})

    return render(request, 'payment.html', {'form': form, 'booking_data': booking_data})

@login_required(login_url='logout')
def cod_booking_complete(request):
    # Retrieve the booking ID from the session
    booking_id = request.session.get('booking_id')
    
    if booking_id:
        booking = Booking.objects.get(id=booking_id)
        del request.session['booking_id']  # Clear the booking ID from the session
        return render(request, 'cod_booking_complete.html', {'booking': booking})
    else:
        messages.error(request, "No booking data found.")
        return redirect('book_slot')


@csrf_exempt
def razorpay_callback(request):
    if request.method == 'POST':
        razorpay_order_id = request.POST.get('razorpay_order_id')
        razorpay_payment_id = request.POST.get('razorpay_payment_id')
        razorpay_signature = request.POST.get('razorpay_signature')

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        try:
            client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })

            # Payment is successful, update the booking
            booking_data = request.session.get('booking_data', {})
            date = datetime.strptime(booking_data['date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(booking_data['start_time'], '%H:%M:%S').time()
            end_time = datetime.strptime(booking_data['end_time'], '%H:%M:%S').time()

            booking = Booking.objects.create(
                user=request.user,
                date=date,
                start_time=start_time,
                end_time=end_time,
                total_hours=booking_data['total_hours'],
                total_price=booking_data['total_price'],
                payment_status=True,  # Payment received
                payment_method='Razorpay'
            )

            # Clear session booking data
            del request.session['booking_data']
            send_confirmation_email(request.user.email, booking)

            messages.success(request, "Your payment was successful. Your booking is confirmed.")
            return render(request, 'booking_complete.html', {'booking': booking})
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed. Please try again.")
            return redirect('payment_failed')
    else:
        return redirect('payment_failed')


def calculate_end_time(start_time, total_hours):   
    return (datetime.combine(datetime.today(), start_time) + timedelta(hours=total_hours)).time()

def calculate_price(start_time, end_time):
    # Define hourly rates
    rate_day = 1000  # Rate from 6 AM to Midnight
    rate_night = 1300  # Rate from Midnight to 6 AM
    
    # Convert start_time and end_time to datetime objects for easier manipulation
    now = datetime.now()
    start_datetime = datetime.combine(now.date(), start_time)
    end_datetime = datetime.combine(now.date(), end_time)
    
    # If end time is before start time, assume booking spans to the next day
    if end_datetime <= start_datetime:
        end_datetime += timedelta(days=1)
    
    total_price = 0
    current_time = start_datetime
    
    while current_time < end_datetime:
        # Determine whether the current hour falls within the day or night rate period
        if 6 <= current_time.hour < 24:
            total_price += rate_day
        else:
            total_price += rate_night
        
        # Move to the next hour
        current_time += timedelta(hours=1)
    
    return total_price

# Example usage
start_time = datetime.strptime('22:00:00', '%H:%M:%S').time()  # 10 PM
end_time = datetime.strptime('23:00:00', '%H:%M:%S').time()    # 11 PM

price = calculate_price(start_time, end_time)
print(f"Total Price: {price}")

def send_confirmation_email(email, booking):
    # Convert booking times to IST
    ist = pytz.timezone('Asia/Kolkata')
    start_time_ist = datetime.combine(booking.date, booking.start_time).astimezone(ist).strftime('%I:%M %p')
    end_time_ist = datetime.combine(booking.date, booking.end_time).astimezone(ist).strftime('%I:%M %p')

    subject = 'Booking Confirmation'
    message = (
        f"Dear {booking.user.first_name},\n\n"
        f"Your slot booking for Sports Land turf on {booking.date} has been successfully booked.\n\n"
        f"Time: from {start_time_ist} to {end_time_ist}\n\n"
        f"Thank you for choosing Sports Land. We look forward to seeing you!\n\n"
        f"Best regards,\n"
        f"Sports Land Team"
    )
    from_email = 'sportsland20242gmail.com'
    send_mail(subject, message,from_email,[email])

@login_required(login_url='logout')
def payment_cancelled(request):
    # Remove the booking data from the session
    if 'booking_data' in request.session:
        del request.session['booking_data']
    
    # Add a message to inform the user
    messages.info(request, "Your payment was cancelled. Feel free to book again when you're ready.")
    
    # Render the payment cancelled template
    return render(request, 'payment_cancelled.html')

@login_required(login_url='logout')
def payment_failed(request):
    # Retrieve the booking data from the session
    booking_data = request.session.get('booking_data', {})
    
    # Remove the booking data from the session
    if 'booking_data' in request.session:
        del request.session['booking_data']
    
    # Add a message to inform the user
    messages.error(request, "We're sorry, but your payment failed. Please try again or choose a different payment method.")
    
    # Render the payment failed template with the booking data
    return render(request, 'payment_failed.html', {'booking_data': booking_data})

@login_required(login_url='logout')
def booking_history(request):
    user = request.user
    bookings = Booking.objects.filter(user=user).order_by('-date','-start_time')
    return render(request, 'booking_history.html', {'bookings': bookings})

@login_required(login_url='logout')
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    # Check if cancellation is within one hour
     # Set timezone to IST
    ist = pytz.timezone('Asia/Kolkata')
    current_time = timezone.now().astimezone(ist)
    one_hour_limit = booking.booking_time.astimezone(ist) + timedelta(hours=1)

    if current_time <= one_hour_limit:
        booking.delete()  # Remove the booking
        messages.success(request, 'Your booking has been successfully canceled.')
    else:
        messages.error(request, 'You can only cancel your booking within one hour of making it.')

    return redirect('booking_history')

@login_required(login_url='logout')
def confirm_cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        return redirect('cancel_booking', booking_id=booking_id)

    return render(request, 'confirm_cancel_booking.html', {'booking': booking})

@login_required(login_url='logout')
def match_list(request):
    matches = Match.objects.all()
    user_bookings = MatchBooking.objects.filter(player=request.user).values_list('match_id', flat=True)
    for match in matches:
        match.user_has_booked = match.id in user_bookings
        match.players_booked = match.bookings.count()  # Count the number of players booked
    return render(request, 'match_list.html', {'matches': matches})

@login_required(login_url='logout')
def book_match(request, id):
    match = get_object_or_404(Match, id=id)
    if match.bookings.filter(player=request.user).exists():
        return render(request, 'already_booked.html', {'match': match})
    if match.bookings.count() < match.max_players:
        return redirect(match_payment, id=id)
    else:
        return render(request, 'match_full.html', {'match': match})
    


@login_required(login_url='logout')
def match_payment(request, id):
    match = get_object_or_404(Match, id=id)
    amount = match.amount  # Use the amount from the match

    if request.method == 'POST':
        if 'cancel' in request.POST:
            # Handle cancellation
            return redirect('match_list')

        form = MatchPaymentForm(request.POST)
        if form.is_valid():
            payment_method = form.cleaned_data.get('payment_method')
            
            if payment_method == 'COD':
                # Handle Cash on Delivery
                MatchBooking.objects.create(match=match, player=request.user)
                return redirect('booking_success', id=match.id)

            elif payment_method == 'Razorpay':
                # Handle Razorpay payment
                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

                try:

                    # Create a new Razorpay order
                    order_data = {
                        'amount': int(amount * 100),  # amount in paise (e.g., 100 INR = 10000 paise)
                        'currency': 'INR',  # Ensure this is a supported currency
                        'payment_capture': '1'  # auto-capture payment
                    }
                    order = client.order.create(data=order_data)

                    # Store order details in session to handle post-payment
                    request.session['order_id'] = order['id']
                    request.session['match_id'] = match.id
                    request.session['player_id'] = request.user.id

                    # Render Razorpay payment page with order details
                    return render(request, 'razorpay_payment.html', {
                        'amount': amount,
                        'order_id': order['id'],
                        'razorpay_key': 'settings.RAZORPAY_KEY_ID'
                    })
                except razorpay.errors.RazorpayError as e:
                    return render(request, 'payment_failure.html', {'message': 'Payment processing failed. Please try again.'})

    else:
        form = MatchPaymentForm()

    return render(request, 'match_payment.html', {'match': match, 'amount': amount, 'form': form})


def payment_success(request):
    # Fetch Razorpay keys from settings
    razorpay_key = settings.RAZORPAY_KEY
    razorpay_secret = settings.RAZORPAY_SECRET

    # Initialize Razorpay client
    client = razorpay.Client(auth=(razorpay_key, razorpay_secret))

    # Retrieve the order ID and payment ID from request
    order_id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    
    # Fetch session data
    match_id = request.session.get('match_id')
    player_id = request.session.get('player_id')

    # Verify the payment
    if order_id and payment_id:
        try:
            # Fetch payment details from Razorpay
            payment = client.payment.fetch(payment_id)
            if payment['status'] == 'captured':
                # Payment is successful
                match = get_object_or_404(Match, id=match_id)
                MatchBooking.objects.create(match=match, player_id=player_id)

                # Clear session data
                request.session.pop('order_id', None)
                request.session.pop('match_id', None)
                request.session.pop('player_id', None)

                return render(request, 'match_payment_success.html', {'message': 'Payment successful!'})
            else:
                # Payment failed
                return render(request, 'match_payment_failure.html', {'message': 'Payment failed. Please try again.'})
        except razorpay.errors.RazorpayError as e:
            # Handle Razorpay errors
            return render(request, 'match_payment_failure.html', {'message': 'Payment verification failed. Please try again.'})

    return render(request, 'match_payment_failure.html', {'message': 'Invalid payment details.'})

# def send_confirmation_email_match(email, match):
#     subject = 'Booking Confirmation'
#     message = (
#         f'Your slot for the match on {match.date} has been successfully booked. \n\n'
#         f'Sport: {match.match.sport}\n'
#         f'Time: {match.match.start_time} to {match.match.end_time}\n\n'
#         f'Thank you for choosing Sports Land.\n'
#         f'Best regards,\nSports Land'
#     )
#     send_mail(subject, message, 'sportsland20242gmail.com', [email])




@login_required(login_url='logout')
def booking_success(request,id):
    match = get_object_or_404(Match, id=id)
    return render(request, 'booking_success.html',{'match': match})