from django.contrib import admin
from .models import Movie

# ลงทะเบียนโมเดล Movie ให้หน้าแอดมินเห็น
admin.site.register(Movie)