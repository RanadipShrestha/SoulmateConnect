from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
urlpatterns = [
    path('', index, name="index"),
    path("register/", registerPage, name="register"),
    path('profiles/', profiles_view, name='profiles'),
    path('my_profile/', my_profile, name='my_profile'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path("login/", loginPage, name="login"),
]