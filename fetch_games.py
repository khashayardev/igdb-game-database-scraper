"""
IGDB Game Fetcher - اسکریپت دریافت کامل بازی‌ها از API آی‌جی‌دی‌بی
این اسکریپت تمام بازی‌های منتشر شده بین سال‌های مشخص شده را دریافت کرده و در فایل JSON ذخیره می‌کند.
"""

import os
import json
import requests
from datetime import datetime
import time
from typing import List, Dict, Any, Optional

# ============================================================
# تنظیمات اولیه - کاربران می‌توانند این مقادیر را تغییر دهند
# ============================================================

# سال شروع و پایان برای دریافت بازی‌ها
START_YEAR = 2000
END_YEAR = 2026

# هر بار چند سال با هم دریافت شود (برای دور زدن محدودیت 5000 تایی offset)
# مقدار 3 یا 4 معمولاً مناسب است. اگر خطای خالی برگشتن دیدید، این عدد را کوچک‌تر کنید.
YEAR_CHUNK_SIZE = 3

# حداکثر تعداد بازی در هر درخواست (مقدار مجاز توسط API، قابل تغییر نیست)
LIMIT = 500

# تاخیر بین درخواست‌ها به ثانیه (برای رعایت Rate Limit)
REQUEST_DELAY = 0.3

# تاخیر بین هر بازه سالیانه (برای استراحت بیشتر بین چانک‌ها)
CHUNK_DELAY = 1.0

# ============================================================
# توابع کمکی
# ============================================================

def get_access_token(client_id: str, client_secret: str) -> str:
    """
    دریافت توکن دسترسی از API توئیچ
    
    Args:
        client_id: شناسه کلاینت توئیچ
        client_secret: رمز کلاینت توئیچ
        
    Returns:
        توکن دسترسی به صورت رشته
        
    Raises:
        Exception: اگر توکن دریافت نشود
    """
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        token_data = response.json()
        return token_data["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"❌ خطا در دریافت توکن: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"   پاسخ سرور: {e.response.text}")
        raise
    except KeyError as e:
        print(f"❌ خطا: توکن در پاسخ سرور یافت نشد - {e}")
        raise

def build_query(offset: int, start_year: int, end_year: int) -> str:
    """
    ساخت کوئری Apicalypse برای دریافت بازی‌ها
    
    Args:
        offset: تعداد رکوردهایی که از ابتدا نادیده گرفته شوند
        start_year: سال شروع
        end_year: سال پایان
        
    Returns:
        رشته کوئری آماده برای ارسال به API
    """
    # لیست کامل فیلدهایی که دریافت می‌کنیم
    fields = [
        "id",
        "name",
        "slug",
        "summary",
        "storyline",
        "first_release_date",
        "genres.id",
        "genres.name",
        "platforms.id",
        "platforms.name",
        "platforms.platform_logo.url",
        "cover.id",
        "cover.url",
        "cover.image_id",
        "screenshots.id",
        "screenshots.url",
        "screenshots.image_id",
        "rating",
        "rating_count",
        "total_rating",
        "total_rating_count",
        "popularity",
        "game_modes.id",
        "game_modes.name",
        "themes.id",
        "themes.name",
        "franchise.id",
        "franchise.name",
        "involved_companies.company.id",
        "involved_companies.company.name",
        "involved_companies.developer",
        "involved_companies.publisher",
        "time_to_beat",
        "category",
        "status",
        "version_title",
        "alternative_names.name",
        "age_ratings.rating",
        "age_ratings.synopsis",
        "websites.url",
        "websites.category",
        "videos.video_id",
        "videos.name"
    ]
    
    # تبدیل سال به تایم‌استمپ (اول ژانویه و آخر دسامبر هر سال)
    start_timestamp = int(datetime(start_year, 1, 1).timestamp())
    end_timestamp = int(datetime(end_year, 12, 31, 23, 59, 59).timestamp())
    
    # ساخت کوئری نهایی
    query = f"""
        fields {','.join(fields)};
        where first_release_date >= {start_timestamp} & first_release_date <= {end_timestamp};
        sort first_release_date asc;
        limit {LIMIT};
        offset {offset};
    """
    
    return query

