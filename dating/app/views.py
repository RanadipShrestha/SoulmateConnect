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
from .models import Message, Notification
from app.models import Notification

def index(request):
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'index.html', {'unread_count': unread_count})


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



# @login_required
# def profile_view(request, user_id):
#     user = request.user

#     # Users already liked or disliked
#     liked_or_disliked_user_ids = Like.objects.filter(from_user=user).values_list('to_user_id', flat=True)

#     # Users matched with current user
#     matched_user_ids = Match.objects.filter(
#         Q(user1=user) | Q(user2=user)
#     ).values_list('user1_id', 'user2_id')

#     # Flatten matched_user_ids tuples and exclude current user id
#     matched_user_ids_flat = set()
#     for u1, u2 in matched_user_ids:
#         if u1 != user.id:
#             matched_user_ids_flat.add(u1)
#         if u2 != user.id:
#             matched_user_ids_flat.add(u2)

#     # Combine all to exclude
#     exclude_ids = list(set(liked_or_disliked_user_ids) | matched_user_ids_flat | {user.id})

#     profiles = UserDetails.objects.select_related('user').exclude(user__id__in=exclude_ids)

#     return render(request, 'profiles.html', {'profiles': profiles})



@login_required
def profiles_view(request):
    user = request.user

    # Get all matched user IDs where current user is user1 or user2
    matched_user_ids = Match.objects.filter(Q(user1=user) | Q(user2=user)) \
                                    .values_list('user1__id', 'user2__id')

    # Flatten the tuple list to a set of IDs excluding current user's ID
    matched_ids = set()
    for u1, u2 in matched_user_ids:
        if u1 != user.id:
            matched_ids.add(u1)
        if u2 != user.id:
            matched_ids.add(u2)

    # Get profiles excluding self and matched users
    profiles = UserDetails.objects.select_related('user') \
        .exclude(user=user) \
        .exclude(user__id__in=matched_ids)

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



@login_required
@require_POST
def like_user(request, user_id):
    liked_user = get_object_or_404(User, id=user_id)
    current_user = request.user

    if liked_user != current_user:
        # Create or get the Like
        like, created = Like.objects.get_or_create(from_user=current_user, to_user=liked_user)
        
        if created:
            # Check if liked_user has already liked current_user
            reciprocal_like_exists = Like.objects.filter(from_user=liked_user, to_user=current_user).exists()
            
            if reciprocal_like_exists:
                # Check if match already exists to avoid duplicates
                user1, user2 = sorted([current_user, liked_user], key=lambda u: u.id)
                match, match_created = Match.objects.get_or_create(user1=user1, user2=user2)

                if match_created:
                    # Create matched notification for both users
                    Notification.objects.create(
                        recipient=current_user,
                        sender=liked_user,
                        message=f"You matched with {liked_user.username}!"
                    )
                    Notification.objects.create(
                        recipient=liked_user,
                        sender=current_user,
                        message=f"You matched with {current_user.username}!"
                    )
            else:
                # Just notify liked_user about the like
                Notification.objects.create(
                    recipient=liked_user,
                    sender=current_user,
                    message=f"{current_user.username} liked you!"
                )

    return redirect('profiles')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def my_matches(request):
    user = request.user
    # Get matches where the logged-in user is either user1 or user2
    matches = Match.objects.filter(user1=user) | Match.objects.filter(user2=user)
    matched_users = []

    for match in matches:
        other_user = match.user2 if match.user1 == user else match.user1
        matched_users.append(other_user)

    return render(request, 'my_matches.html', {'matched_users': matched_users})


@login_required
def profile_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    userdetails = getattr(user, 'userdetails', None)
    return render(request, 'profile_detail.html', {
        'user': user,
        'userdetails': userdetails
    })


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
    other_user = get_object_or_404(User, id=user_id)
    room_name = f'{min(request.user.id, other_user.id)}_{max(request.user.id, other_user.id)}'

    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        recipient__in=[request.user, other_user]
    ).order_by('timestamp')

    if request.method == "POST":
        message_content = request.POST.get('message')
        if message_content:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                content=message_content,
            )
            return redirect('chat_view', user_id=other_user.id)

    return render(request, 'chat.html', {
        'other_user': other_user,
        'room_name': room_name,
        'messages': messages,
    })


@login_required
def notifications_view(request):
    notifications = request.user.notifications.order_by('-timestamp')
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})
