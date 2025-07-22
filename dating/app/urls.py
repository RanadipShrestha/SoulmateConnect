from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from . import views
urlpatterns = [
    path('', index, name="index"),
    path("register/", registerPage, name="register"),
    path('profiles/', profiles_view, name='profiles'),
    path('my_profile/', my_profile, name='my_profile'),
    path('messages/', views.conversations, name='conversations'),
    path('chat/<int:user_id>/', views.chat_view, name='chat_view'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path("login/", loginPage, name="login"),
    path('like/<int:user_id>/', views.like_user, name='like_user'),
    path('my-matches/', views.my_matches, name='my_matches'),
]