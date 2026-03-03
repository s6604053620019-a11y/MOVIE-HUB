from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from .models import Movie  # เรียกใช้โมเดลหนังที่เราสร้างไว้
from django.contrib.auth.decorators import login_required  # ตัวเช็คว่าล็อกอินหรือยัง
from django.shortcuts import render, get_object_or_404, redirect # เพิ่ม redirect
from .forms import ReviewForm  # <--- เพิ่มบรรทัดนี้

def movie_list(request):
    query = request.GET.get('q')
    if query:
        # ถ้ามี: ให้หาหนังที่ชื่อมีคำนั้นอยู่ (icontains = ไม่สนตัวพิมพ์เล็ก-ใหญ่)
        movies = Movie.objects.filter(title__icontains=query)
    else:
        # ถ้าไม่มี: ให้ดึงหนังมาทั้งหมดเหมือนเดิม
        movies = Movie.objects.all()
    return render(request, 'movies/movie_list.html', {'movies': movies, 'query': query})
    # ส่งข้อมูลหนังไปที่หน้าเว็บ (Template) ที่ชื่อ movie_list.html
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    reviews = movie.reviews.all().order_by('-created_at') # ดึงรีวิวทั้งหมดของหนังเรื่องนี้ (ใหม่สุดขึ้นก่อน)

    if request.method == 'POST':
        # ถ้ามีการกดส่งรีวิว
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                new_review = form.save(commit=False)
                new_review.movie = movie      # บอกว่ารีวิวนี้ของหนังเรื่องนี้นะ
                new_review.user = request.user # บอกว่าใครเป็นคนเขียน
                new_review.save()
                return redirect('movie_detail', movie_id=movie_id) # รีเฟรชหน้าเดิม
        else:
            return redirect('login') # ถ้าไม่ได้ล็อกอิน ให้ไปล็อกอินก่อน
    else:
        # ถ้าแค่เปิดเข้ามาดูเฉยๆ
        form = ReviewForm()
    return render(request, 'movies/movie_detail.html', {
        'movie': movie, 
        'reviews': reviews, 
        'form': form
    })

@login_required  # บังคับว่าต้องล็อกอินก่อนถึงจะกดไลก์ได้
def toggle_like(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    
    # เช็คว่าเราอยู่ในรายชื่อคนที่ไลก์หรือยัง?
    if request.user in movie.likes.all():
        movie.likes.remove(request.user)  # ถ้ามีแล้ว เอาออก (Unlike)
    else:
        movie.likes.add(request.user)     # ถ้ายังไม่มี ใส่เพิ่ม (Like)
        
    # ทำเสร็จแล้ว เด้งกลับไปหน้าเดิม (หน้ารายละเอียดหนัง)
    return redirect('movie_detail', movie_id=movie_id)

@login_required
def toggle_watchlist(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)
    
    # ถ้ามีอยู่ในลิสต์แล้ว ให้เอาออก / ถ้ายังไม่มี ให้เพิ่มเข้าไป
    if request.user in movie.watchlist.all():
        movie.watchlist.remove(request.user)
    else:
        movie.watchlist.add(request.user)
        
    return redirect('movie_detail', movie_id=movie_id)