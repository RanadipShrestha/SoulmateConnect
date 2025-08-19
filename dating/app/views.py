from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import UserCreateForm, UserDetailsEditForm, ProfileEditForm, MessageForm
from .models import UserDetails, Like, Match, Message, Notification
from .models import FriendRequest


def index(request):
    homes = Home.objects.all()
    context ={
        'homes':homes
    }
    return render(request, 'index.html',context)

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
        # Check if a FriendRequest already exists from current_user to liked_user
        existing_request = FriendRequest.objects.filter(from_user=current_user, to_user=liked_user).first()
        
        if not existing_request:
            # Create a FriendRequest from current_user to liked_user
            FriendRequest.objects.create(from_user=current_user, to_user=liked_user)

            # Notify liked_user about the incoming friend request
            Notification.objects.create(
                recipient=liked_user,
                sender=current_user,
                message=f"{current_user.username} sent you a friend request!"
            )
        
        # Check if reciprocal friend request exists (liked_user -> current_user)
        reciprocal_request = FriendRequest.objects.filter(from_user=liked_user, to_user=current_user, accepted=False).first()
        
        if reciprocal_request:
            # Auto accept both requests and create a Match
            reciprocal_request.accepted = True
            reciprocal_request.save()

            current_request = FriendRequest.objects.get(from_user=current_user, to_user=liked_user)
            current_request.accepted = True
            current_request.save()

            user1, user2 = sorted([current_user, liked_user], key=lambda u: u.id)
            match, created = Match.objects.get_or_create(user1=user1, user2=user2)

            if created:
                # Notify both users of the match
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

    return redirect('profiles')


@require_POST
def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def profile_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    userdetails = getattr(user, 'userdetails', None)
    return render(request, 'profile_detail.html', {
        'user': user,
        'userdetails': userdetails
    })


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

    

def mark_as_read(self):
        self.is_read = True
        self.save()
        

@login_required
def my_matches(request):
    user = request.user

    # Get matches from the Match table
    match_objs = Match.objects.filter(Q(user1=user) | Q(user2=user))
    matched_users = [m.user2 if m.user1 == user else m.user1 for m in match_objs]

    # Incoming pending friend requests
    incoming_requests = FriendRequest.objects.filter(
        to_user=user,
        accepted=False
    )

    return render(request, "my_matches.html", {
        "matched_users": matched_users,
        "incoming_requests": incoming_requests
    })

from django.views.decorators.http import require_POST

@login_required
@require_POST
def accept_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user, accepted=False)

    # Mark friend request as accepted
    friend_request.accepted = True
    friend_request.save()

    # Create Match (user1 and user2 sorted by id to avoid duplicates)
    user1, user2 = sorted([friend_request.from_user, friend_request.to_user], key=lambda u: u.id)
    Match.objects.get_or_create(user1=user1, user2=user2)

    # Notify both users about the new match
    Notification.objects.create(
        recipient=friend_request.from_user,
        sender=friend_request.to_user,
        message=f"{friend_request.to_user.username} accepted your friend request!"
    )
    Notification.objects.create(
        recipient=friend_request.to_user,
        sender=friend_request.from_user,
        message=f"You accepted {friend_request.from_user.username}'s friend request!"
    )

    messages.success(request, f"You accepted {friend_request.from_user.username}'s request.")
    return redirect('my_matches')


@login_required
@require_POST
def decline_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user, accepted=False)
    from_username = friend_request.from_user.username
    friend_request.delete()
    messages.info(request, f"You declined {from_username}'s request.")
    return redirect('my_matches')


@login_required
@require_POST
def remove_match(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    Match.objects.filter(
        Q(user1=request.user, user2=other_user) |
        Q(user1=other_user, user2=request.user)
    ).delete()

    messages.success(request, f"You have removed your match with {other_user.username}.")
    return redirect('my_matches')

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
