from django.shortcuts import render, redirect
from .forms import UserCreateForm
from .models import userDetails, Contact, FAQ, Home
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def index(request):
    homes = Home.objects.all()
    context ={
        'homes':homes
    }
    return render(request, 'index.html',context)

# def registerPage(request):
#     if request.method == "POST":
#         form = UserCreateForm(request.POST, request.FILES)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user.first_name = request.POST.get("first_name")
#             user.last_name = request.POST.get("last_name")
#             user.email = request.POST.get("email")
#             user.username = request.POST.get("username")
#             user.save()

#             bio = request.POST.get("bio")
#             dob = request.POST.get("dob")
#             profile = request.FILES.get("profile")
#             city = request.POST.get("city")
#             occupation = request.POST.get("occupation")
#             education = request.POST.get("education")
#             hobbies = request.POST.get("hobbies")
#             gender = request.POST.get("gender")

#             userDetails.objects.create(
#                 user=user,
#                 bio=bio,
#                 dob=dob,
#                 profile=profile,
#                 city=city,
#                 occupation=occupation,
#                 education=education,
#                 hobbies=hobbies,
#                 gender=gender
#             )
#             return redirect('login') 
#     else:
#         form = UserCreateForm()
#     return render(request, 'register.html', {"form": form})

from django.contrib import messages
from django.contrib.auth.models import User

def registerPage(request):
    if request.method == "POST":
        username = request.POST.get("username")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another one.")
            return render(request, 'register.html')

        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.email = request.POST.get("email")
            user.username = username
            user.save()

            bio = request.POST.get("bio")
            dob = request.POST.get("dob")
            profile = request.FILES.get("profile")
            city = request.POST.get("city")
            occupation = request.POST.get("occupation")
            education = request.POST.get("education")
            hobbies = request.POST.get("hobbies")
            gender = request.POST.get("gender")

            userDetails.objects.create(
                user=user,
                bio=bio,
                dob=dob,
                profile=profile,
                city=city,
                occupation=occupation,
                education=education,
                hobbies=hobbies,
                gender=gender
            )
            return redirect('login')
    else:
        form = UserCreateForm()
    return render(request, 'register.html', {"form": form})

from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect

def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            # Always show same message to avoid revealing if username exists
            messages.error(request, "Incorrect username or password")
            return render(request, 'login.html', {"username": username})

    return render(request, 'login.html')


def matching_page(request):
    if not request.user.is_authenticated:
        return redirect('login')  
    
    profiles = userDetails.objects.exclude(user=request.user)
    return render(request, 'match.html', {'matching_profiles': profiles})

@login_required
def message(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'message.html', {'users': users})

def aboutUs(request):
    return render(request, "aboutus.html")

def contactUs(request):
    faqs = FAQ.objects.all()
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        Contact.objects.create(name=name, email=email, subject=subject, message=message)
        return redirect('conatctus')
    context={
        "faqs": faqs 
    }
    return render(request, "contact.html", context)



from .models import Message
from django.db import models
@login_required
def chat_room(request, receiver_id):
    receiver = User.objects.get(id=receiver_id)
    messages = Message.objects.filter(
        models.Q(sender=request.user, receiver=receiver) |
        models.Q(sender=receiver, receiver=request.user)
    ).order_by('timestamp')
    return render(request, 'chat_room.html', {
        'receiver': receiver,
        'messages': messages,
        'users': User.objects.exclude(id=request.user.id),  # For sidebar
    })