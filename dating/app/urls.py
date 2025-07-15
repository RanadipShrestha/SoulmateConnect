from django.urls import path
from .views import *
urlpatterns = [
    path('', index, name="index"),
    path("register/", registerPage, name="register"),
    path("login/", loginPage, name="login"),
    path("aboutus/", aboutUs, name="aboutus"),
    path("match/",  matching_page, name="match"),
    path("message/", message, name="message"),
    path("conatctus/", contactUs, name="conatctus")
]