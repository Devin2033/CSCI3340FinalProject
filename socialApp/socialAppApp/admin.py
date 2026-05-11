from django.contrib import admin
from .models import Community, Post, SavedPost, Comment, UserCommunity, PostVote, UserProfile, RegisteredCourse


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'key')
    prepopulated_fields = {'key': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display    = ('title', 'author', 'community', 'category', 'votes', 'created_at')
    list_filter     = ('community', 'category')
    search_fields   = ('title', 'body', 'author__username')
    readonly_fields = ('created_at',)


@admin.register(SavedPost)
class SavedPostAdmin(admin.ModelAdmin):
    list_display    = ('user', 'post', 'saved_at')
    readonly_fields = ('saved_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display    = ('author', 'post', 'created_at')
    search_fields   = ('body', 'author__username')
    readonly_fields = ('created_at',)


@admin.register(UserCommunity)
class UserCommunityAdmin(admin.ModelAdmin):
    list_display    = ('user', 'community', 'joined_at')
    list_filter     = ('community',)
    readonly_fields = ('joined_at',)


@admin.register(PostVote)
class PostVoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'value')
    list_filter  = ('value',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'major', 'year')
    search_fields = ('user__username', 'major')
    list_filter   = ('year',)


@admin.register(RegisteredCourse)
class RegisteredCourseAdmin(admin.ModelAdmin):
    list_display  = ('user', 'course_code', 'course_name', 'semester')
    search_fields = ('user__username', 'course_code', 'course_name')
    list_filter   = ('semester',)
