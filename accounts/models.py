from django.db import models
from django.contrib.auth.models import User

# สร้างตารางแยกมาผูกกับ User แบบ 1-ต่อ-1
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True) # เก็บรูปไว้ในโฟลเดอร์ media/avatars/

    def __str__(self):
        return f"{self.user.username}'s Profile"