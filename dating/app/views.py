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
from .models import Like, Match
from django.db.models import Q
from .forms import MessageForm
from .models import Message

@login_required
def like_user(request, user_id):
    from_user = request.user
    to_user = get_object_or_404(User, id=user_id)

    # Prevent duplicate likes
    if Like.objects.filter(from_user=from_user, to_user=to_user).exists():
        messages.info(request, "You already liked this user.")
        return redirect('profiles')

    # Save the like
    Like.objects.create(from_user=from_user, to_user=to_user)

    # Check for mutual like
    if Like.objects.filter(from_user=to_user, to_user=from_user).exists():
        user_ids = sorted([from_user.id, to_user.id])
        if not Match.objects.filter(user1_id=user_ids[0], user2_id=user_ids[1]).exists():
            Match.objects.create(user1_id=user_ids[0], user2_id=user_ids[1])
            messages.success(request, "It's a match!")

    else:
        messages.success(request, "You liked this user.")

    return redirect('profiles')



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
    profiles = UserDetails.objects.select_related('user').exclude(user=request.user)
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

@require_POST
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def my_matches(request):
    user = request.user
    matches = Match.objects.filter(user1=user) | Match.objects.filter(user2=user)
    matched_users = []

    for match in matches:
        matched_users.append(match.user2 if match.user1 == user else match.user1)

    return render(request, 'my_matches.html', {'matched_users': matched_users})

@login_required
def conversations(request):
    user = request.user
    # Get users matched with the current user
    matches = Match.objects.filter(Q(user1=user) | Q(user2=user))
    matched_users = []
    for match in matches:
        matched_users.append(match.user2 if match.user1 == user else match.user1)

    return render(request, 'conversations.html', {'matched_users': matched_users})


@login_required
def chat_view(request, user_id):
    user = request.user
    other_user = get_object_or_404(User, id=user_id)

    # Check if they are matched
    matched = Match.objects.filter(
        Q(user1=user, user2=other_user) | Q(user1=other_user, user2=user)
    ).exists()

    if not matched:
        return redirect('conversations')  # not allowed

    messages = Message.objects.filter(
        Q(sender=user, recipient=other_user) | Q(sender=other_user, recipient=user)
    ).order_by('timestamp')

    # Mark received messages as read
    Message.objects.filter(sender=other_user, recipient=user, is_read=False).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = user
            message.recipient = other_user
            message.save()
            return redirect('chat_view', user_id=other_user.id)
    else:
        form = MessageForm()

    return render(request, 'chat.html', {
        'other_user': other_user,
        'messages': messages,
        'form': form,
    })