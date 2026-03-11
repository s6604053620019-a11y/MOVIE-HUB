from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import SignUpForm, UserProfileForm
from .models import UserProfile


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to CineShare, {user.username}! Your account has been created successfully.")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=user_profile)

    favorite_movies = request.user.liked_movies.all()
    watchlist_movies = request.user.watchlist_movies.all()
    my_reviews = request.user.reviews.select_related('movie').all()

    context = {
        'profile': user_profile,
        'form': form,
        'favorite_movies': favorite_movies,
        'watchlist_movies': watchlist_movies,
        'my_reviews': my_reviews,
    }
    return render(request, 'accounts/profile.html', context)


def public_profile(request, username):
    """View another user's public profile."""
    profile_user = get_object_or_404(User, username=username)
    user_profile = profile_user.userprofile

    # If viewing own profile, redirect to editable profile
    if request.user == profile_user:
        return redirect('profile')

    is_following = False
    if request.user.is_authenticated:
        is_following = request.user.userprofile.following.filter(pk=user_profile.pk).exists()

    favorite_movies = profile_user.liked_movies.all()
    watchlist_movies = profile_user.watchlist_movies.all()
    user_reviews = profile_user.reviews.select_related('movie').all()

    context = {
        'profile_user': profile_user,
        'profile': user_profile,
        'is_following': is_following,
        'favorite_movies': favorite_movies,
        'watchlist_movies': watchlist_movies,
        'user_reviews': user_reviews,
    }
    return render(request, 'accounts/public_profile.html', context)


@login_required
def toggle_follow(request, username):
    """Follow or unfollow a user via AJAX."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)

    my_profile = request.user.userprofile
    target_profile = target_user.userprofile

    if my_profile.following.filter(pk=target_profile.pk).exists():
        my_profile.following.remove(target_profile)
        following = False
    else:
        my_profile.following.add(target_profile)
        following = True

    return JsonResponse({
        'following': following,
        'followers_count': target_profile.followers_count,
    })


def members_list(request):
    """List all members with their stats."""
    profiles = UserProfile.objects.select_related('user').all().order_by('-user__date_joined')

    # Add follow status for authenticated users
    members = []
    for p in profiles:
        is_following = False
        if request.user.is_authenticated and request.user != p.user:
            is_following = request.user.userprofile.following.filter(pk=p.pk).exists()
        members.append({
            'profile': p,
            'is_following': is_following,
        })

    return render(request, 'accounts/members.html', {'members': members})


@login_required
def activity_feed(request):
    """Show recent reviews from users you follow."""
    from movies.models import Review

    following_profiles = request.user.userprofile.following.all()
    following_users = User.objects.filter(userprofile__in=following_profiles)

    reviews = Review.objects.filter(
        user__in=following_users
    ).select_related('user', 'movie').order_by('-created_at')[:50]

    return render(request, 'accounts/activity_feed.html', {
        'reviews': reviews,
        'following_count': following_profiles.count(),
    })