def fetch_year_chunk(
    access_token: str, 
    client_id: str, 
    start_year: int, 
    end_year: int
) -> List[Dict[str, Any]]:
    """
    دریافت تمام بازی‌های یک بازه سالیانه با مدیریت خودکار pagination
    
    Args:
        access_token: توکن دسترسی
        client_id: شناسه کلاینت
        start_year: سال شروع بازه
        end_year: سال پایان بازه
        
    Returns:
        لیست بازی‌های دریافت شده
    """
    all_games = []
    offset = 0
    url = "https://api.igdb.com/v4/games"
    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "text/plain"
    }
    
    print(f"  📅 شروع دریافت {start_year} تا {end_year}...")
    
    while True:
        query = build_query(offset, start_year, end_year)
        
        try:
            response = requests.post(url, headers=headers, data=query)
            
            if response.status_code == 401:
                print("    ❌ خطای احراز هویت. توکن ممکن است منقضی شده باشد.")
                break
            elif response.status_code == 429:
                print("    ⚠️ محدودیت نرخ درخواست! صبر می‌کنم 5 ثانیه...")
                time.sleep(5)
                continue
            elif response.status_code != 200:
                print(f"    ❌ خطا در offset {offset}: کد وضعیت {response.status_code}")
                print(f"       پاسخ: {response.text[:200]}")
                break
            
            games = response.json()
            
            if not games or len(games) == 0:
                break
            
            all_games.extend(games)
            print(f"    ✅ دریافت {len(games)} بازی (مجموع این بازه: {len(all_games)})")
            
            # اگر تعداد بازی‌های برگشتی کمتر از حد مجاز باشد، به انتها رسیده‌ایم
            if len(games) < LIMIT:
                break
            
            offset += LIMIT
            time.sleep(REQUEST_DELAY)
            
        except requests.exceptions.RequestException as e:
            print(f"    ❌ خطای شبکه: {e}")
            break
        except json.JSONDecodeError as e:
            print(f"    ❌ خطا در پردازش پاسخ JSON: {e}")
            break
    
    return all_games

