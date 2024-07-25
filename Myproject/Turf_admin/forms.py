from django import forms
from django.contrib.auth.models import User
from turfapp.models import Booking,Match
from django.core.exceptions import ValidationError


class UserForm(forms.ModelForm):
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

    class Meta:
        model = User
        fields=['username','email','first_name','last_name','phone_no']
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        # Check for unique username
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Username already exists.')

        # Check for unique email
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Email already exists.')

        return cleaned_data

class MatchForm(forms.ModelForm):
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
    end_time = forms.ChoiceField(
        choices=time_choices,widget=forms.Select(
            attrs={'class': 'form-control'}
            )
    )
    class Meta:
        model = Match
        fields = ['date', 'start_time', 'end_time','sport_type','max_players', 'amount'] 