from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile,Transaction

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    surname = forms.CharField(max_length=30, required=True)
    nickname = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'surname', 'nickname']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['surname']       
        if commit:
            user.save()
            profile = user.profile
            profile.first_name = self.cleaned_data['first_name']
            profile.surname = self.cleaned_data['surname']
            profile.nickname = self.cleaned_data['nickname']
            profile.save()
        return user

class TopUpForm(forms.Form):
    amount = forms.DecimalField(min_value=0.00, # Creates the field for the user to enter the amount they want to top up, ensuring it is greater than $0.00
                                decimal_places=2, # Ensures the amount entered is to 2 decimal places
                                max_digits=5, # Ensures the amount entered is to 5 digits
                                error_messages={ # Provides error messages to the user based on what they have entered
                                    'min_value': "Please enter an amount greater than $0.00.",
                                    'invalid': "Enter a valid amount in dollars and cents."}, 
                                label="Amount to Top-Up") # Sets the label for the field

    class Meta: # Sets the model and fields for the form
        model = Transaction
        fields = ['amount']