def clean_game_data(games: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    پاکسازی و استانداردسازی داده‌های بازی
    
    Args:
        games: لیست خام بازی‌ها از API
        
    Returns:
        لیست پاکسازی شده
    """
    cleaned_games = []
    
    for game in games:
        cleaned = {}
        
        # فیلدهای اصلی
        cleaned["id"] = game.get("id")
        cleaned["name"] = game.get("name")
        cleaned["slug"] = game.get("slug")
        cleaned["summary"] = game.get("summary", "")
        cleaned["storyline"] = game.get("storyline", "")
        
        # تاریخ انتشار (تبدیل به فرمت خوانا و همچنین نگهداری تایم‌استمپ)
        first_release = game.get("first_release_date")
        cleaned["first_release_timestamp"] = first_release
        if first_release:
            try:
                cleaned["first_release_date"] = datetime.fromtimestamp(
                    first_release
                ).strftime("%Y-%m-%d")
            except (ValueError, OSError):
                cleaned["first_release_date"] = None
        else:
            cleaned["first_release_date"] = None
        
        # ژانرها
        if game.get("genres"):
            cleaned["genres"] = [
                {"id": g.get("id"), "name": g.get("name")} 
                for g in game["genres"] 
                if g.get("name")
            ]
        else:
            cleaned["genres"] = []
        
        # پلتفرم‌ها
        if game.get("platforms"):
            cleaned["platforms"] = [
                {"id": p.get("id"), "name": p.get("name")} 
                for p in game["platforms"] 
                if p.get("name")
            ]
        else:
            cleaned["platforms"] = []
        
        # کاور
        if game.get("cover"):
            cover_url = game["cover"].get("url")
            if cover_url:
                # تبدیل // به https:// برای استفاده در وب
                if cover_url.startswith("//"):
                    cover_url = f"https:{cover_url}"
            cleaned["cover"] = {
                "id": game["cover"].get("id"),
                "url": cover_url,
                "image_id": game["cover"].get("image_id")
            }
        else:
            cleaned["cover"] = None
        
        # اسکرین‌شات‌ها
        if game.get("screenshots"):
            cleaned["screenshots"] = [
                {
                    "id": s.get("id"),
                    "url": f"https:{s.get('url')}" if s.get('url', '').startswith('//') else s.get('url'),
                    "image_id": s.get("image_id")
                }
                for s in game["screenshots"] if s.get("url")
            ]
        else:
            cleaned["screenshots"] = []
        
        # امتیازات
        cleaned["rating"] = game.get("rating")
        cleaned["rating_count"] = game.get("rating_count")
        cleaned["total_rating"] = game.get("total_rating")
        cleaned["total_rating_count"] = game.get("total_rating_count")
        cleaned["popularity"] = game.get("popularity")
        
        # حالت‌های بازی
        if game.get("game_modes"):
            cleaned["game_modes"] = [
                {"id": m.get("id"), "name": m.get("name")} 
                for m in game["game_modes"] if m.get("name")
            ]
        else:
            cleaned["game_modes"] = []
        
        # تم‌ها
        if game.get("themes"):
            cleaned["themes"] = [
                {"id": t.get("id"), "name": t.get("name")} 
                for t in game["themes"] if t.get("name")
            ]
        else:
            cleaned["themes"] = []
        
        # فرنچایز
        if game.get("franchise"):
            cleaned["franchise"] = {
                "id": game["franchise"].get("id"),
                "name": game["franchise"].get("name")
            }
        else:
            cleaned["franchise"] = None
        
        # شرکت‌های سازنده
        if game.get("involved_companies"):
            companies = []
            for ic in game["involved_companies"]:
                company = ic.get("company", {})
                companies.append({
                    "id": company.get("id"),
                    "name": company.get("name"),
                    "is_developer": ic.get("developer", False),
                    "is_publisher": ic.get("publisher", False)
                })
            cleaned["involved_companies"] = companies
        else:
            cleaned["involved_companies"] = []
        
        # زمان لازم برای تمام کردن (ساعت)
        cleaned["time_to_beat"] = game.get("time_to_beat")
        
        # دسته‌بندی بازی (0=اصلی، 1=الحاقی، 2=دمو، 3=...)
        cleaned["category"] = game.get("category")
        
        # وضعیت انتشار
        cleaned["status"] = game.get("status")
        
        # نسخه (برای بازی‌هایی که نسخه خاصی دارند)
        cleaned["version_title"] = game.get("version_title")
        
        # نام‌های جایگزین
        if game.get("alternative_names"):
            cleaned["alternative_names"] = [
                n.get("name") for n in game["alternative_names"] if n.get("name")
            ]
        else:
            cleaned["alternative_names"] = []
        
        # رده‌بندی سنی
        if game.get("age_ratings"):
            cleaned["age_ratings"] = [
                {
                    "rating": ar.get("rating"),
                    "synopsis": ar.get("synopsis")
                }
                for ar in game["age_ratings"]
            ]
        else:
            cleaned["age_ratings"] = []
        
        # وب‌سایت‌های مرتبط
        if game.get("websites"):
            cleaned["websites"] = [
                {"url": w.get("url"), "category": w.get("category")}
                for w in game["websites"] if w.get("url")
            ]
        else:
            cleaned["websites"] = []
        
        # ویدئوها (یوتیوب)
        if game.get("videos"):
            cleaned["videos"] = [
                {
                    "video_id": v.get("video_id"),
                    "name": v.get("name")
                }
                for v in game["videos"] if v.get("video_id")
            ]
        else:
            cleaned["videos"] = []
        
        cleaned_games.append(cleaned)
    
    return cleaned_games

def save_to_json(data: List[Dict[str, Any]], filename: str) -> None:
    """
    ذخیره داده‌ها در فایل JSON
    
    Args:
        data: داده‌های آماده برای ذخیره
        filename: نام فایل خروجی
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"💾 فایل ذخیره شد: {filename} (حجم: {len(data)} بازی)")

