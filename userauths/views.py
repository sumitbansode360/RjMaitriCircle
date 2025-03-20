from django.shortcuts import render, redirect, get_object_or_404, HttpResponse, HttpResponseRedirect
from userauths.forms import UserRegisterForm, EditProfile
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from userauths.models import Profile, User
from post.models import Post, Follow, Stream
from django.urls import resolve, reverse
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from django.contrib.auth import get_user_model, authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm
from .models import Profile
from userauths.utils import send_activation_email
from channels.layers import get_channel_layer
from notification.models import Notification
from asgiref.sync import async_to_sync



User = get_user_model()

def RegisterView(request):
    if request.user.is_authenticated:
        messages.warning(request, f"{request.user}, you are already logged in!")
        return redirect('index')

    form = UserRegisterForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        # Save the user
        user = form.save(commit=False)  # Save the form but don't commit yet
        user.full_name = form.cleaned_data.get("full_name")
        user.save()  # Save the user with the updated full_name

        # Generate activation link
        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = default_token_generator.make_token(user)   # Create token using default generator
        activation_link = reverse('activate', kwargs={'uidb64': uid, 'token': token})
        activation_url = f'{settings.SITE_DOMAIN}{activation_link}'

        # send mail
        send_activation_email(user.email, activation_url)

        messages.success(request, "Account created! Please check your email to activate your account.")
        return redirect('sign-in')  # Redirect to login after successful registration

    context = {"form": form}
    return render(request, 'userauths/register.html', context)


def activate_account(request, uidb64, token):
    try:
        # Decode the user ID
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

        # Validate the token
        if default_token_generator.check_token(user, token):
            user.is_active = True  # Activate the user account
            user.save()
            messages.success(request, "Account activated! You can now log in.")
            return redirect('sign-in')  # Redirect to login page
        else:
            messages.error(request, "Activation link is invalid or has expired.")
            return redirect('register')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid activation link.")
        return redirect('register')

def Loginview(request):
    if request.user.is_authenticated:
        messages.warning(request, f"{request.user} you are already logged in!")
        return redirect('index')
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user_query = User.objects.get(email=email)
            user_auth = authenticate(request, username=email, password=password)  # Email as username
            if user_auth is not None:
                login(request, user_auth)
                messages.success(request, f"{request.user} you are logged in now!")
                next_url = request.GET.get("next", "index") 
                return redirect(next_url)
            else:
                messages.error(request, "invalid email or password")
                return redirect('sign-in')      
        except: 
            messages.error(request, "User does not exist!")
            return redirect('sign-in')
    return render(request, 'userauths/sign-in.html')

def LogOutView(request):
    logout(request)
    messages.success(request,"You are log out!")
    return redirect('sign-in')


def ProfileView(request, username):

    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    url_name = resolve(request.path).url_name

    if url_name == 'ProfileView':
        posts = Post.objects.filter(user=user)
    else:
        posts = profile.saved.all()

    #pagination
    paginator = Paginator(posts,3)
    page_number = request.GET.get('page')
    post_paginator = paginator.get_page(page_number)
    
    # follow stats
    follow_status = Follow.objects.filter(follower=request.user, following=user).exists()
    # profile stats
    post_count = Post.objects.filter(user=user).count()
    following_count = Follow.objects.filter(follower=user).count()
    follower_count = Follow.objects.filter(following=user).count()

    context = {
        "posts" : posts,
        "profile" : profile,
        "paginator" : post_paginator,
        "url_name" : url_name,
        "post_count" : post_count,
        "follower_count" : follower_count,
        "following_count" : following_count,
        "follow_status" : follow_status,

    }

    return render(request, 'userauths/profile.html', context)

def FollowView(request, username, option):
    user = request.user
    if not user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    following = get_object_or_404(User, username=username)

    try:
        # Get or create a follow relationship
        follow_obj, created = Follow.objects.get_or_create(follower=user, following=following)

        if int(option) == 0:
            # Unfollow logic
            follow_obj.delete()
            Stream.objects.filter(user=user, following=following).delete()
        else:
            # Follow logic
            posts = Post.objects.filter(user=following)
            with transaction.atomic():
                for post in posts:
                    Stream.objects.create(
                        post=post,
                        user=request.user,
                        following=following,
                        date=post.posted,
                    )
            
            notification = Notification.objects.create(
                user = follow_obj.following,
                sender = follow_obj.follower,
                notification_type = "follow",
                message = f"{user.username} just followed you! 🎉 Check out their profile!"
            )


            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{following.id}",  
                {
                    "type" : "send_notification",
                    "notification": {
                        "id": notification.id,
                        "image": notification.sender.profile.image.url if notification.sender.profile.image.url else "/static/default-profile.png",
                        "notification_type": notification.notification_type,
                        "message": notification.message,
                        "timestamp": str(notification.created_at),
                    }
                }
            )

        # Redirect to the profile view of the user being followed/unfollowed
        return HttpResponseRedirect(reverse('ProfileView', args=[username]))
    except Exception as e:
        # Handle unexpected errors
        return HttpResponse(f"An error occurred: {str(e)}", status=500)
    
#edit profile
@login_required
def EditProfileView(request):
    user = request.user
    profile = get_object_or_404(Profile, user=user)

    if request.method == "POST":
        form = EditProfile(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated!")
            profile_url = reverse('ProfileView', kwargs={'username': user.username})
            return redirect(profile_url)  # Use reverse to ensure proper resolution        
    else:
        form = EditProfile(instance=profile)

    context = {
        'form': form,
        'profile' : profile,
    }
    return render(request, 'userauths/edit-profile.html', context)

def Follower_List(request, username):
    user_profile = Profile.objects.get(user__username=username)
    
    # Get followers: Users who follow the requested user
    followers = Follow.objects.filter(following=user_profile.user).select_related('follower')
    
    context = {
        'user_profile': user_profile,
        'followers': [f.follower for f in followers],  # List of follower profiles
    }
    return render(request, 'follows/followers.html', context)

def Following_List(request, username):

    user_profile = Profile.objects.get(user__username=username)
    following = Follow.objects.filter(follower=user_profile.user).select_related('following')

    
    context = {
        'user_profile': user_profile,
        'following': [f.following for f in following],  # List of following profiles

    }

    return render(request, 'follows/following.html', context)


def Search(request):
    context = { }
    user = User.objects.all()
    prof = Profile.objects.all()

    if request.GET.get('search'):
        search = request.GET.get('search')
        serach_user = user.filter(
            Q(username__icontains=search) |
            Q(profile__full_name__icontains=search)|
            Q(profile__bio__icontains=search)|
            Q(profile__location__icontains=search)
            
        )
        print(f"Search result count: {serach_user.count()}")

        #Paginator
        paginator = Paginator(serach_user,8)
        page_number = request.GET.get('page')
        users_paginator = paginator.get_page(page_number)

        context = {
            'users' : users_paginator
        }
    return render(request,'search.html',context)
