from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    # ชื่อหนัง (ตัวหนังสือสั้นๆ)
    title = models.CharField(max_length=200)
    
    # เรื่องย่อ (ตัวหนังสือยาวๆ)
    description = models.TextField()
    
    # ปีที่ฉาย (ตัวเลข)
    release_year = models.IntegerField()
    
    # ลิงก์รูปโปสเตอร์ (ใส่เป็น URL ก่อน เพื่อความง่าย)
    poster_url = models.URLField(default="https://placehold.co/600x400")
    where_to_watch = models.CharField(max_length=200, blank=True, null=True, help_text="เช่น Netflix, Disney+, HBO GO")

    likes = models.ManyToManyField(User, related_name='liked_movies', blank=True)
    watchlist = models.ManyToManyField(User, related_name='watchlist_movies', blank=True)

    def __str__(self):
        return self.title
    
    def total_likes(self):
        return self.likes.count()

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews') # เชื่อมกับหนัง
    user = models.ForeignKey(User, on_delete=models.CASCADE) # เชื่อมกับคนเขียน
    text = models.TextField() # เนื้อหาที่เขียน
    created_at = models.DateTimeField(auto_now_add=True) # เวลาที่เขียน
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} review of {self.movie.title}"