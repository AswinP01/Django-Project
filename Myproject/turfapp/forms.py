
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile,Booking
from django.core.exceptions import ValidationError

class RegisterForm(UserCreationForm):
    first_name=forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control forminp','placeholder':'First name'}
    ))
    last_name=forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control forminp','placeholder':'Last name'}
    ))
    email=forms.EmailField(widget=forms.EmailInput(
        attrs={'class':'form-control forminp','placeholder':'Email'}
    ))
    username=forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control forminp','placeholder':'User name'}
    ))
    phone_no=forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control forminp','placeholder':'Phone number'}
    ))
    password1=forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
        attrs={'class':'form-control forminp','placeholder':'Password'}
    ))
    password2=forms.CharField(
        label="Confirm Password", 
        widget=forms.PasswordInput(
        attrs={'class':'form-control forminp','placeholder':'Renter Password'}
    ))

    class Meta:
        model = User
        fields=['username','email','first_name','last_name','phone_no']

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        # Check for unique username
        if User.objects.filter(username=username).exists():
            raise ValidationError('Username already exists.')

        # Check for unique email
        if User.objects.filter(email=email).exists():
            raise ValidationError('Email already exists.')

        # Check that password and confirm_password match
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise ValidationError('Passwords do not match.')

        return cleaned_data


class Addprofile(forms.ModelForm):
    first_name=forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control forminp','placeholder':'First name'}
    ))
    last_name=forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control forminp','placeholder':'Last name'}
    ))
    full_name=forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control forminp','placeholder':'Full name'}
    ))
    email=forms.EmailField(widget=forms.EmailInput(
        attrs={'class':'form-control forminp','placeholder':'Email'}
    ))
    phone_no=forms.CharField(widget=forms.TextInput(
        attrs={'class':'form-control forminp','placeholder':'Phone number'}
    ))
    image=forms.ImageField(widget=forms.ClearableFileInput(
        attrs={'class':'form-control forminp','placeholder':'Image'}
    ))
    class Meta:
        model=Profile
        fields=['image','first_name','last_name','full_name','email','phone_no']

class BookingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'class': 'form-control', 'id': 'datepicker', 'placeholder': 'Date'}
        )
    )
    time_choices = []
    for hour in range(24):
        period = 'AM' if hour < 12 else 'PM'
        display_hour = hour if hour <= 12 else hour - 12
        display_hour = 12 if display_hour == 0 else display_hour
        time_str = f'{display_hour:02d}:00 {period}'
        time_24 = f'{hour:02d}:00'
        time_choices.append((time_24, time_str))
    
    start_time = forms.ChoiceField(
        choices=time_choices,widget=forms.Select(
            attrs={'class': 'form-control'}
            )
    )        
    total_hours = forms.IntegerField(
        min_value=1, max_value=12,widget=forms.NumberInput(
            attrs={'class': ''})
            )  # Set max_value to 12

    class Meta:
        model = Booking
        fields = ['date', 'start_time', 'total_hours']
        
class PaymentForm(forms.Form):
    PAYMENT_CHOICES = [
        ('razorpay', 'Pay Online (Razorpay)'),
        ('cod', 'Pay on Arrival')
    ]
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect,
        label="Payment Method"  # Set label for the ChoiceField
    )
    total_price = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        widget=forms.HiddenInput(),
        label="Total Price"  # Set label for the hidden field (not displayed)
    )
class MatchPaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('Razorpay', 'Pay with Razorpay'),
    ]
    
    payment_method = forms.ChoiceField(choices=PAYMENT_METHOD_CHOICES, widget=forms.RadioSelect)