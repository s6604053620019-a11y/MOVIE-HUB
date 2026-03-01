import requests
from django.core.management.base import BaseCommand
from movies.models import Movie

class Command(BaseCommand):
    help = 'ดึงข้อมูลหนังจาก TMDB'

    def handle(self, *args, **kwargs):
        # 1. ใส่ API Key ของคุณตรงนี้ (ในเครื่องหมายคำพูด)
        api_key = 'b68187fe531bf212d76bd46a62399142' 
        
        # URL ของ TMDB (ดึงหนังยอดนิยม)
        url = f'https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1'

        self.stdout.write("กำลังเชื่อมต่อกับ TMDB...")
        response = requests.get(url)
        
        if response.status_code != 200:
            self.stdout.write(self.style.ERROR('เชื่อมต่อไม่ได้! ตรวจสอบ API Key อีกทีครับ'))
            return

        data = response.json()
        movies = data['results']

        self.stdout.write(f"เจอหนังทั้งหมด {len(movies)} เรื่อง กำลังบันทึก...")

        for item in movies:
            # ดึงข้อมูลที่จำเป็น
            title = item['title']
            overview = item['overview']
            release_date = item['release_date']
            poster_path = item['poster_path']
            
            # สร้าง URL รูปเต็มๆ
            full_poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
            
            # เอาแค่ปี (4 ตัวแรกของวันที่)
            year = int(release_date[:4]) if release_date else 0

            # บันทึกลง Database (ถ้ามีอยู่แล้วจะไม่อัปเดต เพื่อป้องกันซ้ำ)
            movie, created = Movie.objects.get_or_create(
                title=title,
                defaults={
                    'description': overview,
                    'release_year': year,
                    'poster_url': full_poster_url
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'บันทึกใหม่: {title}'))
            else:
                self.stdout.write(f'มีอยู่แล้ว: {title}')

        self.stdout.write(self.style.SUCCESS('เสร็จเรียบร้อย!'))