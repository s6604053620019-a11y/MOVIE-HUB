from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count

class Movie(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    title = models.CharField(max_length=255)
    poster_path = models.CharField(max_length=255, null=True, blank=True)
    release_year = models.CharField(max_length=10, null=True, blank=True)
    
    likes = models.ManyToManyField(User, related_name='liked_movies', blank=True)
    watchlist = models.ManyToManyField(User, related_name='watchlist_movies', blank=True)

    def __str__(self):
        return self.title

    @property
    def total_likes(self):
        return self.likes.count()

    @property
    def average_rating(self):
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg, 1) if avg else 0

    @property
    def rating_count(self):
        return self.reviews.count()

    @property
    def rating_distribution(self):
        counts = self.reviews.values('rating').annotate(count=Count('rating')).order_by('rating')
        dist = {i: 0 for i in range(1, 6)}
        for item in counts:
            dist[item['rating']] = item['count']
        
        total = self.rating_count
        if total == 0:
            return {i: {'count': 0, 'percent': 0} for i in range(1, 6)}
            
        return {i: {'count': count, 'percent': (count / total) * 100} for i, count in dist.items()}

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('user', 'movie')

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} ({self.rating})"
