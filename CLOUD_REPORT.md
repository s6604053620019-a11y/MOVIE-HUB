# รายงานโครงการ CineShare — เน้นด้าน Cloud Computing

## สารบัญ
1. [บทนำ](#1-บทนำ)
2. [ภาพรวมของโครงการ](#2-ภาพรวมของโครงการ)
3. [สถาปัตยกรรมระบบ (System Architecture)](#3-สถาปัตยกรรมระบบ-system-architecture)
4. [Cloud Services ที่ใช้ในโครงการ](#4-cloud-services-ที่ใช้ในโครงการ)
5. [การออกแบบเชิง Cloud-Native](#5-การออกแบบเชิง-cloud-native)
6. [แผนการ Deploy บน Cloud](#6-แผนการ-deploy-บน-cloud)
7. [ความปลอดภัย (Security)](#7-ความปลอดภัย-security)
8. [ข้อดีและข้อจำกัดด้าน Cloud](#8-ข้อดีและข้อจำกัดด้าน-cloud)
9. [สรุปและข้อเสนอแนะ](#9-สรุปและข้อเสนอแนะ)

---

## 1. บทนำ

**CineShare** เป็น Web Application สำหรับค้นหา รีวิว และแบ่งปันข้อมูลภาพยนตร์ พัฒนาด้วย Django Framework โดยมีการใช้งาน **Cloud-based API Services** เป็นหัวใจหลักของการดึงข้อมูล และออกแบบให้สามารถ Deploy บน **Cloud Platform** ได้

รายงานฉบับนี้จะเน้นวิเคราะห์โครงการในมุมมองของ **Cloud Computing** ครอบคลุมทั้ง Cloud Services ที่ใช้งาน, สถาปัตยกรรมที่รองรับ Cloud, และแผนการ Deploy บน Cloud Platform

---

## 2. ภาพรวมของโครงการ

| รายการ | รายละเอียด |
|--------|-----------|
| **ชื่อโครงการ** | CineShare |
| **ประเภท** | Movie Review & Discovery Web Application |
| **ภาษา/Framework** | Python 3 / Django 5.2 |
| **ฐานข้อมูล** | SQLite (Development) |
| **Web Server** | Gunicorn (WSGI HTTP Server) |
| **Static Files** | WhiteNoise Middleware |
| **External API** | TMDB (The Movie Database) Cloud API |
| **Frontend** | Django Template Engine + Bootstrap + Vanilla CSS/JS |

### ฟีเจอร์หลัก
- 🎬 ค้นหาและเรียกดูภาพยนตร์จาก TMDB Cloud API
- ⭐ ระบบรีวิวและให้คะแนนภาพยนตร์ (1-5 ดาว)
- ❤️ ระบบถูกใจ (Like) และ Watchlist
- 👤 ระบบสมาชิก สมัคร/เข้าสู่ระบบ/โปรไฟล์
- 🔍 ค้นหาอัตโนมัติ (Autocomplete Search)
- 🎭 กรองตาม Genre และ ปี

---

## 3. สถาปัตยกรรมระบบ (System Architecture)

```mermaid
graph TB
    subgraph "Client Layer"
        A["🌐 Web Browser<br/>(HTML/CSS/JS)"]
    end

    subgraph "Application Layer (Django)"
        B["Gunicorn<br/>WSGI Server"]
        C["Django Framework"]
        D["Views Layer<br/>(movies/views.py)"]
        E["Services Layer<br/>(movies/services.py)"]
        F["Models Layer<br/>(movies/models.py)"]
        G["WhiteNoise<br/>Static Files"]
    end

    subgraph "Cloud Services ☁️"
        H["TMDB Cloud API<br/>(api.themoviedb.org)"]
        I["TMDB Image CDN<br/>(image.tmdb.org)"]
        J["YouTube Embed<br/>(youtube.com)"]
    end

    subgraph "Data Layer"
        K["SQLite Database<br/>(User Data, Reviews)"]
        L["Media Storage<br/>(User Avatars)"]
    end

    A -->|"HTTP Request"| B
    B --> C
    C --> D
    D --> E
    D --> F
    C --> G
    E -->|"REST API Calls"| H
    A -->|"Image Loading"| I
    A -->|"Trailer Embed"| J
    F -->|"ORM Queries"| K
    F -->|"File Upload"| L
```

### อธิบายสถาปัตยกรรม

โครงการใช้สถาปัตยกรรมแบบ **3-Tier Architecture** ร่วมกับ **Cloud API Integration**:

1. **Presentation Tier** — Django Template + Bootstrap + JavaScript (ฝั่ง Browser)
2. **Application Tier** — Django Framework ทำหน้าที่เป็น Backend พร้อมเรียก Cloud API
3. **Data Tier** — SQLite สำหรับข้อมูลผู้ใช้ + TMDB Cloud API สำหรับข้อมูลหนัง

---

## 4. Cloud Services ที่ใช้ในโครงการ

### 4.1 TMDB (The Movie Database) — Cloud API

| รายการ | รายละเอียด |
|--------|-----------|
| **ผู้ให้บริการ** | TMDB (themoviedb.org) |
| **ประเภท** | RESTful Cloud API (SaaS) |
| **รูปแบบ Cloud** | Public Cloud |
| **Service Model** | Software as a Service (SaaS) |
| **Base URL** | `https://api.themoviedb.org/3` |
| **Authentication** | API Key (Query Parameter) |
| **Data Format** | JSON |

#### API Endpoints ที่ใช้งาน

| Endpoint | หน้าที่ | ไฟล์ที่เรียกใช้ |
|----------|--------|----------------|
| `GET /movie/popular` | ดึงรายการหนังยอดนิยม | `services.py` → `get_popular_movies()` |
| `GET /search/movie` | ค้นหาหนังตามชื่อ | `services.py` → `search_movies()` |
| `GET /discover/movie` | กรองหนังตาม Genre/Year | `services.py` → `get_movies_by_genre()` |
| `GET /movie/{id}` | ดึงรายละเอียดหนัง + Cast + Trailer | `services.py` → `get_movie_details()` |
| `GET /genre/movie/list` | ดึงรายการ Genre ทั้งหมด | `services.py` → `get_tmdb_genres()` |

#### ตัวอย่าง Code ที่เรียกใช้ Cloud API

```python
# services.py — การเรียก TMDB Cloud API
TMDB_API_KEY = "b68187fe..."
BASE_URL = "https://api.themoviedb.org/3"

def get_popular_movies(page=1):
    url = f"{BASE_URL}/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page={page}"
    response = requests.get(url)  # HTTP GET ไปยัง Cloud API
    if response.status_code == 200:
        data = response.json()
        return format_movies(data.get('results', [])), data.get('total_pages', 1)
    return [], 1
```

### 4.2 TMDB Image CDN — Cloud Content Delivery

| รายการ | รายละเอียด |
|--------|-----------|
| **URL** | `https://image.tmdb.org/t/p/` |
| **ประเภท** | Content Delivery Network (CDN) |
| **ขนาดภาพ** | w185 (cast), w500 (poster), original (backdrop) |
| **ลักษณะ** | โหลดรูปโดยตรงจาก CDN ไปยัง Browser ของผู้ใช้ |

รูปภาพทุกรูปในเว็บ (โปสเตอร์, Backdrop, รูปนักแสดง) ถูกโหลดจาก **TMDB Cloud CDN** โดยตรง ไม่ต้องเก็บในเซิร์ฟเวอร์ของเรา

### 4.3 YouTube Embed — Cloud Video Streaming

| รายการ | รายละเอียด |
|--------|-----------|
| **URL** | `https://www.youtube.com/embed/{key}` |
| **ประเภท** | Cloud Video Streaming (SaaS) |
| **การใช้งาน** | Embed Trailer ของภาพยนตร์ในหน้ารายละเอียด |

---

## 5. การออกแบบเชิง Cloud-Native

### 5.1 สิ่งที่โครงการทำได้ดีแล้ว (Cloud-Ready)

| หัวข้อ | รายละเอียด |
|--------|-----------|
| **Gunicorn** | ใช้ Production-grade WSGI Server พร้อม Deploy บน Cloud |
| **WhiteNoise** | จัดการ Static Files โดยไม่ต้องพึ่ง Nginx/Apache — เหมาะกับ PaaS |
| **ALLOWED_HOSTS = ['*']** | รองรับ Dynamic Hostname ของ Cloud Platform |
| **External API** | ข้อมูลหนังมาจาก Cloud API — ไม่ต้อง Store ข้อมูลขนาดใหญ่เอง |
| **requirements.txt** | มีไฟล์ Dependencies พร้อม Deploy |
| **Stateless Design** | ไม่พึ่ง Local Session Storage — พร้อม Scale ได้ |

### 5.2 สิ่งที่ต้องปรับปรุงเพื่อ Cloud Production

| หัวข้อ | สถานะปัจจุบัน | แนะนำสำหรับ Cloud |
|--------|--------------|-------------------|
| **Database** | SQLite (ไฟล์ Local) | ใช้ Cloud Database เช่น PostgreSQL บน AWS RDS / Google Cloud SQL |
| **Secret Key** | Hard-coded ใน settings.py | ใช้ Environment Variables หรือ Cloud Secret Manager |
| **API Key** | Hard-coded ใน services.py | ใช้ Environment Variables หรือ Cloud Secret Manager |
| **DEBUG Mode** | `DEBUG = True` | ต้องตั้ง `DEBUG = False` สำหรับ Production |
| **Media Storage** | เก็บใน Local Filesystem | ใช้ Cloud Object Storage เช่น AWS S3 / Google Cloud Storage |
| **HTTPS** | ยังไม่บังคับ | บังคับ HTTPS ผ่าน Cloud Load Balancer |

---

## 6. แผนการ Deploy บน Cloud

### 6.1 ตัวเลือก Cloud Platform

#### Option A: Render.com (แนะนำ — ง่ายที่สุด)

```mermaid
graph LR
    A["GitHub Repository"] -->|"Auto Deploy"| B["Render.com<br/>Web Service"]
    B -->|"Django App"| C["Render PostgreSQL<br/>(Cloud Database)"]
    B -->|"API Calls"| D["TMDB Cloud API"]
    B -->|"Static"| E["Render CDN"]
```

**ขั้นตอน:**
1. Push code ขึ้น GitHub
2. สร้าง Web Service ใน Render.com → เลือก Repository
3. ตั้งค่า Environment Variables (SECRET_KEY, TMDB_API_KEY)
4. สร้าง PostgreSQL Database ใน Render
5. เชื่อมต่อ Database → Deploy

#### Option B: AWS (Amazon Web Services)

| AWS Service | หน้าที่ |
|-------------|--------|
| **EC2** หรือ **Elastic Beanstalk** | รัน Django Application |
| **RDS (PostgreSQL)** | Cloud Database |
| **S3** | เก็บ Media Files (Avatar) |
| **CloudFront** | CDN สำหรับ Static/Media |
| **Route 53** | DNS Management |
| **ACM** | SSL Certificate |

#### Option C: Google Cloud Platform (GCP)

| GCP Service | หน้าที่ |
|-------------|--------|
| **App Engine** หรือ **Cloud Run** | รัน Django Application |
| **Cloud SQL (PostgreSQL)** | Cloud Database |
| **Cloud Storage** | เก็บ Media Files |
| **Cloud CDN** | Caching & CDN |
| **Cloud DNS** | DNS Management |

#### Option D: Microsoft Azure

| Azure Service | หน้าที่ |
|---------------|--------|
| **App Service** | รัน Django Application |
| **Azure Database for PostgreSQL** | Cloud Database |
| **Blob Storage** | เก็บ Media Files |
| **Azure CDN** | Caching & CDN |

### 6.2 สถาปัตยกรรม Cloud Deploy (ตัวอย่าง AWS)

```mermaid
graph TB
    subgraph "Internet"
        U["👤 Users"]
    end

    subgraph "AWS Cloud ☁️"
        subgraph "Networking"
            ALB["Application<br/>Load Balancer<br/>(HTTPS)"]
        end

        subgraph "Compute"
            EB1["EC2 Instance 1<br/>Django + Gunicorn"]
            EB2["EC2 Instance 2<br/>Django + Gunicorn"]
        end

        subgraph "Storage"
            RDS["RDS PostgreSQL<br/>(Multi-AZ)"]
            S3["S3 Bucket<br/>(Media Files)"]
        end

        subgraph "CDN"
            CF["CloudFront<br/>(Static + Media)"]
        end
    end

    subgraph "External Cloud Services"
        TMDB["TMDB API ☁️"]
        YT["YouTube ☁️"]
    end

    U -->|"HTTPS"| ALB
    ALB --> EB1
    ALB --> EB2
    EB1 --> RDS
    EB2 --> RDS
    EB1 --> S3
    EB1 -->|"REST API"| TMDB
    U -->|"CDN"| CF
    CF --> S3
    U -->|"Embed"| YT
```

---

## 7. ความปลอดภัย (Security)

### 7.1 Cloud Security ที่ควรทำ

| ด้าน | Best Practice | สถานะโครงการ |
|------|--------------|-------------|
| **API Key Management** | ใช้ Environment Variables หรือ Secret Manager | ❌ ยัง Hard-code |
| **HTTPS** | บังคับใช้ SSL/TLS | ❌ ยังไม่ตั้งค่า |
| **CSRF Protection** | Django CSRF Middleware | ✅ เปิดใช้งานแล้ว |
| **SQL Injection** | Django ORM ป้องกันอัตโนมัติ | ✅ ใช้ ORM |
| **XSS Protection** | Django Template Auto-escaping | ✅ เปิดใช้งานแล้ว |
| **DEBUG Mode** | ปิดใน Production | ❌ ยังเปิด `DEBUG = True` |
| **Password Validation** | ตั้งกฎ Password ที่เข้มงวด | ❌ ปิดอยู่ (Commented out) |

### 7.2 ตัวอย่าง Environment Variables สำหรับ Cloud

```bash
# ตั้งค่าใน Cloud Platform (Render / AWS / GCP)
SECRET_KEY=your-production-secret-key-here
TMDB_API_KEY=b68187fe531bf212d76bd46a62399142
DEBUG=False
DATABASE_URL=postgres://user:pass@cloud-host:5432/cineshare
ALLOWED_HOSTS=cineshare.example.com
```

---

## 8. ข้อดีและข้อจำกัดด้าน Cloud

### ข้อดี ✅

| ข้อดี | คำอธิบาย |
|-------|---------|
| **ลดภาระ Server** | ข้อมูลหนังทั้งหมดมาจาก TMDB Cloud — ไม่ต้อง Crawl/Store เอง |
| **CDN รูปภาพ** | รูปโหลดจาก TMDB CDN — ลด Bandwidth ของ Server |
| **Scalable** | สถาปัตยกรรม Stateless พร้อม Scale Horizontally บน Cloud |
| **Cloud-Ready Stack** | Gunicorn + WhiteNoise พร้อม Deploy บน PaaS/IaaS |
| **Cost Efficient** | TMDB API ฟรี — ลดต้นทุน Infrastructure |
| **ข้อมูลอัพเดทเรียลไทม์** | หนังใหม่, ข้อมูลล่าสุดจาก TMDB API อัตโนมัติ |

### ข้อจำกัด ⚠️

| ข้อจำกัด | คำอธิบาย |
|----------|---------|
| **พึ่งพา Third-party API** | หาก TMDB API ล่ม เว็บจะไม่แสดงข้อมูลหนัง |
| **API Rate Limit** | TMDB มี Rate Limit — ต้องจัดการ Caching |
| **SQLite ไม่เหมาะ Cloud** | ไม่รองรับ Concurrent Write — ต้องเปลี่ยนเป็น PostgreSQL |
| **Media บน Local** | Avatar เก็บใน Local — ต้องเปลี่ยนเป็น Cloud Storage |
| **Latency** | ทุก Request ต้องรอ TMDB API ตอบกลับ — อาจช้า |

---

## 9. สรุปและข้อเสนอแนะ

### สรุป

โครงการ **CineShare** ใช้ประโยชน์จาก **Cloud Computing** อย่างมีนัยสำคัญ โดยเฉพาะ:

1. **TMDB Cloud API (SaaS)** — เป็นแหล่งข้อมูลหลักของแอปพลิเคชัน ทำให้ไม่ต้องสร้างฐานข้อมูลหนังเอง
2. **TMDB Image CDN** — ลดภาระ Bandwidth ของเซิร์ฟเวอร์โดยให้ผู้ใช้โหลดรูปจาก CDN โดยตรง
3. **YouTube Cloud Streaming** — ฝัง Trailer จาก YouTube โดยไม่ต้อง Host วิดีโอเอง
4. **Cloud-Ready Architecture** — ด้วย Gunicorn + WhiteNoise พร้อม Deploy บน Cloud Platform

### ข้อเสนอแนะเพื่อปรับปรุง Cloud Readiness

| ลำดับ | ข้อเสนอแนะ | ความสำคัญ |
|-------|-----------|----------|
| 1 | เปลี่ยน Database เป็น Cloud PostgreSQL | 🔴 สูง |
| 2 | ย้าย API Key และ Secret Key ไปเป็น Environment Variables | 🔴 สูง |
| 3 | เพิ่ม Caching Layer (Redis) สำหรับ TMDB API Response | 🟡 ปานกลาง |
| 4 | ใช้ Cloud Storage (S3/GCS) สำหรับ Media Files | 🟡 ปานกลาง |
| 5 | ตั้งค่า CI/CD Pipeline สำหรับ Auto Deploy | 🟢 ต่ำ |
| 6 | เพิ่ม Health Check Endpoint สำหรับ Cloud Monitoring | 🟢 ต่ำ |

---

> **จัดทำโดย:** ระบบ AI Assistant  
> **วันที่:** 10 มีนาคม 2569  
> **โครงการ:** CineShare — Movie Review & Discovery Platform
