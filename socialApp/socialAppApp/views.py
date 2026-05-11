from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Count, Sum
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.utils import timezone
import requests

from .models import Community, Post, SavedPost, PostVote, Comment, UserCommunity, UserProfile, RegisteredCourse

_COMMUNITY_META = {
    'cs':          {'emoji': '💻', 'description': 'A space for CS students to share internship leads, get help with coursework, and talk about the tech industry.'},
    'business':    {'emoji': '💼', 'description': 'Connect with fellow business students on topics like finance, marketing, and career development.'},
    'engineering': {'emoji': '⚙️', 'description': 'A hub for engineering students across all disciplines to collaborate on projects and get help with coursework.'},
    'biology':     {'emoji': '🔬', 'description': 'For pre-med, research, and life science students navigating tough coursework and lab work.'},
}


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

    joined_ids        = list(request.user.joined_communities.values_list('community_id', flat=True))
    joined_communities = Community.objects.filter(id__in=joined_ids).order_by('name')

    posts = (Post.objects
             .filter(community_id__in=joined_ids)
             .select_related('author', 'community')
             .annotate(comment_count=Count('comments'))
             .order_by('-created_at'))

    saved_ids  = set(SavedPost.objects.filter(user=request.user).values_list('post_id', flat=True))
    user_votes = {v.post_id: v.value for v in PostVote.objects.filter(user=request.user)}

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
            'comments':      p.comment_count,
            'detailUrl':     f'/post/{p.pk}/',
            'saved':         p.pk in saved_ids,
            'voted':         user_votes.get(p.pk),
            'edited':        p.edited_at is not None,
        }
        for p in posts
    ]

    db_communities = [{'name': c.name, 'key': c.key} for c in joined_communities]

    return render(request, 'socialAppApp/index.html', {
        'quote':           quote,
        'author':          author,
        'db_posts':        db_posts,
        'db_communities':  db_communities,
        'has_communities': len(joined_ids) > 0,
    })


#Login
def login_view(request):
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
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == 'POST':
        username         = request.POST.get('username')
        first_name       = request.POST.get('first_name')
        last_name        = request.POST.get('last_name')
        email            = request.POST.get('email')
        password         = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "socialAppApp/register.html")

        if User.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken. Please choose another.')
            return render(request, 'socialAppApp/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with that email already exists.')
            return render(request, 'socialAppApp/register.html')

        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

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


