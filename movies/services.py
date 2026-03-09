import requests

TMDB_API_KEY = "b68187fe531bf212d76bd46a62399142"
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


def _fetch_movies(url):
    """Fetch movies from a URL, return (movies_list, total_pages)."""
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return format_movies(data.get('results', [])), data.get('total_pages', 1)
    return [], 1


def get_popular_movies(page=1):
    url = f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
    return _fetch_movies(url)


def search_movies(query, page=1):
    url = f"{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&language=en-US&query={query}&page={page}"
    return _fetch_movies(url)


def get_movies_by_genre(genre_id, page=1):
    url = f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&language=en-US&with_genres={genre_id}&sort_by=popularity.desc&page={page}"
    return _fetch_movies(url)


def get_movies_by_year(year, page=1):
    url = f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&language=en-US&primary_release_year={year}&sort_by=popularity.desc&page={page}"
    return _fetch_movies(url)


def get_movies_by_genre_and_year(genre_id, year, page=1):
    url = f"{BASE_URL}/discover/movie?api_key={TMDB_API_KEY}&language=en-US&with_genres={genre_id}&primary_release_year={year}&sort_by=popularity.desc&page={page}"
    return _fetch_movies(url)


def get_tmdb_genres():
    """Return list of genre dicts: [{'id': 28, 'name': 'Action'}, ...]"""
    url = f"{BASE_URL}/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get('genres', [])
    return []


def get_movie_details(movie_id):
    # Fetch main details and credits, videos, recommendations using append_to_response
    url = f"{BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}&language=en-US&append_to_response=credits,videos,recommendations"
    response = requests.get(url)
    if response.status_code == 200:
        movie = response.json()

        # Extract cast (top 10)
        cast = []
        for person in movie.get('credits', {}).get('cast', [])[:10]:
            cast.append({
                'name': person['name'],
                'character': person['character'],
                'profile_url': f"https://image.tmdb.org/t/p/w185{person['profile_path']}" if person.get('profile_path') else None
            })

        # Extract director
        director = "Unknown"
        for person in movie.get('credits', {}).get('crew', []):
            if person['job'] == 'Director':
                director = person['name']
                break

        # Find YouTube trailer
        trailer_key = None
        for video in movie.get('videos', {}).get('results', []):
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                trailer_key = video['key']
                break

        # Recommendations
        recommendations = format_movies(movie.get('recommendations', {}).get('results', [])[:6])

        return {
            'id': movie['id'],
            'title': movie['title'],
            'description': movie['overview'],
            'release_year': movie['release_date'][:4] if movie.get('release_date') else "N/A",
            'poster_url': f"{IMAGE_BASE_URL}{movie['poster_path']}" if movie.get('poster_path') else None,
            'backdrop_url': f"https://image.tmdb.org/t/p/original{movie['backdrop_path']}" if movie.get('backdrop_path') else None,
            'vote_average': round(movie.get('vote_average', 0), 1),
            'runtime': movie.get('runtime'),
            'genres': [g['name'] for g in movie.get('genres', [])],
            'director': director,
            'cast': cast,
            'trailer_key': trailer_key,
            'recommendations': recommendations
        }
    return None


def format_movies(movies_list):
    formatted = []
    for m in movies_list:
        formatted.append({
            'id': m['id'],
            'title': m['title'],
            'release_year': m['release_date'][:4] if m.get('release_date') else "N/A",
            'poster_url': f"{IMAGE_BASE_URL}{m['poster_path']}" if m.get('poster_path') else None,
            'backdrop_url': f"https://image.tmdb.org/t/p/original{m['backdrop_path']}" if m.get('backdrop_path') else None,
            'overview': m.get('overview', ''),
        })
    return formatted
