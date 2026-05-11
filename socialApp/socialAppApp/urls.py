from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('quote/', views.quote_view, name='quote_of_the_day'),
    path('create-post/', views.create_post, name='create_post'),
    path('saved/', views.saved_posts_view, name='saved_posts'),
    path('post/<int:post_id>/save/', views.toggle_save, name='toggle_save'),
    path('post/<int:post_id>/vote/', views.toggle_vote, name='toggle_vote'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/courses/add/', views.add_course, name='add_course'),
    path('profile/courses/<int:course_id>/remove/', views.remove_course, name='remove_course'),
    path('communities/', views.communities_list, name='communities'),
    path('community/<slug:key>/', views.community_detail, name='community_detail'),
    path('community/<slug:key>/join/', views.toggle_join, name='toggle_join'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]
