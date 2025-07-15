from django.shortcuts import render, redirect
from .forms import UserCreateForm
from .models import userDetails, Contact
from django.contrib.auth import authenticate, login
from django.contrib import messages
# Create your views here.

def index(request):
    return render(request, 'index.html')

def registerPage(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST, request.FILES)  # Include request.FILES for profile pic
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.email = request.POST.get("email")
            user.username = request.POST.get("username")
            user.save()

            # Save additional user details
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

def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Invalide username or password")
    return render(request, 'login.html')


def matching_page(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login page if user not logged in
    
    profiles = userDetails.objects.exclude(user=request.user)
    return render(request, 'match.html', {'matching_profiles': profiles})

def message(request):
    
    return render(request, 'message.html')

def aboutUs(request):
    return render(request, "aboutus.html")

def contactUs(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        Contact.objects.create(name=name, email=email, subject=subject, message=message)

        return redirect('conatctus')
    return render(request, "contact.html")