from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *
from . import views
urlpatterns = [
    path('profiles/', profiles_view, name='profiles'),
    path('my_profile/', my_profile, name='my_profile'),
    path('matches/', views.my_matches, name='my_matches'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('like/<int:user_id>/', views.like_user, name='like_user'),
    path('my-matches/', views.my_matches, name='my_matches'),
    path("matches/", views.my_matches, name="my_matches"),
    path('accept-request/<int:request_id>/', views.accept_request, name='accept_request'),
    path('decline-request/<int:request_id>/', views.decline_request, name='decline_request'),
    path('remove-match/<int:user_id>/', views.remove_match, name='remove_match'),

]