from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Avg, Count
from .services import (
    get_popular_movies, search_movies, get_movie_details,
    get_movies_by_genre, get_movies_by_year, get_movies_by_genre_and_year,
    get_tmdb_genres
)
from .models import Movie, Review
from .forms import ReviewForm


def movie_list(request):
    query = request.GET.get('q', '').strip()
    genre_id = request.GET.get('genre', '').strip()
    year = request.GET.get('year', '').strip()
    try:
        page = max(1, int(request.GET.get('page', 1)))
    except (ValueError, TypeError):
        page = 1

    # Fetch movies based on active filters
    if query:
        movies, total_pages = search_movies(query, page=page)
    elif genre_id and year:
        movies, total_pages = get_movies_by_genre_and_year(genre_id, year, page=page)
    elif genre_id:
        movies, total_pages = get_movies_by_genre(genre_id, page=page)
    elif year:
        movies, total_pages = get_movies_by_year(year, page=page)
    else:
        movies, total_pages = get_popular_movies(page=page)

    # Clamp total_pages to 500 (TMDb API max)
    total_pages = min(total_pages, 500)

    # --- Enrich movie cards with local DB data (avg rating, watchlist status) ---
    tmdb_ids = [m['id'] for m in movies]

    # Bulk query avg rating and review count
    db_movies = Movie.objects.filter(tmdb_id__in=tmdb_ids).annotate(
        avg_rating=Avg('reviews__rating'),
        review_count=Count('reviews')
    )
    db_map = {m.tmdb_id: m for m in db_movies}

    # Watchlist & likes set for current user
    user_watchlist_ids = set()
    user_liked_ids = set()
    if request.user.is_authenticated:
        user_watchlist_ids = set(
            request.user.watchlist_movies.filter(tmdb_id__in=tmdb_ids).values_list('tmdb_id', flat=True)
        )
        user_liked_ids = set(
            request.user.liked_movies.filter(tmdb_id__in=tmdb_ids).values_list('tmdb_id', flat=True)
        )

    # Inject DB data into each movie dict
    for movie in movies:
        db_obj = db_map.get(movie['id'])
        movie['avg_rating'] = round(db_obj.avg_rating, 1) if db_obj and db_obj.avg_rating else None
        movie['review_count'] = db_obj.review_count if db_obj else 0
        movie['in_watchlist'] = movie['id'] in user_watchlist_ids
        movie['is_liked'] = movie['id'] in user_liked_ids

    # Fetch TMDb genre list for filter UI
    genres = get_tmdb_genres()

    # Find active genre name
    active_genre_name = ''
    if genre_id:
        for g in genres:
            if str(g['id']) == genre_id:
                active_genre_name = g['name']
                break

    # Build page range for pagination widget (show ±3 pages around current)
    page_range = []
    if total_pages > 1:
        start = max(1, page - 3)
        end = min(total_pages, page + 3)
        page_range = list(range(start, end + 1))

    # Year choices for filter dropdown
    year_choices = list(range(2026, 1979, -1))

    context = {
        'movies': movies,
        'query': query,
        'genres': genres,
        'active_genre': genre_id,
        'active_genre_name': active_genre_name,
        'active_year': year,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'has_prev': page > 1,
        'has_next': page < total_pages,
        'year_choices': year_choices,
    }
    return render(request, 'movies/movie_list.html', context)


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

    reviews = movie.reviews.select_related('user').all()
    user_liked = False
    in_watchlist = False
    user_review = None
    form = ReviewForm()

    if request.user.is_authenticated:
        user_liked = movie.likes.filter(id=request.user.id).exists()
        in_watchlist = movie.watchlist.filter(id=request.user.id).exists()
        # Get user's existing review if any
        try:
            user_review = movie.reviews.get(user=request.user)
        except Review.DoesNotExist:
            user_review = None

        if request.method == 'POST':
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            form = ReviewForm(request.POST, instance=user_review)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.movie = movie
                review.save()
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'is_edit': user_review is not None,
                        'review': {
                            'id': review.id,
                            'username': review.user.username,
                            'rating': review.rating,
                            'text': review.text,
                            'created_at': review.created_at.strftime('%d %b %Y'),
                            'is_owner': True,
                        },
                        'avg_rating': movie.average_rating,
                        'rating_count': movie.rating_count,
                    })
                messages.success(request, 'Your review has been saved!')
                return redirect('movie_detail', tmdb_id=tmdb_id)
            else:
                if is_ajax:
                    return JsonResponse({'success': False, 'error': 'Please select a star rating.'}, status=400)
                messages.error(request, 'Please select a star rating.')
        elif user_review:
            form = ReviewForm(instance=user_review)

    context = {
        'movie': movie_data,
        'db_movie': movie,
        'reviews': reviews,
        'user_liked': user_liked,
        'in_watchlist': in_watchlist,
        'form': form,
        'user_review': user_review,
    }
    return render(request, 'movies/movie_detail.html', context)


@login_required
def toggle_like(request, tmdb_id):
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
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
    if movie.watchlist.filter(id=request.user.id).exists():
        movie.watchlist.remove(request.user)
        added = False
    else:
        movie.watchlist.add(request.user)
        added = True
    return JsonResponse({'added': added})


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    tmdb_id = review.movie.tmdb_id
    review.delete()
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        movie = Movie.objects.get(tmdb_id=tmdb_id)
        return JsonResponse({
            'success': True,
            'avg_rating': movie.average_rating,
            'rating_count': movie.rating_count,
        })
    messages.success(request, 'Your review has been deleted.')
    return redirect('movie_detail', tmdb_id=tmdb_id)


def search_autocomplete(request):
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})

    movies, _ = search_movies(query)
    return JsonResponse({'results': movies[:5]})
