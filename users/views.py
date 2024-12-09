from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm,TopUpForm
import requests
from django.conf import settings
from .models import Transaction

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created! You can now log in.")
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        recaptcha_response = request.POST.get("recaptcha-token")  # Updated
        # Verify reCAPTCHA
        data = {
            'secret': settings.RECAPTCHA_SECRET_KEY,
            'response': recaptcha_response,
            'remoteip': request.META.get('REMOTE_ADDR'),
        }
        recaptcha_verification = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=data
        )
        result = recaptcha_verification.json()
        # Check reCAPTCHA response
        if not result.get("success"):
            messages.error(request, "reCAPTCHA validation failed. Please try again.")
            return redirect("users:login")  # Redirect back to the login page
        # Authenticate user if reCAPTCHA is valid
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the next URL if provided, else default to user profile
            next_url = request.GET.get('next', reverse("users:user"))  # Simplified fallback
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "users/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "Successfully logged out.")
    return redirect('users:login')

def user_view(request):
    profile = request.user.profile  # Get the logged-in user's profile
    return render(request, 'users/user.html', {'balance': profile.balance})

@login_required(login_url='users:login') # Redirects the user to the login page if they are not logged in
def user(request):
    profile = request.user.profile # Gets the currently logged in users profile
    transactions = Transaction.objects.all().filter(user=request.user).order_by('-created_at') # Gets the queryset of all the transactions for the currently logged in user and sorts them by date
    return render(request, 'users/user.html', { # Renders the user.html template with the provided variables
        'user': request.user,
        'balance': profile.balance,
        'transactions': transactions
    })

@login_required
def top_up(request): # Logic for the top_up page
    profile = request.user.profile # Gets the currently logged in users profile
    if request.method == 'POST': # Checks if the form has been submitted
        form = TopUpForm(request.POST) # Creates the form for the user to interact with
        if form.is_valid(): # Checks if the form is valid
            amount = form.cleaned_data['amount'] # Gets the amount to top up from the form
            profile.balance += amount # Adds the amount to the users balance
            profile.save() # Saves the updated balance
            Transaction.objects.create(user=request.user, amount=amount, reason="Topped up balance") # Creates a transaction to show the top up
            messages.success(request, f"Your balance has been topped up by ${amount}.") # Provides feedback to the user that their balance has been topped up
            return redirect('users:user') # Redirects the user to the user page
    else:
        form = TopUpForm() # Creates the form for the user without a POST request
    context = { # Defines the variables that top_up.html has access to
        'form': form, 
        'user_balance': request.user.profile.balance,
        'welcome_message': f"Welcome back, {request.user.first_name}!",
    }
    return render(request, 'users/top_up.html', context) # Renders the top_up.html template with the provided variables from context