@login_required(login_url='login')
def toggle_save(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    post = get_object_or_404(Post, pk=post_id)
    saved_obj, created = SavedPost.objects.get_or_create(user=request.user, post=post)
    if not created:
        saved_obj.delete()
        return JsonResponse({'saved': False})
    return JsonResponse({'saved': True})


@login_required(login_url='login')
def toggle_vote(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    direction = request.POST.get('direction')
    if direction not in ('up', 'down'):
        return JsonResponse({'error': 'Invalid direction'}, status=400)

    post = get_object_or_404(Post, pk=post_id)

    try:
        existing = PostVote.objects.get(user=request.user, post=post)
        if existing.value == direction:
            post.votes += -1 if direction == 'up' else 1
            existing.delete()
            voted = None
        else:
            post.votes += 2 if direction == 'up' else -2
            existing.value = direction
            existing.save()
            voted = direction
    except PostVote.DoesNotExist:
        PostVote.objects.create(user=request.user, post=post, value=direction)
        post.votes += 1 if direction == 'up' else -1
        voted = direction

    post.save()
    return JsonResponse({'votes': post.votes, 'voted': voted})


@login_required(login_url='login')
def saved_posts_view(request):
    posts = (Post.objects
             .filter(saved_by__user=request.user)
             .select_related('author', 'community')
             .order_by('-saved_by__saved_at'))
    return render(request, 'socialAppApp/saved_posts.html', {'posts': posts})


@login_required(login_url='login')
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    posts = (Post.objects
             .filter(author=request.user)
             .select_related('community')
             .annotate(comment_count=Count('comments'))
             .order_by('-created_at'))

    total_votes    = posts.aggregate(total=Sum('votes'))['total'] or 0
    total_comments = Comment.objects.filter(author=request.user).count()
    communities    = Community.objects.filter(members__user=request.user).order_by('name')
    courses        = RegisteredCourse.objects.filter(user=request.user)

    return render(request, 'socialAppApp/profile.html', {
        'profile':        profile,
        'posts':          posts,
        'total_votes':    total_votes,
        'total_comments': total_comments,
        'communities':    communities,
        'courses':        courses,
    })


@login_required(login_url='login')
def edit_profile(request):
    if request.method != 'POST':
        return redirect('profile')

    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    VALID_YEARS = {c[0] for c in UserProfile.YEAR_CHOICES}
    year = request.POST.get('year', '').strip()

    profile.major              = request.POST.get('major', '').strip()[:100]
    profile.year               = year if year in VALID_YEARS else ''
    profile.bio                = request.POST.get('bio', '').strip()[:500]
    profile.research_interests = request.POST.get('research_interests', '').strip()[:300]
    profile.linkedin           = request.POST.get('linkedin', '').strip()[:200]
    profile.github             = request.POST.get('github', '').strip()[:200]
    profile.save()

    first_name = request.POST.get('first_name', '').strip()[:30]
    last_name  = request.POST.get('last_name', '').strip()[:150]
    if first_name or last_name:
        request.user.first_name = first_name
        request.user.last_name  = last_name
        request.user.save(update_fields=['first_name', 'last_name'])

    new_password = request.POST.get('new_password', '').strip()
    if new_password:
        current_password = request.POST.get('current_password', '').strip()
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('profile')
        if new_password != request.POST.get('confirm_password', '').strip():
            messages.error(request, 'New passwords do not match.')
            return redirect('profile')
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)

    messages.success(request, 'Profile updated.')
    return redirect('profile')


@login_required(login_url='login')
def add_course(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    code     = request.POST.get('course_code', '').strip()[:20]
    name     = request.POST.get('course_name', '').strip()[:150]
    semester = request.POST.get('semester', '').strip()[:30]

    if not code or not name:
        return JsonResponse({'error': 'Course code and name are required.'}, status=400)

    _, created = RegisteredCourse.objects.get_or_create(
        user=request.user, course_code=code, semester=semester,
        defaults={'course_name': name},
    )
    if not created:
        return JsonResponse({'error': 'You already have that course this semester.'}, status=400)

    courses = list(
        RegisteredCourse.objects.filter(user=request.user)
        .values('id', 'course_code', 'course_name', 'semester')
    )
    return JsonResponse({'courses': courses})


@login_required(login_url='login')
def remove_course(request, course_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    course = get_object_or_404(RegisteredCourse, pk=course_id, user=request.user)
    course.delete()
    return JsonResponse({'deleted': True})


@login_required(login_url='login')
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    VALID_CATEGORIES = {'internship', 'event', 'rating', 'question', 'general'}
    if request.method == 'POST':
        title    = request.POST.get('title', '').strip()
        body     = request.POST.get('body', '').strip()
        category = request.POST.get('category', '').strip()
        if not title or not body or category not in VALID_CATEGORIES:
            messages.error(request, 'Please fill in all fields.')
        else:
            post.title     = title
            post.body      = body
            post.category  = category
            post.edited_at = timezone.now()
            post.save()
            return redirect('post_detail', post_id=post.pk)
    return render(request, 'socialAppApp/edit_post.html', {'post': post})


@login_required(login_url='login')
def delete_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    post = get_object_or_404(Post, pk=post_id, author=request.user)
    post.delete()
    return JsonResponse({'deleted': True})


@login_required(login_url='login')
def communities_list(request):
    joined_ids = set(request.user.joined_communities.values_list('community_id', flat=True))
    _ORDER = ['engineering', 'cs', 'biology', 'business']
    qs = sorted(
        Community.objects.annotate(
            post_count=Count('posts', distinct=True),
            member_count=Count('members', distinct=True),
        ),
        key=lambda c: _ORDER.index(c.key) if c.key in _ORDER else 99,
    )
    communities = []
    for c in qs:
        meta = _COMMUNITY_META.get(c.key, {'emoji': '🏛️', 'description': ''})
        communities.append({
            'key':          c.key,
            'name':         c.name,
            'emoji':        meta['emoji'],
            'description':  meta['description'],
            'post_count':   c.post_count,
            'member_count': c.member_count,
            'is_joined':    c.pk in joined_ids,
        })
    return render(request, 'socialAppApp/communities.html', {'communities': communities})


@login_required(login_url='login')
def toggle_join(request, key):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    community = get_object_or_404(Community, key=key)
    obj, created = UserCommunity.objects.get_or_create(user=request.user, community=community)
    if not created:
        obj.delete()
        return JsonResponse({'joined': False})
    return JsonResponse({'joined': True})


@login_required(login_url='login')
def community_detail(request, key):
    community = get_object_or_404(Community, key=key)
    posts = (Post.objects
             .filter(community=community)
             .select_related('author', 'community')
             .annotate(comment_count=Count('comments'))
             .order_by('-created_at'))
    return render(request, 'socialAppApp/community_feed.html', {
        'community': community,
        'posts':     posts,
    })


@login_required(login_url='login')
def post_detail(request, post_id):
    post     = get_object_or_404(Post, pk=post_id)
    comments = post.comments.select_related('author').order_by('created_at')
    return render(request, 'socialAppApp/post_detail.html', {
        'post':     post,
        'comments': comments,
    })


@login_required(login_url='login')
def add_comment(request, post_id):
    if request.method != 'POST':
        return redirect('post_detail', post_id=post_id)
    post = get_object_or_404(Post, pk=post_id)
    body = request.POST.get('body', '').strip()
    if body:
        Comment.objects.create(body=body, author=request.user, post=post)
    return redirect('post_detail', post_id=post_id)


@login_required(login_url='login')
def delete_comment(request, comment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    comment = get_object_or_404(Comment, pk=comment_id, author=request.user)
    comment.delete()
    return JsonResponse({'deleted': True})
