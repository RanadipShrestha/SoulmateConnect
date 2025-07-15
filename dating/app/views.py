from django.shortcuts import render, redirect
from .forms import UserCreateForm
from .models import UserDetails
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .forms import UserDetailsEditForm, ProfileEditForm


@require_POST
def logout_view(request):
    logout(request)
    return redirect('index')

def index(request):
    return render(request, 'index.html')

def registerPage(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = request.POST.get("first_name")
            user.last_name = request.POST.get("last_name")
            user.email = request.POST.get("email")
            user.username = request.POST.get("username")
            user.save()
            bio = request.POST.get("bio")
            dob = request.POST.get("dob")
            profile = request.FILES.get("profile")
            city = request.POST.get("city")
            occupation = request.POST.get("occupation")
            education = request.POST.get("education")
            hobbies = request.POST.get("hobbies")
            gender = request.POST.get("gender") 

            UserDetails.objects.create(
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


def profiles_view(request):
    profiles = UserDetails.objects.select_related('user').all()
    return render(request, 'profiles.html', {'profiles': profiles})

@login_required
def my_profile(request):
    return render(request, 'my_profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    user = request.user
    user_details = UserDetails.objects.get(user=user)

    if request.method == 'POST':
        user_form = ProfileEditForm(request.POST, instance=user)
        details_form = UserDetailsEditForm(request.POST, request.FILES, instance=user_details)

        if user_form.is_valid() and details_form.is_valid():
            user_form.save()
            details_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('my_profile')
    else:
        user_form = ProfileEditForm(instance=user)
        details_form = UserDetailsEditForm(instance=user_details)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,
        'details_form': details_form,
    })