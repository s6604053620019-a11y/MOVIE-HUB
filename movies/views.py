from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .services import get_popular_movies, search_movies, get_movie_details
from .models import Movie, Review
from .forms import ReviewForm

def movie_list(request):
    query = request.GET.get('q')
    if query:
        movies = search_movies(query)
    else:
        movies = get_popular_movies()
    return render(request, 'movies/movie_list.html', {'movies': movies, 'query': query})

def movie_detail(request, tmdb_id):
    # Fetch movie details from TMDb API
    movie_data = get_movie_details(tmdb_id)
    if not movie_data:
        return render(request, '404.html', status=404)

    # Sync movie with local database for likes/reviews
    movie, created = Movie.objects.get_or_create(
        tmdb_id=tmdb_id,
        defaults={
            'title': movie_data['title'],
            'poster_path': movie_data['poster_url'].replace("https://image.tmdb.org/t/p/w500", "") if movie_data['poster_url'] else "",
            'release_year': movie_data['release_year']
        }
    )

    reviews = movie.reviews.all()
    user_liked = False
    in_watchlist = False
    form = ReviewForm()

    if request.user.is_authenticated:
        user_liked = movie.likes.filter(id=request.user.id).exists()
        in_watchlist = movie.watchlist.filter(id=request.user.id).exists()
        
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.movie = movie
                review.save()
                return redirect('movie_detail', tmdb_id=tmdb_id)

    context = {
        'movie': movie_data,
        'db_movie': movie,
        'reviews': reviews,
        'user_liked': user_liked,
        'in_watchlist': in_watchlist,
        'form': form
    }
    return render(request, 'movies/movie_detail.html', context)

@login_required
def toggle_like(request, tmdb_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
        
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
    if movie.likes.filter(id=request.user.id).exists():
        movie.likes.remove(request.user)
        liked = False
    else:
        movie.likes.add(request.user)
        liked = True
    return JsonResponse({'liked': liked, 'total_likes': movie.total_likes})

@login_required
def toggle_watchlist(request, tmdb_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
    if movie.watchlist.filter(id=request.user.id).exists():
        movie.watchlist.remove(request.user)
        added = False
    else:
        movie.watchlist.add(request.user)
        added = True
    return JsonResponse({'added': added})

def search_autocomplete(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    movies = search_movies(query)
    return JsonResponse({'results': movies[:5]})
