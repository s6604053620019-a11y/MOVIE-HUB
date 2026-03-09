from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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
    profile = request.user.userprofile
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    favorite_movies = request.user.liked_movies.all()
    watchlist_movies = request.user.watchlist_movies.all()
    my_reviews = request.user.reviews.all()
    
    context = {
        'profile': profile,
        'form': form,
        'favorite_movies': favorite_movies,
        'watchlist_movies': watchlist_movies,
        'my_reviews': my_reviews
    }
    return render(request, 'accounts/profile.html', context)
