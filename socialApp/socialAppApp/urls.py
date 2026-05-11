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
]
