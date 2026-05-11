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
