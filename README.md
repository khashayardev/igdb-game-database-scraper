<div dir="rtl" align="center">
  
# 🎮 کاوشگر بازی‌های IGDB – IGDB Game Fetcher

### ابزاری قدرتمند برای دریافت و ذخیره‌سازی دیتابیس بازی‌ها از ۲۰۰۰ تا ۲۰۲۶

[![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Automated-blue?logo=githubactions)](https://github.com/features/actions)
[![Python](https://img.shields.io/badge/Python-3.11%2B-green?logo=python)](https://www.python.org/)
[![IGDB](https://img.shields.io/badge/IGDB-API-purple?logo=twitch)](https://igdb.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

</div>

---

## 📖 معرفی پروژه

**فارسی**  
این پروژه یک اسکریپت پایتون خودکار است که با استفاده از **API رسمی IGDB** (که از طریق توئیچ قابل دسترسی است) اطلاعات کامل بازی‌های ویدیویی منتشر شده بین سال‌های ۲۰۰۰ تا ۲۰۲۶ را دریافت کرده و در قالب یک فایل **JSON** ذخیره می‌کند.  

اسکریپت با استفاده از **GitHub Actions** به صورت خودکار اجرا می‌شود و خروجی نهایی را به عنوان **Artifact** در اختیار شما قرار می‌دهد.

**English**  
This project is an automated Python script that uses the **official IGDB API** (accessible via Twitch) to fetch complete video game data released between 2000 and 2026 and saves it as a **JSON** file.  

The script runs automatically using **GitHub Actions** and provides the final output as an **Artifact** for download.

---

## ✨ امکانات کلیدی

### فارسی
- ✅ **دریافت خودکار** تمام بازی‌های یک بازه زمانی مشخص (مثلاً ۲۰۰۰ تا ۲۰۲۶)
- ✅ **مدیریت هوشمند Pagination** و عبور از محدودیت ۵۰۰۰ تایی `offset` API با تقسیم بازه سال به قطعات کوچک‌تر
- ✅ **رعایت Rate Limit** با تاخیرهای هوشمند بین درخواست‌ها
- ✅ **خروجی JSON استاندارد** با تمام فیلدهای مهم: نام، خلاصه، ژانر، پلتفرم، کاور، امتیاز، محبوبیت و...
- ✅ **اجرا در GitHub Actions** بدون نیاز به سرور شخصی
- ✅ **قابلیت دانلود خروجی** به عنوان Artifact از بخش Actions
- ✅ **امنیت اطلاعات** با ذخیره کلیدهای API در Secrets گیت‌هاب
- ✅ **خروجی جداگانه آمار** همراه با اطلاعات مفید مانند محبوب‌ترین پلتفرم‌ها و ژانرها

### English
- ✅ **Automated fetching** of all games within a specified date range (e.g., 2000–2026)
- ✅ **Smart Pagination handling** bypassing the 5000 `offset` limit by splitting years into smaller chunks
- ✅ **Rate Limit compliance** with intelligent delays between requests
- ✅ **Standard JSON output** with all important fields: name, summary, genre, platform, cover, rating, popularity, etc.
- ✅ **GitHub Actions integration** – no personal server required
- ✅ **Artifact download** from the Actions tab
- ✅ **Security** – API keys stored as GitHub Secrets
- ✅ **Separate statistics output** with useful info like top platforms and genres

---

## 🗂️ فیلدهای دریافتی برای هر بازی

اسکریپت اطلاعات زیر را برای هر بازی ذخیره می‌کند:

| فیلد | توضیح |
|:---|:---|
| `id` | شناسه یکتا در IGDB |
| `name` | نام بازی |
| `slug` | نسخه کوتاه شده نام برای URL |
| `summary` | خلاصه کوتاه از بازی |
| `storyline` | داستان کامل (اگر وجود داشته باشد) |
| `first_release_date` | تاریخ انتشار به صورت میلادی (مثال: 2024-01-15) |
| `first_release_timestamp` | تاریخ انتشار به صورت Unix timestamp |
| `genres` | لیست ژانرهای بازی (با id و name) |
| `platforms` | لیست پلتفرم‌های قابل اجرا (PC, PS, Xbox, Nintendo, ...) |
| `cover` | اطلاعات کاور بازی (آدرس و id) |
| `screenshots` | لیست آدرس‌های اسکرین‌شات‌ها |
| `rating` | امتیاز کاربران |
| `rating_count` | تعداد آرای کاربران |
| `total_rating` | امتیاز تجمیعی (کاربران + منتقدان) |
| `total_rating_count` | تعداد کل آرای تجمیعی |
| `popularity` | میزان محبوبیت |
| `game_modes` | حالت‌های بازی (تکنفره، چندنفره، ...) |
| `themes` | تم‌های بازی (فانتزی، علمی‑تخیلی، ...) |
| `franchise` | نام فرنچایز (اگر بازی بخشی از یک مجموعه باشد) |
| `involved_companies` | لیست شرکت‌های سازنده و ناشر |
| `time_to_beat` | زمان تقریبی برای تمام کردن بازی (ساعت) |
| `category` | دسته‌بندی بازی (اصلی، بسته الحاقی، دمو، ...) |
| `status` | وضعیت انتشار بازی |
| `alternative_names` | نام‌های جایگزین بازی |
| `age_ratings` | رده‌بندی سنی (ESRB, PEGI, ...) |
| `websites` | وب‌سایت‌های مرتبط (رسمی، ویکی‌پدیا، ...) |
| `videos` | ویدئوهای یوتیوب مرتبط با بازی |

---

## 📁 ساختار خروجی JSON

```json
[
  {
    "id": 1234,
    "name": "The Witcher 3: Wild Hunt",
    "slug": "the-witcher-3-wild-hunt",
    "summary": "خلاصه بازی...",
    "storyline": "داستان کامل بازی...",
    "first_release_date": "2015-04-01",
    "first_release_timestamp": 1427846400,
    "genres": [{"id": 5, "name": "RPG"}],
    "platforms": [{"id": 6, "name": "PC"}, {"id": 48, "name": "PlayStation 4"}],
    "cover": {
      "id": 123,
      "url": "https://images.igdb.com/...",
      "image_id": "abc123"
    },
    "rating": 92.5,
    "total_rating": 91.8,
    "popularity": 4.2,
    "time_to_beat": 52
  }
]
