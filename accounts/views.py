from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from datetime import datetime
from time import sleep
import pytz
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from itertools import chain
import random
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404
from .forms import *
from .models import *
from django.urls import reverse
from django.http import JsonResponse
from random import sample
from django.db.models import Q
from django.http import Http404


User = get_user_model()

def landingpage(request):
    return render(request, 'landingpage.html')

def signup(request):
    form = RegisterForm(request.POST or None)

    if request.POST and form.is_valid():
        # Check if the username is already in use
        username = form.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            form.add_error('username', 'This username is already taken. Please choose a different one.')
        else:
            user = form.save()
            if user:
                # Log in the user
                login(request, user)
                return redirect('add_user_info')

    context = {
        'form': form,
    }

    return render(request, "signup.html", context)

def signin(request):
    form = LoginForm(request.POST or None)
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            # Use reverse to create a dynamic URL based on the 'profile' URL name
            # and pass the 'username' as a keyword argument
            return redirect(reverse('profile', kwargs={'username': user.username}))
    context = {
        "form": form
    }
    return render(request, "signin.html", context)
    

@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def add_user_info(request):
    if request.method == 'POST':
        form = AddUserInfoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Exclude the current user from username and email uniqueness checks
            form.save()
            # Redirect to the user's profile page
            return redirect(reverse('profile', kwargs={'username': request.user.username}))
    else:
        form = AddUserInfoForm(instance=request.user)
    
    return render(request, 'adduserinfo.html', {'form': form})

@login_required(login_url='signin')
def change_password(request):
    if request.method == 'POST':
        form = ChangePassForm(request.POST, instance=request.user)
        if form.is_valid():
            # Exclude the current user from username and email uniqueness checks
            form.save()
            # Redirect to the user's profile page
            return redirect(reverse('profile', kwargs={'username': request.user.username}))
    else:
        form = ChangePassForm(instance=request.user)
    
    return render(request, 'changepassword.html', {'form': form})

@login_required(login_url='signin')
def profile(request, username):
    try:
        user = get_object_or_404(CustomUser, username=username)
    except Http404:
        # User not found, display an error message or redirect to an error page
        return HttpResponse("User not found")
    comments = Comment.objects.filter(profile=user.profile)
    comment_form = CommentForm()

    is_admin = request.user.is_admin

    if request.method == 'POST':
        comment_form = CommentForm(request.POST, request.FILES)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.user = request.user
            new_comment.profile = user.profile

            # Check for profanity
            profanity_words = ProfanityWord.objects.values_list('word', flat=True)
            for word in profanity_words:
                if word.lower() in new_comment.content.lower():
                    return HttpResponse("Your comment contains profanity and cannot be posted.")

            new_comment.save()
            return redirect(reverse('profile', kwargs={'username': user.username}))

    # Check if the current user is the owner of the profile
    is_profile_owner = request.user == user

    # Handle comment deletion if the user is the profile owner
    if is_profile_owner or is_admin:  # Allow profile owner or admin to delete comments
        if request.method == 'POST':
            comment_id_to_delete = request.POST.get('comment_id_to_delete')
            if comment_id_to_delete:
                comment_to_delete = Comment.objects.get(id=comment_id_to_delete)
                comment_to_delete.delete()
                return redirect('profile', username=user.username)
    # Check if a user is logged in
    if request.user.is_authenticated:
        logged_in_user = request.user
    else:
        logged_in_user = None

    # Check if the logged-in user is friends with the profile user
    is_friends = Profile.objects.filter(friends=user.profile, user=request.user).exists()
    search_form = UserSearchForm()

    search_query = request.GET.get('username')
    search_results = None

    if search_query:
        search_form = UserSearchForm(request.GET)
        if search_form.is_valid():
            search_query = search_form.cleaned_data['username']
            search_results = CustomUser.objects.filter(username__icontains=search_query)

    recommended_friends = CustomUser.objects.exclude(id=user.id).order_by('?')[:5]

    return render(request, 'profile.html', {
        'user': user,
        'comments': comments,
        'comment_form': comment_form,
        'is_profile_owner': is_profile_owner,
        'logged_in_user': logged_in_user,
        'is_friends': is_friends,  # Pass the 'is_friends' variable to the template
        'search_form': search_form,
        'search_results': search_results,
        'is_admin': is_admin,
        'recommended_friends': recommended_friends,
    })

