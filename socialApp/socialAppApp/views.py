from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
import requests

from .models import Community, Post


_FALLBACK_QUOTE = (
    "He who knows not, and knows not that he knows not, is a fool—shun him. "
    "He who knows not, and knows that he knows not, is a child—teach him. "
    "He who knows, and knows not that he knows, is asleep—wake him up. "
    "He who knows, and knows that he knows, is wise—follow him.",
    "Persian Proverb",
)

def _get_quote():
    result = cache.get('quote_of_the_day')
    if result:
        return result
    try:
        response = requests.get("https://zenquotes.io/api/today", timeout=5)
        data = response.json()
        result = (data[0]['q'], data[0]['a'])
    except Exception:
        return _FALLBACK_QUOTE
    cache.set('quote_of_the_day', result, timeout=86400)
    return result


#Homepage (requires login)
@login_required(login_url='login')
def homepage(request):
    quote, author = _get_quote()

    posts = Post.objects.select_related('author', 'community').order_by('-created_at')

    db_posts = [
        {
            'id':            p.pk,
            'community':     p.community.name,
            'communityKey':  p.community.key,
            'category':      p.category,
            'categoryLabel': p.get_category_display(),
            'author':        p.author.username,
            'time':          p.created_at.strftime('%b %d, %Y'),
            'timestamp':     p.created_at.isoformat(),
            'title':         p.title,
            'excerpt':       p.body,
            'votes':         p.votes,
            'comments':      0,
        }
        for p in posts
    ]

    db_communities = list(Community.objects.values('name', 'key').order_by('name'))

    return render(request, 'socialAppApp/index.html', {
        'quote':          quote,
        'author':         author,
        'db_posts':       db_posts,
        'db_communities': db_communities,
    })


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
    quote, author = _get_quote()
    return render(request, 'socialAppApp/quote.html', {'quote': quote, 'author': author})


@login_required(login_url='login')
def create_post(request):
    if request.method != 'POST':
        return redirect('homepage')

    title         = request.POST.get('title', '').strip()
    body          = request.POST.get('body', '').strip()
    category      = request.POST.get('category', '').strip()
    community_key = request.POST.get('community', '').strip()

    VALID_CATEGORIES = {'internship', 'event', 'rating', 'question', 'general'}
    if not title or not body or category not in VALID_CATEGORIES:
        messages.error(request, 'Please fill in all fields.')
        return redirect('homepage')

    try:
        community = Community.objects.get(key=community_key)
    except Community.DoesNotExist:
        messages.error(request, 'Invalid community selected.')
        return redirect('homepage')

    Post.objects.create(title=title, body=body, author=request.user,
                        community=community, category=category)
    return redirect('homepage')
