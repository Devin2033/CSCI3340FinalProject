from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests


#Homepage (requires login)
@login_required(login_url='login')
def homepage(request):
    try:
        url = "https://zenquotes.io/api/today"
        response = requests.get(url)
        data = response.json()
        quote = data[0]['q']
        author = data[0]['a']
    except:
        #in case API is down
        quote = "He who knows not, and knows not that he knows not, is a fool—shun him. He who knows not, and knows that he knows not, is a child—teach him. He who knows, and knows not that he knows, is asleep—wake him up. He who knows, and knows that he knows, is wise—follow him."
        author = "Persian Proverb"
        # context = {
        
        #     'quote':quote,
        #     'author':author,
        #     #'posts
        # }
    return render(request, 'socialAppApp/index.html',{'quote':quote,'author':author})


#Login
def login_view(request):
    # If already logged in, go straight to homepage
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'socialAppApp/login.html')


#Register
def register_view(request):
    # If already logged in, go straight to homepage
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == 'POST':
        username   = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name  = request.POST.get('last_name')
        email      = request.POST.get('email')
        password   = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        #Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "socialAppApp/register.html")

        #Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken. Please choose another.')
            return render(request, 'socialAppApp/register.html')

        #Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with that email already exists.')
            return render(request, 'socialAppApp/register.html')

        #Create the user
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        #Log them in automatically after registering
        login(request, user)
        return redirect('homepage')

    return render(request, 'socialAppApp/register.html')


#Logout
def logout_view(request):
    logout(request)
    return redirect('login')

def quote_view(request):
    try:
        url = "https://zenquotes.io/api/today"
        response = requests.get(url)
        data = response.json()
        quote = data[0]['q']
        author = data[0]['a']
    except:
        #in case API is down
        quote = "He who knows not, and knows not that he knows not, is a fool—shun him. He who knows not, and knows that he knows not, is a child—teach him. He who knows, and knows not that he knows, is asleep—wake him up. He who knows, and knows that he knows, is wise—follow him."
        author = "Persian Proverb"
    
    return render(request, 'socialAppApp/quote.html',
        {
            'quote':quote,
            'author':author
        })