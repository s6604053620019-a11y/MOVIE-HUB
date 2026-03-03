from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from movies.models import Movie, Review
from .models import UserProfile      # <--- เพิ่ม
from .forms import UserProfileForm

def signup_view(request):
    if request.method == 'POST':
        # ถ้ามีการกดปุ่ม Submit (ส่งข้อมูลมา)
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()      # 1. บันทึกสมาชิกลงฐานข้อมูล
            login(request, user)    # 2. ล็อกอินให้เลยอัตโนมัติ
            return redirect('/')    # 3. เด้งกลับไปหน้าแรก
    else:
        # ถ้าเปิดหน้าเว็บเฉยๆ (ยังไม่กรอก)
        form = UserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required # บังคับล็อกอินก่อนเข้าหน้านี้
def profile_view(request):
    # ดึงข้อมูลของ "ฉัน" คนเดียว
    user = request.user
    
    # --- ส่วนที่ 1: จัดการ Profile และอัปโหลดรูปภาพ ---
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # ข้อควรระวัง: ต้องมี request.FILES เพื่อรับไฟล์รูปภาพ
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile') # โหลดหน้าเดิมซ้ำให้รูปใหม่ขึ้น
    else:
        form = UserProfileForm(instance=profile)
        
    # --- ส่วนที่ 2: ดึงข้อมูลประวัติการใช้งาน ---
    favorite_movies = user.liked_movies.all() # หนังที่ฉันไลก์
    my_reviews = Review.objects.filter(user=user).order_by('-created_at') # รีวิวของฉัน
    watchlist_movies = user.watchlist_movies.all() # หนังใน Watchlist

    return render(request, 'accounts/profile.html', {
        'favorite_movies': favorite_movies,
        'my_reviews': my_reviews, # <--- เติมลูกน้ำ (Comma) ตรงนี้ให้แล้วครับ ไม่งั้น Error แน่นอน!
        'watchlist_movies': watchlist_movies,
        'form': form, # <--- ส่งฟอร์มรูปไปที่หน้าเว็บด้วย
        'profile': profile
    })