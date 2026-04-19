# igdb_complete_scraper.py
import requests
import json
import time
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

class IGDBCompleteScraper:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api.igdb.com/v4"
        self.access_token = None
        self._get_access_token()
        
        # لیست همه چیزهایی که می‌خواهیم از API بگیریم
        self.fields = [
            "id", "name", "slug", "summary", "storyline", "first_release_date",
            "genres.id", "genres.name",
            "platforms.id", "platforms.name", "platforms.platform_logo.url",
            "cover.id", "cover.url", "cover.image_id",
            "screenshots.id", "screenshots.url", "screenshots.image_id",
            "artworks.id", "artworks.url", "artworks.image_id",
            "videos.id", "videos.video_id", "videos.name",
            "websites.id", "websites.url", "websites.category",
            "involved_companies.id", "involved_companies.company.id", "involved_companies.company.name",
            "involved_companies.developer", "involved_companies.publisher",
            "franchise.id", "franchise.name",
            "game_modes.id", "game_modes.name",
            "themes.id", "themes.name",
            "rating", "rating_count", "total_rating", "total_rating_count", "popularity",
            "time_to_beat", "category", "status", "version_title",
            "alternative_names.name",
            "age_ratings.id", "age_ratings.rating", "age_ratings.synopsis",
            "language_support.id", "language_support.language_id", "language_support.language.name"
        ]
        
        self.stats = {'total_games': 0, 'years_processed': 0, 'api_calls': 0}

    def _get_access_token(self):
        """دریافت توکن دسترسی از توئیچ"""
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        response = requests.post(url, params=params)
        response.raise_for_status()
        self.access_token = response.json()["access_token"]
        print(f"✅ توکن دسترسی دریافت شد")

    def _make_request(self, endpoint: str, query: str) -> List[Dict]:
        """ارسال درخواست به API IGDB"""
        headers = {
            "Client-ID": self.client_id,
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "text/plain"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/{endpoint}",
                headers=headers,
                data=query,
                timeout=30
            )
            self.stats['api_calls'] += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                # توکن منقضی شده، توکن جدید بگیر
                self._get_access_token()
                return self._make_request(endpoint, query)
            elif response.status_code == 429:
                time.sleep(2)
                return self._make_request(endpoint, query)
            else:
                print(f"      ⚠️ خطا {response.status_code}: {response.text[:100]}")
                return []
        except Exception as e:
            print(f"      ❌ خطا: {e}")
            return []

    def fetch_games_by_year(self, year: int, min_rating: float = 0, limit: int = 500) -> List[Dict]:
        """دریافت لیست بازی‌های یک سال با فیلتر امتیاز"""
        start_timestamp = int(datetime(year, 1, 1).timestamp())
        end_timestamp = int(datetime(year, 12, 31, 23, 59, 59).timestamp())
        
        print(f"   🔍 سال {year}: حداقل امتیاز >= {min_rating}")
        
        all_games = []
        offset = 0
        
        while True:
            # ساخت کوئری با pagination
            rating_filter = f"& rating >= {min_rating}" if min_rating > 0 else ""
            query = f"""
                fields id, name, rating, first_release_date;
                where first_release_date >= {start_timestamp} & first_release_date <= {end_timestamp}{rating_filter};
                sort rating desc;
                limit 500;
                offset {offset};
            """
            
            games = self._make_request("games", query)
            
            if not games:
                break
            
            all_games.extend(games)
            print(f"      📄 offset {offset} - {len(games)} بازی (مجموع: {len(all_games)})")
            
            if len(games) < 500:
                break
                
            offset += 500
            time.sleep(0.2)  # تاخیر برای رعایت rate limit
        
        # حذف تکراری‌ها و محدود کردن به خروجی
        unique_games = {g['id']: g for g in all_games}.values()
        result = sorted(list(unique_games), key=lambda x: x.get('rating', 0), reverse=True)[:limit]
        print(f"      ✅ {len(result)} بازی با امتیاز >= {min_rating} برای سال {year}")
        return result

    def get_complete_game_details(self, game_id: int) -> Dict:
        """
        دریافت کامل‌ترین اطلاعات ممکن برای یک بازی
        معادل append_to_response در TMDB
        """
        # ساخت کوئری برای دریافت تمام فیلدها
        query = f"""
            fields {','.join(self.fields)};
            where id = {game_id};
        """
        
        result = self._make_request("games", query)
        
        if not result or len(result) == 0:
            return {}
        
        game = result[0]
        
        # ----- اضافه کردن لینک‌های کامل تصاویر -----
        if game.get('cover') and game['cover'].get('url'):
            url = game['cover']['url']
            if url.startswith('//'):
                url = f"https:{url}"
            game['cover_url'] = url
        
        if game.get('screenshots'):
            game['screenshots_urls'] = []
            for ss in game['screenshots']:
                if ss.get('url'):
                    url = ss['url']
                    if url.startswith('//'):
                        url = f"https:{url}"
                    game['screenshots_urls'].append(url)
        
        if game.get('artworks'):
            game['artworks_urls'] = []
            for art in game['artworks']:
                if art.get('url'):
                    url = art['url']
                    if url.startswith('//'):
                        url = f"https:{url}"
                    game['artworks_urls'].append(url)
        
        # 1. اطلاعات ویدیوها (trailers, gameplay)
        if game.get('videos'):
            game['videos_summary'] = [
                {
                    'name': v.get('name', 'Unknown'),
                    'video_id': v.get('video_id'),
                    'url': f"https://www.youtube.com/watch?v={v.get('video_id')}" if v.get('video_id') else None
                }
                for v in game['videos']
            ]
        
        # 2. اطلاعات شرکت‌های سازنده
        if game.get('involved_companies'):
            developers = [c['company']['name'] for c in game['involved_companies'] if c.get('developer')]
            publishers = [c['company']['name'] for c in game['involved_companies'] if c.get('publisher')]
            game['companies_summary'] = {
                'developers': developers,
                'publishers': publishers,
                'total_companies': len(game['involved_companies'])
            }
        
        # 3. اطلاعات ژانرها
        if game.get('genres'):
            game['genres_summary'] = [g['name'] for g in game['genres']]
        
        # 4. اطلاعات پلتفرم‌ها
        if game.get('platforms'):
            game['platforms_summary'] = [p['name'] for p in game['platforms']]
        
        # 5. اطلاعات حالت‌های بازی
        if game.get('game_modes'):
            game['game_modes_summary'] = [m['name'] for m in game['game_modes']]
        
        # 6. اطلاعات تم‌ها
        if game.get('themes'):
            game['themes_summary'] = [t['name'] for t in game['themes']]
        
        # 7. اطلاعات فرنچایز
        if game.get('franchise'):
            game['franchise_name'] = game['franchise']['name']
        
        # 8. اطلاعات نام‌های جایگزین
        if game.get('alternative_names'):
            game['alternative_names_summary'] = [n['name'] for n in game['alternative_names']]
        
        # 9. اطلاعات رده‌بندی سنی
        if game.get('age_ratings'):
            game['age_ratings_summary'] = [
                {'rating': ar.get('rating'), 'synopsis': ar.get('synopsis')}
                for ar in game['age_ratings']
            ]
        
        # 10. تبدیل تاریخ انتشار به فرمت خوانا
        if game.get('first_release_date'):
            try:
                game['release_date_readable'] = datetime.fromtimestamp(
                    game['first_release_date']
                ).strftime("%Y-%m-%d")
            except:
                game['release_date_readable'] = None
        
        # 11. اضافه کردن متادیتای اسکرپر
        game['_scraped_at'] = datetime.now().isoformat()
        
        return game

    def scrape_yearly_archive(self, start_year: int, end_year: int, min_rating: float = 0):
        """اجرای اصلی اسکرپینگ"""
        print(f"\n🎮 شروع ساخت آرشیو کامل بازی‌ها از {start_year} تا {end_year}")
        print(f"⭐ فیلتر: بازی‌های با امتیاز >= {min_rating}")
        print("="*60)
        
        archive = {
            'metadata': {
                'source': 'IGDB (Twitch API)',
                'start_year': start_year,
                'end_year': end_year,
                'total_years': end_year - start_year + 1,
                'min_rating': min_rating,
                'extraction_date': datetime.now().isoformat(),
                'description': 'آرشیو کامل بازی‌ها با تمام اطلاعات (تصاویر، ویدیوها، شرکت‌ها، ژانرها و...)'
            },
            'games': []
        }
        
        for year in range(start_year, end_year + 1):
            print(f"\n📅 سال {year}:")
            
            # مرحله 1: دریافت لیست بازی‌های سال
            games = self.fetch_games_by_year(year, min_rating=min_rating, limit=500)
            
            # مرحله 2: دریافت جزئیات کامل برای هر بازی
            detailed_games = []
            total = len(games)
            for i, game in enumerate(games, 1):
                print(f"      🔄 [{i}/{total}] دریافت اطلاعات کامل: {game.get('name', 'Unknown')[:45]}...")
                details = self.get_complete_game_details(game['id'])
                if details:
                    detailed_games.append(details)
                time.sleep(0.1)  # تاخیر برای جلوگیری از overload
            
            archive['games'].extend(detailed_games)
            self.stats['total_games'] += len(detailed_games)
            self.stats['years_processed'] += 1
            print(f"   ✅ {len(detailed_games)} بازی کامل برای سال {year} ذخیره شد")
        
        archive['metadata']['statistics'] = self.stats
        self.save_archive(archive)
        return archive

    def save_archive(self, archive: Dict):
        """ذخیره آرشیو نهایی"""
        filename = f"complete_games_archive_{archive['metadata']['start_year']}_{archive['metadata']['end_year']}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(archive, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 آرشیو نهایی در فایل {filename} ذخیره شد.")
        print(f"\n📊 آمار نهایی:")
        print(f"   📅 سال‌های پردازش شده: {archive['metadata']['total_years']}")
        print(f"   🎮 تعداد کل بازی‌ها: {archive['metadata']['statistics']['total_games']}")
        print(f"   🌐 تعداد درخواست‌های API: {archive['metadata']['statistics']['api_calls']}")
        print(f"   ⭐ حداقل امتیاز: {archive['metadata']['min_rating']}")
        return filename


def main():
    CLIENT_ID = os.environ.get('TWITCH_CLIENT_ID')
    CLIENT_SECRET = os.environ.get('TWITCH_CLIENT_SECRET')
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ خطا: TWITCH_CLIENT_ID و TWITCH_CLIENT_SECRET پیدا نشد!")
        sys.exit(1)
    
    # دریافت سال‌ها از آرگومان‌ها
    if len(sys.argv) >= 3:
        start_year = int(sys.argv[1])
        end_year = int(sys.argv[2])
    else:
        start_year = 2000
        end_year = 2026
    
    min_rating = 0  # 0 یعنی بدون فیلتر امتیاز
    if len(sys.argv) >= 4:
        min_rating = float(sys.argv[3])
    
    scraper = IGDBCompleteScraper(CLIENT_ID, CLIENT_SECRET)
    scraper.scrape_yearly_archive(start_year, end_year, min_rating)
    print("\n✅ فرآیند کامل شد! فایل JSON آماده دانلود است.")


if __name__ == "__main__":
    main()
