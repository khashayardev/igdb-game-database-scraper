# 🎮 IGDB Game Fetcher

> دریافت خودکار اطلاعات بازی‌های ویدیویی از سال ۲۰۰۰ تا ۲۰۲۶ با پایتون و GitHub Actions

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-blue?logo=githubactions)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.11%2B-green?logo=python)](https://www.python.org/)
[![IGDB](https://img.shields.io/badge/IGDB-API-purple?logo=twitch)](https://igdb.com/)

---

## 📖 معرفی پروژه

این ابزار یک اسکریپت پایتون است که از **API رسمی IGDB** (از طریق توئیچ) اطلاعات کامل بازی‌ها را دریافت کرده و در فایل **JSON** ذخیره می‌کند.  
اسکریپت در **GitHub Actions** اجرا می‌شود و خروجی نهایی به صورت **Artifact** قابل دانلود است.

---

## 🗂️ فیلدهای دریافتی برای هر بازی

| فیلد | توضیح |
|:---|:---|
| `id` | شناسه یکتا در IGDB |
| `name` | نام بازی |
| `slug` | نسخه کوتاه نام برای URL |
| `summary` | خلاصه کوتاه از بازی |
| `storyline` | داستان کامل |
| `first_release_date` | تاریخ انتشار (میلادی) |
| `genres` | لیست ژانرهای بازی |
| `platforms` | لیست پلتفرم‌های قابل اجرا |
| `cover` | آدرس کاور بازی |
| `screenshots` | لیست آدرس اسکرین‌شات‌ها |
| `rating` | امتیاز کاربران |
| `popularity` | میزان محبوبیت |
| `game_modes` | حالت‌های بازی (تکنفره، چندنفره) |
| `themes` | تم‌های بازی (فانتزی، علمی‑تخیلی) |
| `franchise` | نام فرنچایز |
| `involved_companies` | شرکت‌های سازنده و ناشر |
| `time_to_beat` | زمان تقریبی برای تمام کردن بازی (ساعت) |
| `category` | دسته‌بندی بازی (اصلی، الحاقی، دمو) |
| `status` | وضعیت انتشار |
| `alternative_names` | نام‌های جایگزین |
| `age_ratings` | رده‌بندی سنی |
| `websites` | وب‌سایت‌های مرتبط |
| `videos` | ویدئوهای یوتیوب |

---

## 🚀 راهنمای اجرا

### 1. دریافت کلید API

به [Twitch Developer Portal](https://dev.twitch.tv/console) بروید، یک اپلیکیشن جدید بسازید و مقادیر **Client ID** و **Client Secret** را کپی کنید.

### 2. تنظیم Secrets در گیت‌هاب

در مخزن خود:  
**Settings → Secrets and variables → Actions**

دو Secret بسازید:

| Secret Name | Value |
|:---|:---|
| `TWITCH_CLIENT_ID` | Client ID شما |
| `TWITCH_CLIENT_SECRET` | Client Secret شما |

### 3. اجرای دستی

- به تب **Actions** بروید
- **Fetch Games from IGDB** را انتخاب کنید
- روی دکمه سبز **Run workflow** کلیک کنید
- منتظر بمانید (۵ تا ۱۵ دقیقه)
- خروجی را از بخش **Artifacts** دانلود کنید

### 4. اجرای محلی (اختیاری)

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
pip install requests
export TWITCH_CLIENT_ID="your_client_id"
export TWITCH_CLIENT_SECRET="your_client_secret"
python fetch_games.py
```
## ⚙️ تنظیمات اسکریپت

شما می‌توانید متغیرهای زیر را در ابتدای فایل `fetch_games.py` تغییر دهید:

| متغیر | مقدار پیش‌فرض | توضیح |
|:---|:---|:---|
| `START_YEAR` | 2000 | سال شروع دریافت بازی‌ها |
| `END_YEAR` | 2026 | سال پایان دریافت بازی‌ها |
| `YEAR_CHUNK_SIZE` | 3 | تعداد سال در هر قطعه (برای دور زدن محدودیت offset) |
| `LIMIT` | 500 | حداکثر بازی در هر درخواست (قابل تغییر نیست) |
| `REQUEST_DELAY` | 0.3 | تاخیر بین درخواست‌ها به ثانیه |
| `CHUNK_DELAY` | 1.0 | تاخیر بین هر بازه سالیانه |

> 💡 **پیشنهاد:** اگر می‌خواهید فقط یک بازه کوچک را تست کنید، مثلاً `START_YEAR = 2024` و `END_YEAR = 2025` قرار دهید.

## 📊 حجم داده‌ها و زمان اجرا

| بازه زمانی | تعداد تقریبی بازی‌ها | زمان تقریبی اجرا |
|:---|:---|:---|
| ۲۰۰۰ – ۲۰۲۶ | ~۳۰۰,۰۰۰ | ۱۰ – ۱۵ دقیقه |
| ۲۰۲۰ – ۲۰۲۶ | ~۵۰,۰۰۰ | ۲ – ۳ دقیقه |
| ۲۰۲۴ – ۲۰۲۵ | ~۱۰,۰۰۰ | کمتر از ۱ دقیقه |

## 📄 فایل‌های خروجی

پس از اجرای موفق، دو فایل JSON دریافت خواهید کرد:

| فایل | توضیح |
|:---|:---|
| `games_2000_2026.json` | داده‌های کامل تمام بازی‌ها |
| `stats_2000_2026.json` | آمار و اطلاعات خلاصه شده (محبوب‌ترین پلتفرم‌ها، ژانرها، تعداد بازی‌های دارای امتیاز و ...) |

---
## 🧠 معماری و نحوه کار

**اجرای اسکریپت در GitHub Actions به این صورت است:**

1. **Checkout** ← دریافت کدهای مخزن
2. **Setup Python** ← نصب پایتون نسخه ۳.۱۱
3. **Install dependencies** ← نصب کتابخانه requests
4. **Run script** ← اجرای اسکریپت fetch_games.py
5. **Upload artifact** ← ذخیره فایل‌های JSON به عنوان Artifact

**مسیر داده‌ها:**
GitHub Repository (شما)
↓
GitHub Runner (اجرای اسکریپت)
↓
Twitch/IGDB API (دریافت اطلاعات)
↓
فایل JSON (خروجی نهایی)
↓
Artifact (قابل دانلود)


**نقش هر بخش:**

- **fetch_games.py** ← اسکریپت اصلی پایتون
- **.github/workflows/fetch-games.yml** ← تنظیمات اجرای خودکار
- **GitHub Runner** ← محیط اجرا (Ubuntu)
- **Twitch/IGDB API** ← منبع داده بازی‌ها
- **Artifact** ← خروجی قابل دانلود
---
## 🛠️ توسعه و سفارشی‌سازی

**افزودن فیلد جدید**

`fields = ["id", "name", "cover.url"]`

**تغییر سال**

`START_YEAR = 2020`

**فیلتر پلتفرم (PC)**

`where platforms = (6)`

**کد پلتفرم‌ها**

| پلتفرم | کد |
|:---|:---|
| PC | 6 |
| PS4 | 48 |
| PS5 | 167 |
| Xbox One | 49 |
| Nintendo Switch | 130 |
---
## ❓ سوالات متداول

**آیا این اسکریپت تمام بازی‌های دنیا را دریافت می‌کند؟**  
خیر، فقط بازی‌هایی که در دیتابیس IGDB ثبت شده‌اند.

**آیا استفاده از این اسکریپت رایگان است؟**  
بله، برای استفاده غیرتجاری.

**خطای Rate Limit گرفتم، چه کنم؟**  
مقدار `REQUEST_DELAY` را در اسکریپت افزایش دهید.

**می‌توانم از داده‌ها در سایت خود استفاده کنم؟**  
بله، با ذکر منبع IGDB.

---

## 📜 قوانین و اعتباردهی

این پروژه تحت مجوز **MIT** منتشر شده است.

---

## 🤝 مشارکت در پروژه

1. مخزن رو Fork کنید
2. یک Branch جدید بسازید (git checkout -b feature/amazing-feature)
3. تغییرات را Commit کنید (git commit -m 'Add amazing feature')
4. Push کنید (git push origin feature/amazing-feature)
5. Pull Request بزنید
