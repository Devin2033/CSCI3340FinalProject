from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages


#Homepage (requires login)
@login_required(login_url='login')
def homepage(request):
    return render(request, 'socialAppApp/index.html')


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
