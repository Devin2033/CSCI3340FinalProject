from django.db import models
from django.contrib.auth.models import User


class Community(models.Model):
    name = models.CharField(max_length=100)
    key  = models.SlugField(unique=True)

    def __str__(self): return self.name

    class Meta:
        verbose_name_plural = 'communities'
        ordering = ['name']


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('internship', 'Internship'),
        ('event',      'Event'),
        ('rating',     'Prof Rating'),
        ('question',   'Question'),
        ('general',    'General'),
    ]

    title      = models.CharField(max_length=300)
    body       = models.TextField()
    author     = models.ForeignKey(User,      on_delete=models.CASCADE, related_name='posts')
    community  = models.ForeignKey(Community, on_delete=models.CASCADE, related_name='posts')
    category   = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    votes      = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at  = models.DateTimeField(null=True, blank=True)

    def __str__(self): return self.title

    class Meta:
        ordering = ['-created_at']


class SavedPost(models.Model):
    user     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post     = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')


class PostVote(models.Model):
    VOTE_CHOICES = [('up', 'Up'), ('down', 'Down')]
    user  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    post  = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='user_votes')
    value = models.CharField(max_length=4, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('user', 'post')


class UserProfile(models.Model):
    YEAR_CHOICES = [
        ('freshman',  'Freshman'),
        ('sophomore', 'Sophomore'),
        ('junior',    'Junior'),
        ('senior',    'Senior'),
        ('graduate',  'Graduate'),
        ('phd',       'PhD'),
        ('other',     'Other'),
    ]

    user               = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    major              = models.CharField(max_length=100, blank=True)
    year               = models.CharField(max_length=20, choices=YEAR_CHOICES, blank=True)
    bio                = models.TextField(max_length=500, blank=True)
    research_interests = models.CharField(max_length=300, blank=True)
    linkedin           = models.URLField(blank=True)
    github             = models.URLField(blank=True)

    def __str__(self): return f'{self.user.username} profile'


class RegisteredCourse(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    course_code = models.CharField(max_length=20)
    course_name = models.CharField(max_length=150)
    semester    = models.CharField(max_length=30, blank=True)
    added_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['course_code']
        unique_together = ('user', 'course_code', 'semester')