def generate_stats(games: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    تولید آمار از داده‌های دریافت شده
    
    Args:
        games: لیست بازی‌ها
        
    Returns:
        دیکشنری حاوی آمار
    """
    stats = {
        "total_games": len(games),
        "start_year": START_YEAR,
        "end_year": END_YEAR,
        "games_with_rating": 0,
        "games_with_cover": 0,
        "games_with_screenshots": 0,
        "games_with_storyline": 0,
        "platforms": {},
        "genres": {},
        "fetch_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    for game in games:
        if game.get("rating"):
            stats["games_with_rating"] += 1
        if game.get("cover"):
            stats["games_with_cover"] += 1
        if game.get("screenshots"):
            stats["games_with_screenshots"] += 1
        if game.get("storyline"):
            stats["games_with_storyline"] += 1
        
        # آمار پلتفرم‌ها
        for platform in game.get("platforms", []):
            name = platform.get("name")
            if name:
                stats["platforms"][name] = stats["platforms"].get(name, 0) + 1
        
        # آمار ژانرها
        for genre in game.get("genres", []):
            name = genre.get("name")
            if name:
                stats["genres"][name] = stats["genres"].get(name, 0) + 1
    
    # مرتب‌سازی و محدود کردن به 10 مورد اول برای خوانایی
    stats["top_platforms"] = dict(
        sorted(stats["platforms"].items(), key=lambda x: x[1], reverse=True)[:10]
    )
    stats["top_genres"] = dict(
        sorted(stats["genres"].items(), key=lambda x: x[1], reverse=True)[:10]
    )
    
    # حذف دیتاهای خام از آمار نهایی برای کاهش حجم
    del stats["platforms"]
    del stats["genres"]
    
    return stats

# ============================================================
# تابع اصلی
# ============================================================

def main():
    """
    تابع اصلی برنامه
    """
    print("=" * 60)
    print("🎮 IGDB Game Fetcher - دریافت کننده بازی‌ها از آی‌جی‌دی‌بی")
    print("=" * 60)
    
    # دریافت کلیدهای API از متغیرهای محیطی
    client_id = os.environ.get("TWITCH_CLIENT_ID")
    client_secret = os.environ.get("TWITCH_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("❌ خطا: متغیرهای محیطی تنظیم نشده‌اند!")
        print("   لطفاً TWITCH_CLIENT_ID و TWITCH_CLIENT_SECRET را تنظیم کنید.")
        print("\n   برای اجرای محلی:")
        print("   export TWITCH_CLIENT_ID='your_client_id'")
        print("   export TWITCH_CLIENT_SECRET='your_client_secret'")
        print("\n   برای GitHub Actions:")
        print("   این مقادیر را در Secrets مخزن خود تنظیم کنید.")
        return
    
    print(f"✅ کلیدهای API دریافت شدند.")
    print(f"📅 بازه زمانی: {START_YEAR} تا {END_YEAR}")
    print(f"📦 هر قطعه: {YEAR_CHUNK_SIZE} سال")
    print(f"⚡ حداکثر بازی در هر درخواست: {LIMIT}")
    print("-" * 60)
    
    # دریافت توکن دسترسی
    try:
        print("🔑 در حال دریافت توکن دسترسی از توئیچ...")
        access_token = get_access_token(client_id, client_secret)
        print("✅ توکن دسترسی دریافت شد.")
    except Exception as e:
        print(f"❌ خطا در دریافت توکن: {e}")
        return
    
    all_games = []
    
    # تقسیم بازه اصلی به قطعات کوچک‌تر
    chunks = []
    for chunk_start in range(START_YEAR, END_YEAR + 1, YEAR_CHUNK_SIZE):
        chunk_end = min(chunk_start + YEAR_CHUNK_SIZE - 1, END_YEAR)
        chunks.append((chunk_start, chunk_end))
    
    print(f"📊 بازه اصلی به {len(chunks)} قطعه تقسیم شد:")
    for cs, ce in chunks:
        print(f"   - {cs} تا {ce}")
    print("-" * 60)
    
    # دریافت هر قطعه
    for i, (chunk_start, chunk_end) in enumerate(chunks, 1):
        print(f"\n🔄 قطعه {i} از {len(chunks)}:")
        chunk_games = fetch_year_chunk(
            access_token, 
            client_id, 
            chunk_start, 
            chunk_end
        )
        
        if chunk_games:
            all_games.extend(chunk_games)
            print(f"   📈 جمع کل بازی‌ها تا اینجا: {len(all_games)}")
        else:
            print(f"   ⚠️ هیچ بازی در این بازه یافت نشد.")
        
        # تاخیر بین قطعات
        if i < len(chunks):
            print(f"   ⏳ صبر {CHUNK_DELAY} ثانیه قبل از قطعه بعدی...")
            time.sleep(CHUNK_DELAY)
    
    print("\n" + "=" * 60)
    print(f"🎉 دریافت داده‌ها به پایان رسید!")
    print(f"📊 تعداد کل بازی‌های دریافت شده: {len(all_games)}")
    
    if len(all_games) == 0:
        print("❌ هیچ داده‌ای دریافت نشد. لطفاً تنظیمات را بررسی کنید.")
        return
    
    # پاکسازی داده‌ها
    print("🧹 در حال پاکسازی و استانداردسازی داده‌ها...")
    cleaned_games = clean_game_data(all_games)
    
    # تولید آمار
    print("📈 در حال تولید آمار...")
    stats = generate_stats(cleaned_games)
    
    # ذخیره داده اصلی
    output_file = f"games_{START_YEAR}_{END_YEAR}.json"
    save_to_json(cleaned_games, output_file)
    
    # ذخیره فایل آمار
    stats_file = f"stats_{START_YEAR}_{END_YEAR}.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"📊 فایل آمار ذخیره شد: {stats_file}")
    
    # نمایش خلاصه آمار در کنسول
    print("\n" + "=" * 60)
    print("📊 خلاصه آمار دریافت شده:")
    print(f"   🎮 تعداد کل بازی‌ها: {stats['total_games']}")
    print(f"   ⭐ بازی‌های دارای امتیاز: {stats['games_with_rating']}")
    print(f"   🖼️ بازی‌های دارای کاور: {stats['games_with_cover']}")
    print(f"   📸 بازی‌های دارای اسکرین‌شات: {stats['games_with_screenshots']}")
    print(f"   📖 بازی‌های دارای داستان کامل: {stats['games_with_storyline']}")
    
    print("\n   🎯 محبوب‌ترین پلتفرم‌ها:")
    for platform, count in list(stats['top_platforms'].items())[:5]:
        print(f"      - {platform}: {count} بازی")
    
    print("\n   🏷️ محبوب‌ترین ژانرها:")
    for genre, count in list(stats['top_genres'].items())[:5]:
        print(f"      - {genre}: {count} بازی")
    
    print("\n" + "=" * 60)
    print("✅ فرآیند با موفقیت به پایان رسید!")
    print("=" * 60)

# ============================================================
# نقطه ورود برنامه
# ============================================================

if __name__ == "__main__":
    main()
