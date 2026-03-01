from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

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