@login_required
def unfriend(request, username):
    user_to_unfriend = get_object_or_404(CustomUser, username=username)
    logged_in_user_profile = request.user.profile

    # Check if the logged-in user is friends with the user to unfriend
    if user_to_unfriend.profile in logged_in_user_profile.friends.all():
        logged_in_user_profile.friends.remove(user_to_unfriend.profile)
        messages.success(request, f"You are no longer friends with {user_to_unfriend.username}.")
    else:
        messages.error(request, f"You were not friends with {user_to_unfriend.username}.")

    return redirect('profile', username=username)

@login_required(login_url='signin')
def send_friend_request(request, to_user_id):
    to_user = User.objects.get(id=to_user_id)
    from_user = request.user

    if to_user != from_user:
        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
    return redirect('profile', username=to_user.username)

@login_required(login_url='signin')
def accept_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)
    
    if request.user == friend_request.to_user:
        friend_request.is_accepted = True
        friend_request.save()
        
        # Get the Profile instances for the sender and receiver
        to_user_profile = get_object_or_404(Profile, user=friend_request.to_user)
        from_user_profile = get_object_or_404(Profile, user=friend_request.from_user)
        
        # Add each user as a friend to the other's Profile
        to_user_profile.friends.add(from_user_profile)
        from_user_profile.friends.add(to_user_profile)
        
        return redirect('friend_requests')
    else:
        # Handle the case where the request user is not the recipient
        # You can redirect or display an error message
        return HttpResponse("You are not authorized to accept this request.")
    
@login_required(login_url='signin')
def decline_friend_request(request, request_id):
    friend_request = FriendRequest.objects.get(id=request_id)

    if request.user == friend_request.to_user:
        friend_request.delete()  # Delete the friend request

        # You can also handle any additional logic here if needed

        return redirect('friend_requests')
    else:
        # Handle the case where the request user is not the recipient
        # You can redirect or display an error message
        return HttpResponse("You are not authorized to decline this request.")

@login_required(login_url='signin')
def friend_requests(request):
    friend_requests_received = FriendRequest.objects.filter(to_user=request.user, is_accepted=False)
    friend_requests_sent = FriendRequest.objects.filter(from_user=request.user, is_accepted=False)
    return render(request, 'friend_requests.html', {
        'friend_requests_received': friend_requests_received,
        'friend_requests_sent': friend_requests_sent,
    })

@login_required(login_url='signin')
def change_user_info(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            # Exclude the current user from username and email uniqueness checks
            form.instance.username = form.cleaned_data['username']
            form.instance.email = form.cleaned_data['email']
            form.save()
            # Redirect to the user's profile page
            return redirect(reverse('profile', kwargs={'username': request.user.username}))
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'changeuserinfo.html', {'form': form})

@login_required(login_url='signin')
def user_search(request):
    results = []
    if request.method == 'GET':
        form = UserSearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['username']
            results = User.objects.filter(username__icontains=query)
    else:
        form = UserSearchForm()

    return render(request, 'user_search.html', {'form': form, 'results': results})

# ADMIN VIEWS
def is_admin(user):
    return user.is_admin

@login_required
@user_passes_test(is_admin, login_url='user_list')
def user_list(request):
    search_query = request.GET.get('search')

    if search_query:
        # Use Q objects to perform case-insensitive search on username, first_name, and last_name
        users = User.objects.filter(Q(username__icontains=search_query) |
                                   Q(first_name__icontains=search_query) |
                                   Q(last_name__icontains=search_query))
    else:
        users = User.objects.all()

    return render(request, 'admin/userlist.html', {'users': users})


@login_required
@user_passes_test(is_admin, login_url='user_list')
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # Exclude the current user from username and email uniqueness checks
            form.instance.username = form.cleaned_data['username']
            form.instance.email = form.cleaned_data['email']
            form.save()
            return redirect('user_list')
    else:
        form = UserProfileForm(instance=user)

    return render(request, 'admin/edituser.html', {'user': user, 'form': form})

@login_required
@user_passes_test(is_admin, login_url='user_list')
def delete_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == 'POST':
        user.delete()
        # Redirect to the user list or a success page after deletion
    
    return redirect('user_list')

@login_required(login_url='signin')
@user_passes_test(is_admin, login_url='user_list')
def add_profanity_word(request):
    profanity_words = ProfanityWord.objects.all()  # Retrieve the list of profanity words
    if request.method == 'POST':
        form = ProfanityWordForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('add_profanity_word')
    else:
        form = ProfanityWordForm()
    return render(request, 'admin/profanityadd.html', {'form': form, 'profanity_words': profanity_words})

@login_required(login_url='signin')
@user_passes_test(is_admin, login_url='user_list')
def delete_profanity_word(request, word_id):
    profanity_word = get_object_or_404(ProfanityWord, pk=word_id)
    if request.method == 'POST':
        profanity_word.delete()
    return redirect('add_profanity_word')