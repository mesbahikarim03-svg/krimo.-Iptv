!pip install pyrogram tgcrypto nest_asyncio python-telegram-bot aiohttp requests -U

import re
import os
import uuid
import asyncio
import zipfile
import random
import base64
import time
import signal
import sys
from datetime import datetime
from collections import defaultdict
import requests
import aiohttp
import nest_asyncio

from pyrogram import Client, enums
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.error import BadRequest

try:
    from keep_alive import keep_alive
    HAS_KEEP_ALIVE = True
except ImportError:
    HAS_KEEP_ALIVE = False

# تفعيل بيئة كولاب/كاجل لحل مشكلة اللوب
nest_asyncio.apply()

# ================== بياناتك السرية (البوت والرفع) ==================
TOKEN = os.environ.get("MY_TELEGRAM_TOKEN")
GITHUB_TOKEN = os.environ.get("MY_GITHUB_TOKEN")
GITHUB_USER = "Mesbahikarim03-svg"
REPO_NAME = "krimo.-Iptv"
SESSION_STRING = s_str
# ================== نظام التنبيهات (الإغلاق والتشغيل الآمن) ==================
def graceful_shutdown(signum, frame):
    print("\n🔴 جاري إيقاف النظام وإرسال إشعار الانطفاء...")
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_ID,
            "text": "⚠️ <b>تنبيه طوارئ:</b>\nتم إيقاف تشغيل الاستضافة أو السكربت! البوت الآن خارج الخدمة 🔴",
            "parse_mode": "HTML"
        }
        requests.post(url, json=payload, timeout=5)
    except: pass
    sys.exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)
signal.signal(signal.SIGTERM, graceful_shutdown)

# ================== بيانات حساب Pyrogram (للصيد) ==================
API_ID = 24974564
API_HASH = "b87511de89b42178862e13e84147952b"
SESSION_STRING = "BAF9FOQAA1-dQDj5AXFWmCGf0F3ZsTtWy_adL3O-w71T_gjPivgB2bQ3VIULT5TMVwiP1czcO9DKKAxOY5Tn5KiS6WRPBcgaoQRxJ2sVyEyW7IYVUgFrZ_Nbo_gsOoii3SWc67N7eVr6LAmSYCnpX2z-Yq8KJbgtuikZDhsNcJ6ttVb0TeGDCXoilx5pNRXjYpEbQvEZO_qhDIkYvdoiYLpgQnX5cbnHr8vS8LOT5DwZoNfehydaPnT_f-b8BJJGvV_D0kVF6pHxqxnsSgUYPtuojnED_RwPlM9u-KrZV7Ab_WiKu54Ryl1xr0ZxfFffxvGYQAFX1TT-X5FPQQmAgpNZACUuNAAAAABEOrkgAA"

# ================== إعدادات ==================
MAX_GROUPS_PER_PAGE = 10
MAX_FILE_SIZE_MB = 150  # تم الرفع لـ 150 لدعم الملفات الكبيرة
MIN_CHANNELS_REQUIRED = 1000

# ================== إعدادات الصيد (Hunter) ==================
MY_CHANNELS = [
    "عالم iptv مجاني",
    "دردشة مجانية عبر الإنترنت",
    "تحديث مجاني لعالم البث عبر الإنترنت"
]

TARGET_KEYWORDS = [
    "iptv", "m3u", "xtream", "mac", "portal", "sat", "tv",
    "server", "stb", "cccam", "streaming", "restream", "codes", "vip", "app"
]

# ================== فلتر الحماية الشرس (النووي) ==================
ADULT_WORDS = [
    "xxx", "porn", "adult", "adults", "sex", "18+", "+18", "erotic", "playboy", "amateur",
    "onlyfans", "brazzers", "vivid", "hustler", "penthouse", "babes",
    "realitykings", "naughty", "bangbros", "milf", "lesbian", "gay", "cam",
    "nsfw", "x-art", "babe", "pussy", "dick", "matures", "hardcore", "xnxx",
    "xvideos", "pornhub", "redtube", "kamasutra", "peep"
]

ADULT_REGEX = re.compile(r'(?i)(?:' + '|'.join(map(re.escape, ADULT_WORDS)) + r')')
GROUP_TITLE_REGEX = re.compile(r'group-title="([^"]*)"')
CHANNEL_ID = "@free_iptv_world"
CHANNEL_NAME_FOR_FILE = "FREE_IPTV_WORLD"

# ================== القوالب ==================
WARNING_TEXT = """<blockquote>⚠️ <b>ATTENTION / انتباه:</b>
Links are valid for <b>10 HOURS</b> from publishing, then they will be deleted automatically. Download them NOW!
مدة الروابط 10 ساعات فقط من وقت النشر ثم سيتم حذفها. يرجى التحميل أو النسخ الآن!</blockquote>\n\n"""

POST_CAPTION = """💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗜𝗣𝗧𝗩 𝗦𝗘𝗥𝗩𝗘𝗥 💎
🌍 𝗙𝗥𝗘𝗘 𝗜𝗣𝗧𝗩 𝗪𝗢𝗥𝗟𝗗 🌍

<blockquote>⚠️ <b>إبراء ذمة:</b>
نبرأ إلى الله من أي استخدام سيء للملفات. قد تحتوي السيرفرات على قنوات غير لائقة، الرجاء تجاوزها.. كل شخص مسؤول عن نفسه. 🤲</blockquote>

<blockquote>📊 𝗦𝗲𝗿𝘃𝗲𝗿 𝗗𝗲𝘁𝗮𝗶𝗹𝘀:
├ 📦 𝗖𝗼𝗻𝘁𝗲𝗻𝘁: {count} Channels & VODs
├ ⚡ 𝗙𝗼𝗿𝗺𝗮𝘁: M3U & Xtream Codes
├ ⚽️ 𝗦𝗽𝗼𝗿𝘁𝘀: beIN, SSC, Sky, TNT
├ 🎬 𝗠𝗼𝘃𝗶𝗲𝘀: Netflix, OSN, Disney+
└ 📱 𝗗𝗲𝘃𝗶𝗰𝗲𝘀: Smart TV, Android, iOS, PC

🌍 𝗪𝗼𝗿𝗹𝗱𝘄𝗶𝗱𝗲 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀 (𝗩𝗜𝗣):
🇩🇿 الجزائر | 🇲🇦 المغرب | 🇹🇳 تونس | 🇪🇬 مصر | 🇸🇦 السعودية | 🇦🇪 الإمارات
🇫🇷 France | 🇬🇧 UK | 🇺🇸 USA | 🇩🇪 Germany | 🇮🇹 Italy | 🇪🇸 Spain
🇨🇦 Canada | 🇳🇱 Netherlands | 🇧🇪 Belgium | 🇸🇪 Sweden | 🇨🇭 Swiss
🇧🇷 Brazil | 🇦🇷 Argentina | 🇹🇷 Turkey | 🇷🇺 Russia | 🇯🇵 Japan
🇹🇷 Türkiye
... 𝗔𝗻𝗱 𝗠𝗮𝗻𝘆 𝗠𝗼𝗿𝗲! 🔥</blockquote>

👇 𝗗𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝗙𝗶𝗹𝗲 𝗕𝗲𝗹𝗼𝘄 👇
♻️ 𝘗𝘭𝘦𝘢𝘴𝘦 𝘚𝘩𝘢𝘳𝘦 & 𝘚𝘶𝘱𝘱𝘰𝘳𝘵 𝘜𝘴!"""

LINK_POST_CAPTION = """🔗 𝗗𝗜𝗥𝗘𝗖𝗧 𝗜𝗣𝗧𝗩 𝗟𝗜𝗡𝗞𝗦 🔗
🌍 𝗙𝗥𝗘𝗘 𝗜𝗣𝗧𝗩 𝗪𝗢𝗥𝗟𝗗 🌍

<blockquote>⚠️ <b>إبراء ذمة:</b>
نبرأ إلى الله من أي استخدام سيء أو الدخول لقنوات غير لائقة. 🤲</blockquote>

🚀 𝗛𝗶𝗴𝗵-𝗦𝗽𝗲𝗲𝗱 𝗟𝗶𝗻𝗸𝘀:
{links}

<blockquote>📊 𝗦𝗲𝗿𝘃𝗲𝗿 𝗗𝗲𝘁𝗮𝗶𝗹𝘀:
├ 📦 𝗖𝗼𝗻𝘁𝗲𝗻𝘁: Premium Channels & VODs
├ ⚡ 𝗙𝗼𝗿𝗺𝗮𝘁: M3U & Xtream Codes
├ ⚽️ 𝗦𝗽𝗼𝗿𝘁𝘀: beIN, SSC, Sky, TNT
├ 🎬 𝗠𝗼𝘃𝗶𝗲𝘀: Netflix, OSN, Disney+
└ 📱 𝗗𝗲𝘃𝗶𝗰𝗲𝘀: Smart TV, Android, iOS, PC

🌍 𝗪𝗼𝗿𝗹𝗱𝘄𝗶𝗱𝗲 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀 (𝗩𝗜𝗣):
🇩🇿 الجزائر | 🇲🇦 المغرب | 🇹🇳 تونس | 🇪🇬 مصر | 🇸🇦 السعودية | 🇦🇪 الإمارات
🇫🇷 France | 🇬🇧 UK | 🇺🇸 USA | 🇩🇪 Germany | 🇮🇹 Italy | 🇪🇸 Spain
🇨🇦 Canada | 🇳🇱 Netherlands | 🇧🇪 Belgium | 🇸🇪 Sweden | 🇨🇭 Swiss
🇹🇷 Türkiye |
... 𝗔𝗻𝗱 𝗠𝗮𝗻𝘆 𝗠𝗼𝗿𝗲! 🔥</blockquote>

⚙️ 𝗛𝗼𝘄 𝘁𝗼 𝘂𝘀𝗲?
1️⃣ Copy the link above.
2️⃣ Open your IPTV Player (Smarters, Tivimate, VLC).
3️⃣ Select "Add Playlist / M3U URL".
4️⃣ Paste & Enjoy! 🍿

♻️ 𝘗𝘭𝘦𝘢𝘴𝘦 𝘚𝘩𝘢𝘳𝘦 & 𝘚𝘶𝘱𝘱𝘰𝘳𝘵 𝘜𝘴!"""

# ================== المتغيرات العالمية ==================
sessions = {}
pending_urls = defaultdict(list)
user_active_session = {}
hunter_tested_urls = set()
user_app = Client("wassim_fast_scraper", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# ================== دوال التنظيف ==================
def clean_server_files():
    count = 0
    for filename in os.listdir('.'):
        if filename.endswith('.m3u') or filename.endswith('.m3u8') or filename.endswith('.zip') or filename.startswith('temp_'):
            try:
                os.remove(filename)
                count += 1
            except:
                pass
    return count

def safe_delete(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass

# ================== دالة فحص جودة الرابط ==================
async def is_link_working(url):
    try:
        timeout = aiohttp.ClientTimeout(total=15)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return True
                else:
                    return False
    except:
        return False

# ================== الرفع السحابي المدرع ==================
async def upload_to_cloud(filename, selected_api="all"):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return None

    size_mb = os.path.getsize(filename) / (1024 * 1024)
    base_name = os.path.basename(filename)
    custom_timeout = aiohttp.ClientTimeout(total=120)

    apis_to_try = ["github", "catbox_m3u8", "pixeldrain", "uguu"] if selected_api == "all" else [selected_api]

    for api in apis_to_try:
        if api == "github" and size_mb > 95:
            continue

        for attempt in range(1, 4):
            try:
                link = None
                # --- 1. GITHUB ---
                if api == "github":
                    unique_id = str(uuid.uuid4().hex)[:6]
                    safe_name = f"FIW_{int(time.time())}_{attempt}_{unique_id}_{base_name}"
                    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{safe_name}"

                    with open(filename, "rb") as f:
                        encoded_content = base64.b64encode(f.read()).decode('utf-8')

                    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
                    payload = {"message": f"Auto Upload {safe_name}", "content": encoded_content}

                    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
                        async with session.put(api_url, json=payload, headers=headers) as response:
                            if response.status in [201, 200]:
                                link = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{safe_name}"
                            elif response.status == 403 or response.status == 429:
                                await asyncio.sleep(15 * attempt)
                                continue
                            elif response.status >= 500:
                                await asyncio.sleep(8)
                                continue

                # --- 2. CATBOX M3U8 ---
                elif api == "catbox_m3u8":
                    upload_name_m3u8 = base_name.replace(".m3u", ".m3u8").replace(".txt", ".m3u8")
                    def upload_catbox_sync():
                        url = "https://catbox.moe/user/api.php"
                        data_payload = {'reqtype': 'fileupload', 'userhash': '4743fd4cd7b648c176c6e5800'}
                        headers_req = {'User-Agent': 'Mozilla/5.0'}
                        with open(filename, 'rb') as f:
                            files_req = {'fileToUpload': (upload_name_m3u8, f, 'application/vnd.apple.mpegurl')}
                            resp = requests.post(url, data=data_payload, files=files_req, headers=headers_req)
                            if resp.status_code == 200 and resp.text.startswith("http"):
                                return resp.text.strip()
                        return None
                    link = await asyncio.to_thread(upload_catbox_sync)

                # --- 2.1. CATBOX TXT ---
                elif api == "catbox_txt":
                    upload_name_txt = base_name.replace(".m3u", ".txt").replace(".m3u8", ".txt")
                    def upload_catbox_txt_sync():
                        url = "https://catbox.moe/user/api.php"
                        data_payload = {'reqtype': 'fileupload', 'userhash': '4743fd4cd7b648c176c6e5800'}
                        headers_req = {'User-Agent': 'Mozilla/5.0'}
                        with open(filename, 'rb') as f:
                            files_req = {'fileToUpload': (upload_name_txt, f, 'text/plain')}
                            resp = requests.post(url, data=data_payload, files=files_req, headers=headers_req)
                            if resp.status_code == 200 and resp.text.startswith("http"):
                                return resp.text.strip()
                        return None
                    link = await asyncio.to_thread(upload_catbox_txt_sync)

                # --- 3. PIXELDRAIN ---
                elif api == "pixeldrain":
                    url = "https://pixeldrain.com/api/file"
                    API_KEY = "6bd803d9-4e6e-402f-a7b1-c355ac2dae63"
                    auth = aiohttp.BasicAuth(login="", password=API_KEY)
                    async with aiohttp.ClientSession(auth=auth, timeout=custom_timeout) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('file', f, filename=base_name)
                            async with session.post(url, data=data) as response:
                                if response.status in [200, 201]:
                                    res_data = await response.json()
                                    if res_data.get("success"):
                                        link = f"https://pixeldrain.com/api/file/{res_data.get('id')}"

                # --- 4. UGUU ---
                elif api == "uguu":
                    upload_name = base_name.replace(".m3u", ".m3u8")
                    headers_upload = {"User-Agent": "Mozilla/5.0"}
                    async with aiohttp.ClientSession(timeout=custom_timeout, headers=headers_upload) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('files[]', f, filename=upload_name, content_type='application/vnd.apple.mpegurl')
                            async with session.post("https://uguu.se/upload.php", data=data) as response:
                                if response.status == 200:
                                    res_data = await response.json()
                                    if res_data.get("success") and res_data.get("files"):
                                        link = res_data["files"][0]["url"]

                if link:
                    return link
                else:
                    raise Exception(f"Error")
            except Exception as e:
                await asyncio.sleep(attempt * 4)

    return None

# ================== المحلل الذكي ==================
def analyze_file(filepath):
    groups = defaultdict(list)
    seen_urls_hashes = set()
    total, duplicates, adult = 0, 0, 0
    current_extinf = ""

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#EXTM3U"):
                continue
            if line.startswith("#EXTINF"):
                current_extinf = line
            elif line.startswith("#"):
                if current_extinf:
                    current_extinf += "\n" + line
            else:
                if current_extinf:
                    url = line
                    total += 1

                    match = GROUP_TITLE_REGEX.search(current_extinf)
                    group = match.group(1) if match else "Unknown"

                    is_adult = bool(ADULT_REGEX.search(current_extinf)) or \
                               bool(ADULT_REGEX.search(url)) or \
                               bool(ADULT_REGEX.search(group))

                    if is_adult:
                        adult += 1
                    else:
                        url_hash = hash(url)
                        if url_hash in seen_urls_hashes:
                            duplicates += 1
                        else:
                            seen_urls_hashes.add(url_hash)
                            groups[group].append((current_extinf, url, False))
                    current_extinf = ""

    clean_groups = defaultdict(list)
    for g_name, entries in groups.items():
        if not bool(ADULT_REGEX.search(g_name)):
            clean_groups[g_name] = entries
        else:
            adult += len(entries)

    return clean_groups, total, duplicates, adult

async def analyze_async(filepath):
    return await asyncio.to_thread(analyze_file, filepath)

def get_clean_size_mb(groups):
    size_bytes = len("#EXTM3U\r\n")
    for g in groups.values():
        for extinf, url, is_adult in g:
            if not is_adult:
                extinf_fixed = extinf.replace('\n', '\r\n')
                size_bytes += len(extinf_fixed.encode('utf-8')) + len(url.encode('utf-8')) + 4
    return size_bytes / (1024 * 1024)

def write_m3u_and_get_count(groups, filename):
    count = 0
    promo_extinf = '#EXTINF:-1 tvg-id="Free.IPTV" tvg-name="FREE IPTV WORLD PROMO" tvg-logo="https://files.catbox.moe/goe4nn.jpg" group-title="🌟 FREE IPTV WORLD 🌟",📺 Welcome to FREE IPTV WORLD\r\n'
    promo_url = 'https://files.catbox.moe/npglfu.mp4\r\n'

    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write("#EXTM3U\r\n")
        f.write(promo_extinf + promo_url)
        count += 1

        for g in groups.keys():
            for extinf, url, is_adult in groups[g]:
                if not is_adult:
                    extinf_fixed = extinf.replace('\n', '\r\n')
                    if ',' in extinf_fixed:
                        parts = extinf_fixed.rsplit(',', 1)
                        channel_name = parts[1]
                        if "FREE IPTV WORLD" not in channel_name:
                            extinf_branded = f"{parts[0]},{channel_name} | 🌟 FREE IPTV WORLD 🌟"
                        else:
                            extinf_branded = extinf_fixed
                    else:
                        extinf_branded = extinf_fixed

                    f.write(extinf_branded + "\r\n" + url + "\r\n")
                    count += 1
    return count

def compress_if_large(filename):
    if not os.path.exists(filename):
        return filename
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        zip_filename = filename.replace(".m3u", ".zip")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filename, os.path.basename(filename))
        return zip_filename
    return filename

def get_selected_merged_groups(files):
    merged = defaultdict(list)
    for f in files:
        if f.get("selected", False):
            for g_name, entries in f["groups"].items():
                merged[g_name].extend(entries)
    return merged

def get_batch_report(files, total_submitted):
    selected_count = sum(1 for f in files if f.get("selected"))
    total_clean = 0
    total_adult = 0
    total_size_mb = 0
    report = f"📊 <b>لوحة التحليل الشاملة:</b>\n"
    report += f"📥 الروابط المستلمة: {total_submitted}\n"
    report += f"✅ السيرفرات الحية/الناجحة: {len(files)}\n"
    report += f"❌ السيرفرات الميتة/الضعيفة: {total_submitted - len(files)}\n\n"
    if len(files) <= 15:
        for f in files:
            icon = "✅" if f.get("selected") else "⬜️"
            clean_in_file = f["total"] - f["adult"]
            report += f"{icon} <b>الملف {f['id']}:</b> {clean_in_file:,} قناة | 📦 <b>{f['size_mb']:.1f} MB</b>\n"
    else:
        report += f"<i>(تم ضغط التفاصيل لكثرة الملفات الناجحة)</i>\n"
    for f in files:
        if f.get("selected"):
            total_clean += (f["total"] - f["adult"])
            total_adult += f["adult"]
            total_size_mb += f["size_mb"]
    report += f"\n📉 <b>إحصائيات الملفات المحددة ({selected_count}):</b>\n"
    report += f"📡 إجمالي القنوات الجاهزة: {total_clean:,}\n"
    report += f"📦 الحجم الإجمالي التقديري: <b>{total_size_mb:.1f} MB</b>\n"
    report += f"🔞 إجمالي الإباحي المحذوف: {total_adult:,}\n\n"
    report += "⚙️ <b>كيف تريد معالجة الملفات المحددة؟ 👇</b>"
    return report

async def is_playlist_alive(groups):
    test_urls = []
    all_valid_urls = []
    for g in groups.values():
        for _, curl, _ in g:
            if curl.lower().startswith("http"):
                all_valid_urls.append(curl)
    if not all_valid_urls:
        return False
    sample_size = min(6, len(all_valid_urls)) # تقليل لزيادة السرعة
    test_urls = random.sample(all_valid_urls, sample_size)
    headers = {
        "User-Agent": "TiviMate/4.7.0 (Linux; Android 11)",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }
    timeout = aiohttp.ClientTimeout(sock_connect=3, sock_read=4)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as stream_session:
        async def check(url):
            try:
                async with stream_session.get(url, allow_redirects=True) as resp:
                    if resp.status in [200, 206, 301, 302, 303, 307, 308]:
                        chunk = await resp.content.read(256)
                        if chunk:
                            if b"<html>" not in chunk.lower() and b"<!doctype" not in chunk.lower():
                                return True
            except:
                pass
            return False
        results = await asyncio.gather(*[check(u) for u in test_urls])
        return any(results)

async def fetch_and_analyze(session, url, idx):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }
    try:
        custom_timeout = aiohttp.ClientTimeout(total=40)
        async with session.get(url, headers=headers, allow_redirects=True, timeout=custom_timeout) as response:
            if response.status in [200, 206]:
                temp_path = f"temp_url_{uuid.uuid4().hex}.m3u"
                with open(temp_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024 * 1024):
                        f.write(chunk)

                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_lines = "".join([f.readline() for _ in range(50)])

                if "#EXTM3U" not in first_lines and "#EXTINF" not in first_lines:
                    safe_delete(temp_path)
                    return {"id": idx, "success": False, "error": "Not a valid M3U"}

                groups, total, duplicates, adult = await analyze_async(temp_path)
                safe_delete(temp_path)

                if total < MIN_CHANNELS_REQUIRED:
                    return {"id": idx, "success": False, "error": f"Only {total} channels"}
                is_alive = await is_playlist_alive(groups)
                if not is_alive:
                    return {"id": idx, "success": False, "error": "Dead Server"}
                size_mb = get_clean_size_mb(groups)
                return {
                    "id": idx,
                    "groups": groups,
                    "total": total,
                    "adult": adult,
                    "size_mb": size_mb,
                    "selected": True,
                    "success": True
                }
            else:
                return {"id": idx, "success": False, "error": f"Status {response.status}"}
    except Exception as e:
        return {"id": idx, "success": False, "error": "Timeout"}

# ================== لوحات التحكم ==================
def build_post_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📣 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url="https://t.me/free_iptv_world"),
            InlineKeyboardButton("💬 𝗢𝘂𝗿 𝗚𝗿𝗼𝘂𝗽", url="https://t.me/FREE_IPTV_WORLD_CHAT")
        ],
        [
            InlineKeyboardButton("🔁 𝗦𝗵𝗮𝗿𝗲 𝗣𝗼𝘀𝘁", url="https://t.me/share/url?url=https://t.me/free_iptv_world&text=🔥%20أقوى%20سيرفرات%20IPTV%20مجاناً%20🔥")
        ],
        [
            InlineKeyboardButton("⚙️ طريقة استخدام روابط", url="https://t.me/free_iptv_world/2763")
        ]
    ])

def build_single_keyboard(group_names, page=0):
    start = page * MAX_GROUPS_PER_PAGE
    end = start + MAX_GROUPS_PER_PAGE
    page_groups = group_names[start:end]
    keyboard = []
    for g in page_groups:
        idx = group_names.index(g)
        keyboard.append([InlineKeyboardButton(g, callback_data=f"grp_idx:{idx}")])
    nav = []
    if page > 0: nav.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page:{page-1}"))
    if end < len(group_names): nav.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page:{page+1}"))
    if nav: keyboard.append(nav)
    keyboard.append([
        InlineKeyboardButton("🚫 تحميل كملف", callback_data="single_dl_clean"),
        InlineKeyboardButton("🔗 استخراج كرابط", callback_data="single_dl_link")
    ])
    keyboard.append([
        InlineKeyboardButton("📢 نشر الملف بالقناة", callback_data="single_pub_clean"),
        InlineKeyboardButton("🌐 نشر الرابط بالقناة", callback_data="single_pub_link")
    ])
    return InlineKeyboardMarkup(keyboard)

def build_batch_keyboard(files, page=0):
    keyboard = []
    row = []
    for i, f_data in enumerate(files):
        icon = "✅" if f_data.get("selected") else "⬜️"
        row.append(InlineKeyboardButton(f"{icon} {f_data['id']}", callback_data=f"batch_toggle:{i}"))
        if len(row) == 5:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton("☑️ تحديد الكل", callback_data="batch_select_all"),
        InlineKeyboardButton("🔲 إلغاء التحديد", callback_data="batch_deselect_all")
    ])
    merged_groups = get_selected_merged_groups(files)
    group_names = sorted(list(merged_groups.keys()))
    if not group_names:
        keyboard.append([InlineKeyboardButton("⚠️ الرجاء تحديد ملف واحد على الأقل", callback_data="ignore")])
    else:
        start = page * MAX_GROUPS_PER_PAGE
        end = start + MAX_GROUPS_PER_PAGE
        for g in group_names[start:end]:
            idx = group_names.index(g)
            keyboard.append([InlineKeyboardButton(g, callback_data=f"bgrp:{idx}")])
        nav = []
        if page > 0: nav.append(InlineKeyboardButton("⬅️", callback_data=f"bpage:{page-1}"))
        if end < len(group_names): nav.append(InlineKeyboardButton("➡️", callback_data=f"bpage:{page+1}"))
        if nav: keyboard.append(nav)
    keyboard.append([
        InlineKeyboardButton("📥 تنزيل (ملفات)", callback_data="batch_dl_selected"),
        InlineKeyboardButton("🔗 توليد (روابط)", callback_data="batch_dl_links")
    ])
    keyboard.append([
        InlineKeyboardButton("🚀 نشر في القناة (ملفات)", callback_data="batch_pub_selected"),
        InlineKeyboardButton("🌐 نشر في القناة (روابط)", callback_data="batch_pub_links")
    ])
    return InlineKeyboardMarkup(keyboard)

# ================== استقبال الملفات أو الروابط ==================
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clean_server_files()
    chat_id = update.message.chat_id
    document = update.message.document
    file_name = document.file_name.lower() if document.file_name else ""
    file = await document.get_file()

    temp_path = f"temp_upload_{uuid.uuid4().hex}_{file_name}"
    await file.download_to_drive(temp_path)

    if file_name.endswith('.txt'):
        with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        raw_urls = re.findall(r'(https?://[^\s\'"<>]+)', content)
        urls = list(set(raw_urls))
        safe_delete(temp_path)

        if not urls:
            await update.message.reply_text("❌ لم أتمكن من العثور على أي روابط في الملف.")
            return
        pending_urls[chat_id].extend(urls)
        pending_urls[chat_id] = list(set(pending_urls[chat_id]))
        count = len(pending_urls[chat_id])
        keyboard = [
            [InlineKeyboardButton("🔍 تحليل كل روابط السلة الآن", callback_data="analyze_pending")],
            [InlineKeyboardButton("🚀 تحليل ونشر في القناة مباشرة", callback_data="auto_pub_menu")],
            [InlineKeyboardButton("➕ مواصلة إرسال الروابط", callback_data="continue_sending")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        sent_msg = await update.message.reply_text(
            f"📥 تم استخراج <b>{len(urls)}</b> رابط فريد من الملف.\n"
            f"🛒 إجمالي الروابط في السلة: <b>{count}</b>\n\n"
            f"اختر إجراء:",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        sessions[sent_msg.message_id] = {"is_cart": True}
        return

    loading_msg = await update.message.reply_text("📥 جاري تحليل الملف... ⏳")
    groups, total, duplicates, adult = await analyze_async(temp_path)
    safe_delete(temp_path)

    if total < MIN_CHANNELS_REQUIRED:
        await loading_msg.edit_text(f"❌ تم رفض الملف: يحتوي على {total} قناة فقط (الحد الأدنى {MIN_CHANNELS_REQUIRED}).")
        return

    is_alive = await is_playlist_alive(groups)
    if not is_alive:
        await loading_msg.edit_text("❌ جميع القنوات المختبرة في هذا الملف ميتة، تم رفض الملف لأنه لا يعمل.")
        return

    size_mb = get_clean_size_mb(groups)
    sorted_group_names = sorted(list(groups.keys()))
    sessions[loading_msg.message_id] = {
        "is_batch": False,
        "groups": groups,
        "group_names": sorted_group_names,
    }
    user_active_session[chat_id] = loading_msg.message_id
    report = f"📊 تحليل الملف:\n📡 القنوات: {total:,} | 📦 الحجم: {size_mb:.1f} MB | 🔞 محذوف: {adult:,}\n\nاختر إجراء:"
    await loading_msg.edit_text(report, reply_markup=build_single_keyboard(sorted_group_names, 0))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    clean_server_files()
    chat_id = update.message.chat_id
    text = update.message.text.strip()

    if bool(ADULT_REGEX.search(text)):
        await update.message.reply_text("🚫 <b>تنبيه أمني:</b> الكلمة التي تبحث عنها محظورة!", parse_mode="HTML")
        return

    raw_urls = re.findall(r'(https?://[^\s\'"<>]+)', text)
    urls = list(set(raw_urls))

    if not urls:
        keyword = text.lower()
        active_msg_id = user_active_session.get(chat_id)
        if not active_msg_id or active_msg_id not in sessions:
            await update.message.reply_text("❌ <b>عذراً!</b> يجب عليك إرسال وتحليل ملف/رابط أولاً قبل البدء بالبحث.", parse_mode="HTML")
            return

        status_msg = await update.message.reply_text(f"🔍 جاري البحث عن <b>{text}</b> في الملفات الحالية... ⏳", parse_mode="HTML")
        session = sessions[active_msg_id]
        is_batch = session.get("is_batch")
        found_groups = defaultdict(list)
        total_found = 0

        if not is_batch:
            groups = session["groups"]
            for g_name, entries in groups.items():
                for extinf, url, is_adult in entries:
                    if not is_adult and (keyword in g_name.lower() or keyword in extinf.lower()):
                        found_groups[g_name].append((extinf, url, is_adult))
                        total_found += 1
        else:
            files = session["files"]
            merged_groups = get_selected_merged_groups(files)
            for g_name, entries in merged_groups.items():
                for extinf, url, is_adult in entries:
                    if not is_adult and (keyword in g_name.lower() or keyword in extinf.lower()):
                        found_groups[g_name].append((extinf, url, is_adult))
                        total_found += 1

        if total_found == 0:
            await status_msg.edit_text(f"❌ لم يتم العثور على أي قناة أو باقة تحتوي على: <b>{text}</b>", parse_mode="HTML")
            return

        unique_code = str(uuid.uuid4().hex)[:4].upper()
        safe_keyword = re.sub(r'[/\?%*:|"<>]', '', text)[:20]
        fname = f"Search_{safe_keyword}_{unique_code}.m3u"

        await asyncio.to_thread(write_m3u_and_get_count, found_groups, fname)
        final_fname = await asyncio.to_thread(compress_if_large, fname)

        try:
            markup = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 توليد رابط لنتيجة البحث", callback_data="ulink_search")]])
            with open(final_fname, "rb") as f_send:
                sent_msg = await update.message.reply_document(
                    document=f_send,
                    caption=f"🔍 <b>نتيجة البحث عن:</b> {text}\n📺 <b>عدد القنوات المكتشفة:</b> {total_found:,}",
                    parse_mode="HTML",
                    reply_markup=markup
                )
                sessions[sent_msg.message_id] = {
                    "is_search": True,
                    "groups": found_groups,
                    "keyword": text
                }
            await status_msg.delete()
        except Exception as e:
            await status_msg.edit_text(f"❌ خطأ في البحث: {e}")
        finally:
            safe_delete(fname)
            if final_fname != fname: safe_delete(final_fname)
        return

    pending_urls[chat_id].extend(urls)
    pending_urls[chat_id] = list(set(pending_urls[chat_id]))
    count = len(pending_urls[chat_id])
    keyboard = [
        [InlineKeyboardButton("🔍 تحليل كل روابط السلة الآن", callback_data="analyze_pending")],
        [InlineKeyboardButton("🚀 تحليل ونشر في القناة مباشرة", callback_data="auto_pub_menu")],
        [InlineKeyboardButton("➕ مواصلة إرسال الروابط", callback_data="continue_sending")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    sent_msg = await update.message.reply_text(
        f"📥 تم استقبال <b>{len(urls)}</b> رابط فريد.\n"
        f"🛒 إجمالي الروابط في السلة: <b>{count}</b>\n\n"
        f"اختر إجراء:",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    sessions[sent_msg.message_id] = {"is_cart": True}

async def safe_answer(query, text=None, show_alert=False):
    try:
        if text:
            await query.answer(text, show_alert=show_alert)
        else:
            await query.answer()
    except BadRequest:
        pass

# ================== أوامر الأساسية والتنظيف ==================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🚀 <b>مرحباً بك في بوت الـ IPTV الشامل!</b>\n\n"
        "أرسل لي أي ملف (M3U / TXT) أو مجموعة روابط وسأقوم بتحليلها وتنقيتها فوراً.\n\n"
        "🛠️ <b>الأوامر المتاحة:</b>\n"
        "🔸 /hunt [العدد] - صيد واختبار ونشر مباشر للقناة.\n"
        "🔸 /hunttxt [العدد] - صيد وتوليد ملف نصي بالروابط.\n"
        "🔸 /scrape [العدد] - سحب سريع جداً للروابط إلى السلة.\n"
        "🔸 /clean - مسح مؤقتات الخادم.\n"
        "🔸 /start - عرض هذه الرسالة."
    )
    keyboard = [[InlineKeyboardButton("🧹 Clean Server Storage", callback_data="clean_server_now")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="HTML")

async def clean_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    deleted = clean_server_files()
    await update.message.reply_text(f"🧹 Server checked and cleaned!\n🗑️ Deleted extra files: {deleted}")

# ================== أوامر الصيد والسحب المدمجة (بنظام التوربو ⚡) ==================

# 1. أمر /scrape السريع
async def scrape_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("⚠️ **تنبيه:** يرجى إرسال العدد المطلوب للروابط.\nمثال:\n`/scrape 100`", parse_mode="Markdown")
        return

    target_count = int(context.args[0])
    status_msg = await update.message.reply_text(f"⚡ **بدأ السحب السريع للروابط!**\nالهدف: جلب {target_count} رابط وإضافتهم لسلة الفحص.\n⏳ جاري الاتصال بالحساب...", parse_mode="Markdown")
    asyncio.create_task(run_fast_scraper(chat_id, target_count, status_msg, context))

async def run_fast_scraper(chat_id, target_count, status_msg, context):
    if not user_app.is_connected:
        await user_app.start()

    all_links = []
    scanned_channels = 0

    try:
        async for dialog in user_app.get_dialogs():
            chat = dialog.chat
            if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
            chat_name = chat.title or chat.username or str(chat.id)
            if any(my_chat.lower() in chat_name.lower() for my_chat in MY_CHANNELS): continue
            if not any(keyword in chat_name.lower() for keyword in TARGET_KEYWORDS): continue

            scanned_channels += 1
            try: await status_msg.edit_text(f"🔍 **سحب من:** {chat_name}\n📊 تم جمع: {len(all_links)} / {target_count}", parse_mode="Markdown")
            except: pass

            async for msg in user_app.get_chat_history(chat.id, limit=100):
                text_to_analyze = str(msg.text or msg.caption)
                if not text_to_analyze.strip(): continue

                urls = re.findall(r'(https?://[^\s]+)', text_to_analyze)
                for u in urls:
                    if 'm3u' in u.lower() or 'get.php' in u.lower():
                        all_links.append(u)

                host = re.search(r'(https?://[a-zA-Z0-9.-]+(:\d+)?)/?', text_to_analyze)
                user = re.search(r'(?:user|username|usr)[:\s=]+([a-zA-Z0-9_.-]+)', text_to_analyze, re.IGNORECASE)
                pw = re.search(r'(?:pass|password|pwd)[:\s=]+([a-zA-Z0-9_.-]+)', text_to_analyze, re.IGNORECASE)
                if host and user and pw:
                    all_links.append(f"{host.group(1)}/get.php?username={user.group(1)}&password={pw.group(1)}&type=m3u_plus&output=ts")

                if len(all_links) >= target_count * 2:
                    break

            if len(all_links) >= target_count * 2:
                break

        unique_links = list(set(all_links))
        random.shuffle(unique_links)
        final_links = unique_links[:target_count]

        if not final_links:
            await status_msg.edit_text("❌ لم يتم العثور على سيرفرات جديدة في القنوات الآن.")
            return

        pending_urls[chat_id].extend(final_links)
        pending_urls[chat_id] = list(set(pending_urls[chat_id]))
        count = len(pending_urls[chat_id])

        keyboard = [
            [InlineKeyboardButton("🔍 تحليل كل روابط السلة الآن", callback_data="analyze_pending")],
            [InlineKeyboardButton("🚀 تحليل ونشر في القناة مباشرة", callback_data="auto_pub_menu")],
            [InlineKeyboardButton("➕ مواصلة إرسال الروابط", callback_data="continue_sending")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        sent_msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚡ <b>تم الصيد السريع بنجاح!</b>\n🔥 تمت إضافة <b>{len(final_links)}</b> سيرفر إلى السلة.\n🛒 إجمالي الروابط في السلة: <b>{count}</b>\n\n👇 اختر إجراء:",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        sessions[sent_msg.message_id] = {"is_cart": True}
        await status_msg.delete()

    except Exception as e:
        await status_msg.edit_text(f"❌ حدث خطأ أثناء السحب السريع: {e}")

# 2. أمر /hunt للنشر التلقائي في القناة (تحديث التوربو + العناوين)
async def hunt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if not context.args:
        await update.message.reply_text("⚠️ **تنبيه:** يرجى إرسال الأمر متبوعاً بالعدد، أو الكلمة البحثية ثم العدد.\nمثال:\n`/hunt 5`\n`/hunt osn 3`", parse_mode="Markdown")
        return

    if context.args[-1].isdigit():
        target_count = int(context.args[-1])
        keyword = " ".join(context.args[:-1]).lower() if len(context.args) > 1 else None
    elif context.args[0].isdigit():
        target_count = int(context.args[0])
        keyword = " ".join(context.args[1:]).lower() if len(context.args) > 1 else None
    else:
        await update.message.reply_text("⚠️ **تنبيه:** يجب تحديد عدد الروابط برقم صحيح.\nمثال:\n`/hunt osn 3`", parse_mode="Markdown")
        return

    if keyword:
        status_msg = await update.message.reply_text(f"🚀 **بدأ الصيد الآلي المخصص (Turbo Mode)!**\n🎯 الهدف: جلب {target_count} سيرفرات تحتوي على <b>{keyword}</b> ونشرها في القناة.\n⏳ جاري الإعداد...", parse_mode="HTML")
    else:
        status_msg = await update.message.reply_text(f"🚀 **بدأ الصيد الآلي السريع!**\n🎯 الهدف: جلب وتجهيز {target_count} سيرفرات ونشرها في القناة.\n⏳ جاري الإعداد...", parse_mode="Markdown")

    asyncio.create_task(run_hunter(chat_id, target_count, keyword, status_msg, context))

async def run_hunter(chat_id, target_count, keyword, status_msg, context):
    if not user_app.is_connected:
        await user_app.start()

    found_count = 0
    scanned_channels = 0
    collected_links = []

    async with aiohttp.ClientSession() as session_req:
        async for dialog in user_app.get_dialogs():
            if found_count >= target_count: break
            chat = dialog.chat
            if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
            chat_name = chat.title or chat.username or str(chat.id)
            if any(my_chat.lower() in chat_name.lower() for my_chat in MY_CHANNELS): continue
            if not any(kw in chat_name.lower() for kw in TARGET_KEYWORDS): continue

            scanned_channels += 1
            try:
                await status_msg.edit_text(f"🔍 **جاري فحص القناة:** {chat_name}\n📊 القنوات المفحوصة: {scanned_channels}\n✅ المجهز للآن: {found_count}/{target_count}", parse_mode="Markdown")
            except: pass

            channel_urls = set()
            try:
                async for msg in user_app.get_chat_history(chat.id, limit=60):
                    text_to_analyze = str(msg.text or msg.caption)
                    if not text_to_analyze.strip(): continue

                    urls = re.findall(r'(https?://[^\s]+)', text_to_analyze)
                    for u in urls:
                        if 'm3u' in u.lower() or 'get.php' in u.lower():
                            channel_urls.add(u)

                    host = re.search(r'(https?://[a-zA-Z0-9.-]+(:\d+)?)/?', text_to_analyze)
                    user = re.search(r'(?:user|username|usr)[:\s=]+([a-zA-Z0-9_.-]+)', text_to_analyze, re.IGNORECASE)
                    pw = re.search(r'(?:pass|password|pwd)[:\s=]+([a-zA-Z0-9_.-]+)', text_to_analyze, re.IGNORECASE)

                    if host and user and pw:
                        channel_urls.add(f"{host.group(1)}/get.php?username={user.group(1)}&password={pw.group(1)}&type=m3u_plus&output=ts")
            except: pass

            # نظام التوربو ⚡ (الفحص المتوازي)
            valid_urls = list(channel_urls - hunter_tested_urls)
            hunter_tested_urls.update(valid_urls)

            if valid_urls and found_count < target_count:
                try:
                    msg_text = f"⚙️ **يتم الآن تحليل {len(valid_urls)} سيرفر بالتوازي...**\n✅ المجهز: {found_count}/{target_count}"
                    if keyword: msg_text = f"⚙️ **جاري البحث عن باقات ({keyword}) في {len(valid_urls)} سيرفر...**\n✅ المجهز: {found_count}/{target_count}"
                    await status_msg.edit_text(msg_text, parse_mode="Markdown")
                except: pass

                tasks = [fetch_and_analyze(session_req, u, found_count+1+i) for i, u in enumerate(valid_urls)]
                results = await asyncio.gather(*tasks)

                for res in results:
                    if found_count >= target_count: break
                    if res and res.get("success"):
                        groups_to_write = {k: v for k, v in res["groups"].items()}

                        if keyword:
                            filtered_groups = defaultdict(list)
                            has_keyword = False
                            for g_name, entries in groups_to_write.items():
                                for extinf, curl, is_adult in entries:
                                    if keyword in g_name.lower() or keyword in extinf.lower():
                                        filtered_groups[g_name].append((extinf, curl, is_adult))
                                        has_keyword = True
                            if not has_keyword:
                                continue
                            groups_to_write = filtered_groups

                        unique_code = str(uuid.uuid4().hex)[:4].upper()
                        fname = f"{CHANNEL_NAME_FOR_FILE}_Hunter_{unique_code}.m3u"
                        
                        await asyncio.to_thread(write_m3u_and_get_count, groups_to_write, fname)
                        final_fname = await asyncio.to_thread(compress_if_large, fname)
                        link = await upload_to_cloud(final_fname, "all")

                        safe_delete(fname)
                        if final_fname != fname: safe_delete(final_fname)

                        if link and await is_link_working(link):
                            collected_links.append(f"🔹 <b>الباقة {found_count + 1}:</b> <code>{link}</code>")
                            found_count += 1
                            try: await status_msg.edit_text(f"🎉 **تم صيد وتجهيز سيرفر قوي!**\n✅ المجهز للنشر: {found_count}/{target_count}", parse_mode="Markdown")
                            except: pass

        if collected_links:
            try:
                await status_msg.edit_text(f"🚀 **انتهى الصيد!**\nجاري نشر {len(collected_links)} روابط في القناة دفعة واحدة...", parse_mode="Markdown")
                chunk_size = 10
                for i in range(0, len(collected_links), chunk_size):
                    chunk_links = collected_links[i:i + chunk_size]
                    links_text = "\n\n".join(chunk_links)

                    caption = LINK_POST_CAPTION.replace("{links}", links_text)
                    
                    # تعديل العنوان في حالة تحديد باقة
                    if keyword:
                        custom_header = f"🔥 𝗘𝗫𝗖𝗟𝗨𝗦𝗜𝗩𝗘 𝗦𝗘𝗥𝗩𝗘𝗥: {keyword.upper()} 🔥"
                        caption = caption.replace("🔗 𝗗𝗜𝗥𝗘𝗖𝗧 𝗜𝗣𝗧𝗩 𝗟𝗜𝗡𝗞𝗦 🔗", custom_header)
                        caption = caption.replace("Premium Channels & VODs", f"Focus: {keyword.upper()} Channels")

                    if any("pixeldrain" in l or "litterbox" in l or "uguu" in l for l in chunk_links):
                        caption = WARNING_TEXT + caption

                    await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_post_keyboard())
                    await asyncio.sleep(3)

                await status_msg.edit_text(f"🏁 **اكتملت مهمة الصيد الأسطورية!**\nتم جلب، فحص، ونشر {found_count} سيرفر بنجاح في القناة.", parse_mode="Markdown")
            except Exception as e:
                await status_msg.edit_text(f"❌ حدث خطأ أثناء النشر النهائي: {e}")
        else:
            await status_msg.edit_text(f"❌ **انتهى البحث ولم أجد أي سيرفرات تلبي طلبك للأسف!**", parse_mode="Markdown")

# 3. أمر /hunttxt لتوليد الروابط كملف نصي (تحديث التوربو)
async def hunttxt_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if not context.args:
        await update.message.reply_text("⚠️ **تنبيه:** يرجى إرسال الأمر متبوعاً بالعدد، أو الكلمة البحثية ثم العدد.\nمثال:\n`/hunttxt 5`\n`/hunttxt bein sport 10`", parse_mode="Markdown")
        return

    if context.args[-1].isdigit():
        target_count = int(context.args[-1])
        keyword = " ".join(context.args[:-1]).lower() if len(context.args) > 1 else None
    elif context.args[0].isdigit():
        target_count = int(context.args[0])
        keyword = " ".join(context.args[1:]).lower() if len(context.args) > 1 else None
    else:
        await update.message.reply_text("⚠️ **تنبيه:** يجب تحديد عدد الروابط برقم صحيح.\nمثال:\n`/hunttxt bein sport 10`", parse_mode="Markdown")
        return

    if keyword:
        status_msg = await update.message.reply_text(f"🚀 **بدأ صيد الروابط المخصص!**\n🎯 الهدف: استخراج {target_count} باقات تحتوي على <b>{keyword}</b> ووضع روابطها في ملف TXT.\n⏳ جاري الإعداد...", parse_mode="HTML")
    else:
        status_msg = await update.message.reply_text(f"🚀 **بدأ صيد الروابط السحابية!**\n🎯 الهدف: جلب ورفع {target_count} سيرفرات ووضع روابطها في ملف TXT لك.\n⏳ جاري الإعداد...", parse_mode="Markdown")

    asyncio.create_task(run_hunter_txt(chat_id, target_count, keyword, status_msg, context))

async def run_hunter_txt(chat_id, target_count, keyword, status_msg, context):
    if not user_app.is_connected:
        await user_app.start()

    found_count = 0
    scanned_channels = 0
    collected_links_raw = []

    async with aiohttp.ClientSession() as session_req:
        async for dialog in user_app.get_dialogs():
            if found_count >= target_count: break
            chat = dialog.chat
            if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
            chat_name = chat.title or chat.username or str(chat.id)
            if any(my_chat.lower() in chat_name.lower() for my_chat in MY_CHANNELS): continue
            if not any(kw in chat_name.lower() for kw in TARGET_KEYWORDS): continue

            scanned_channels += 1
            try: await status_msg.edit_text(f"🔍 **جاري فحص القناة:** {chat_name}\n📊 القنوات المفحوصة: {scanned_channels}\n✅ المستخرج للآن: {found_count}/{target_count}", parse_mode="Markdown")
            except: pass

            channel_urls = set()
            try:
                async for msg in user_app.get_chat_history(chat.id, limit=60):
                    text_to_analyze = str(msg.text or msg.caption)
                    if not text_to_analyze.strip(): continue

                    urls = re.findall(r'(https?://[^\s]+)', text_to_analyze)
                    for u in urls:
                        if 'm3u' in u.lower() or 'get.php' in u.lower(): channel_urls.add(u)

                    host = re.search(r'(https?://[a-zA-Z0-9.-]+(:\d+)?)/?', text_to_analyze)
                    user = re.search(r'(?:user|username|usr)[:\s=]+([a-zA-Z0-9_.-]+)', text_to_analyze, re.IGNORECASE)
                    pw = re.search(r'(?:pass|password|pwd)[:\s=]+([a-zA-Z0-9_.-]+)', text_to_analyze, re.IGNORECASE)

                    if host and user and pw:
                        channel_urls.add(f"{host.group(1)}/get.php?username={user.group(1)}&password={pw.group(1)}&type=m3u_plus&output=ts")
            except: pass

            valid_urls = list(channel_urls - hunter_tested_urls)
            hunter_tested_urls.update(valid_urls)

            if valid_urls and found_count < target_count:
                tasks = [fetch_and_analyze(session_req, u, found_count+1+i) for i, u in enumerate(valid_urls)]
                results = await asyncio.gather(*tasks)

                for res in results:
                    if found_count >= target_count: break
                    if res and res.get("success"):
                        groups_to_write = {k: v for k, v in res["groups"].items()}

                        if keyword:
                            filtered_groups = defaultdict(list)
                            has_keyword = False
                            for g_name, entries in groups_to_write.items():
                                for extinf, curl, is_adult in entries:
                                    if keyword in g_name.lower() or keyword in extinf.lower():
                                        filtered_groups[g_name].append((extinf, curl, is_adult))
                                        has_keyword = True
                            if not has_keyword:
                                continue
                            groups_to_write = filtered_groups

                        unique_code = str(uuid.uuid4().hex)[:4].upper()
                        fname_prefix = f"Hunter_{keyword.replace(' ', '')}_" if keyword else "HunterRaw_"
                        fname = f"{fname_prefix}{unique_code}.m3u"

                        await asyncio.to_thread(write_m3u_and_get_count, groups_to_write, fname)
                        final_fname = await asyncio.to_thread(compress_if_large, fname)
                        link = await upload_to_cloud(final_fname, "all")

                        safe_delete(fname)
                        if final_fname != fname: safe_delete(final_fname)

                        if link and await is_link_working(link):
                            collected_links_raw.append(link)
                            found_count += 1
                            try: await status_msg.edit_text(f"🎉 **تم توليد رابط سحابي بنجاح!**\n✅ المستخرج: {found_count}/{target_count}", parse_mode="Markdown")
                            except: pass

        if collected_links_raw:
            safe_keyword_for_file = re.sub(r'[/\?%*:|"<>]', '', keyword)[:15] if keyword else ""
            txt_filename = f"Cloud_Links_{safe_keyword_for_file}_{target_count}_{uuid.uuid4().hex[:4]}.txt" if keyword else f"Cloud_Links_{target_count}_{uuid.uuid4().hex[:4]}.txt"

            try:
                with open(txt_filename, "w", encoding="utf-8") as f:
                    f.write("\n".join(collected_links_raw))
                with open(txt_filename, "rb") as f_send:
                    caption = f"✅ **اكتمل الصيد المخصص!**\nإليك ملف يحتوي على {len(collected_links_raw)} روابط لملفات M3U تتضمن <b>{keyword}</b> حصرياً." if keyword else f"✅ **اكتمل الصيد!**\nإليك ملف يحتوي على {len(collected_links_raw)} روابط سحابية مباشرة وفعالة."
                    await context.bot.send_document(
                        chat_id=chat_id,
                        document=f_send,
                        caption=caption,
                        parse_mode="HTML"
                    )
                await status_msg.delete()
            except Exception as e:
                await status_msg.edit_text(f"❌ حدث خطأ أثناء إنشاء ملف النصوص: {e}")
            finally:
                safe_delete(txt_filename)
        else:
            await status_msg.edit_text(f"❌ **انتهى البحث ولم أجد أي سيرفرات تلبي طلبك للأسف!**", parse_mode="Markdown")

# ================== الأزرار الرئيسية ==================
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    msg_id = query.message.message_id
    data = query.data

    if data == "ignore":
        await safe_answer(query)
        return
    if data == "clean_server_now":
        deleted_count = clean_server_files()
        await safe_answer(query, f"🧹 تم تنظيف الاستضافة بنجاح!\n🗑️ تم مسح {deleted_count} ملفات زائدة.", show_alert=True)
        return
    if data == "continue_sending":
        await safe_answer(query, "✅ أرسل المزيد من الروابط وسأقوم بحفظها في السلة...", show_alert=False)
        return
    if data == "analyze_pending":
        urls = pending_urls.pop(chat_id, [])
        total_urls = len(urls)
        if total_urls == 0:
            await safe_answer(query, "⚠️ السلة فارغة! أرسل روابط أولاً.", show_alert=True)
            return

        if total_urls == 1:
            await query.edit_message_text("⚡ جاري فحص الرابط بسرعة فائقة... ⏳")
            async with aiohttp.ClientSession() as session_req:
                result = await fetch_and_analyze(session_req, urls[0], 1)
            if result.get("success"):
                sessions[msg_id] = {
                    "is_batch": False,
                    "groups": result["groups"],
                    "group_names": sorted(list(result["groups"].keys())),
                }
                user_active_session[chat_id] = msg_id
                report = f"📊 تحليل الرابط:\n📡 القنوات: {result['total']:,} | 📦 الحجم: {result['size_mb']:.1f} MB | 🔞 محذوف: {result['adult']:,}\n\nاختر إجراء:"
                await query.edit_message_text(report, reply_markup=build_single_keyboard(sorted(list(result["groups"].keys())), 0))
            else:
                await query.edit_message_text(f"❌ فشل تحميل الرابط.\nالسبب: {result.get('error', 'ميت أو غير صالح')}")
        else:
            await query.edit_message_text(f"🚀 سيتم فحص {total_urls} رابط بأمان لتجنب الضغط على السيرفر (0/{total_urls}) ⏳")
            batch_files = []
            semaphore = asyncio.Semaphore(25)
            progress = [0]
            update_interval = max(1, total_urls // 10)

            async def safe_fetch(session_req, url, idx):
                async with semaphore:
                    res = await fetch_and_analyze(session_req, url, idx)
                    progress[0] += 1
                    if progress[0] % update_interval == 0 or progress[0] == total_urls:
                        try: await query.edit_message_text(f"🚀 جاري الفحص واستبعاد الملفات الميتة... ({progress[0]}/{total_urls}) ⏳")
                        except: pass
                    return res

            conn = aiohttp.TCPConnector(limit=50)
            async with aiohttp.ClientSession(connector=conn) as session_req:
                tasks = [safe_fetch(session_req, url, idx) for idx, url in enumerate(urls, 1)]
                results = await asyncio.gather(*tasks)

            for res in results:
                if res.get("success"): batch_files.append(res)

            if not batch_files:
                await query.edit_message_text(f"❌ انتهى الفحص.\nجميع الروابط التي تم فحصها ({total_urls}) ميتة أو ضعيفة جداً.")
                return

            sessions[msg_id] = {"is_batch": True, "files": batch_files, "total_submitted": total_urls, "page": 0}
            user_active_session[chat_id] = msg_id
            report_text = get_batch_report(batch_files, total_urls)
            await query.edit_message_text(report_text, reply_markup=build_batch_keyboard(batch_files, 0), parse_mode="HTML")
        return

    api_trigger_actions = ["auto_pub_menu", "single_dl_link", "single_pub_link", "batch_dl_links", "batch_pub_links", "ulink_search"]
    if data in api_trigger_actions:
        session = sessions.get(msg_id)
        if not session and data == "auto_pub_menu":
            sessions[msg_id] = {"is_cart": True}
            session = sessions[msg_id]
        elif not session:
            await safe_answer(query, "⚠️ انتهت الجلسة.", show_alert=True)
            return

        session["pending_action"] = data
        keyboard = [
            [InlineKeyboardButton("🐙 GitHub (دائم وأزلي خام 100%)", callback_data="api:github")],
            [InlineKeyboardButton("📺 Catbox (صيغة m3u8 شرعية)", callback_data="api:catbox_m3u8")],
            [InlineKeyboardButton("📄 Catbox (صيغة txt مخفية)", callback_data="api:catbox_txt")],
            [InlineKeyboardButton("🚀 PixelDrain (الأسرع بصيغة m3u)", callback_data="api:pixeldrain")],
            [InlineKeyboardButton("🎌 Uguu.se (مباشر وخام 100%)", callback_data="api:uguu")],
            [InlineKeyboardButton("🗑️ Litterbox (مؤقت بصيغة m3u)", callback_data="api:litterbox")],
            [InlineKeyboardButton("🌟 اختيار تلقائي (سريع وآمن)", callback_data="api:all")],
            [InlineKeyboardButton("⬅️ إلغاء العملية", callback_data="cancel_api_menu")]
        ]
        await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("api:"):
        selected_api = data.split(":")[1]
        session = sessions.get(msg_id)
        if not session:
            await safe_answer(query, "⚠️ انتهت الجلسة.", show_alert=True)
            return

        data_action = session.get("pending_action", "")
        today_date = datetime.now().strftime("%Y-%m-%d")
        unique_code = str(uuid.uuid4().hex)[:4].upper()

        if data_action == "auto_pub_menu":
            urls = pending_urls.pop(chat_id, [])
            if not urls:
                await query.edit_message_text("⚠️ السلة فارغة!")
                return
            await query.edit_message_text(f"🚀 جاري الفحص الشامل لـ {len(urls)} روابط للرفع على السيرفر المحدد... ⏳")
            batch_files = []
            semaphore = asyncio.Semaphore(25)
            progress = [0]
            async def safe_fetch(session_req, url, idx):
                async with semaphore:
                    res = await fetch_and_analyze(session_req, url, idx)
                    progress[0] += 1
                    if progress[0] % max(1, len(urls) // 5) == 0 or progress[0] == len(urls):
                        try: await query.edit_message_text(f"🔍 جاري استبعاد الروابط الميتة... ({progress[0]}/{len(urls)}) ⏳")
                        except: pass
                    return res
            conn = aiohttp.TCPConnector(limit=50)
            async with aiohttp.ClientSession(connector=conn) as session_req:
                tasks = [safe_fetch(session_req, url, idx) for idx, url in enumerate(urls, 1)]
                results = await asyncio.gather(*tasks)
            for res in results:
                if res.get("success"): batch_files.append(res)
            if not batch_files:
                await query.edit_message_text("❌ جميع الروابط ميتة أو ضعيفة جداً. تم إلغاء النشر.")
                return
            await query.edit_message_text(f"✅ نجح {len(batch_files)} سيرفر في الفحص. جاري الرفع والنشر في القناة الآن... ⏳")
            links = []
            for index, f_data in enumerate(batch_files, 1):
                try: await query.edit_message_text(f"🚀 جاري معالجة ورفع الملف {index} من {len(batch_files)}...")
                except: pass
                try:
                    fname = f"{CHANNEL_NAME_FOR_FILE}_Part{f_data['id']}_{unique_code}.m3u"
                    count = await asyncio.to_thread(write_m3u_and_get_count, {k: v for k, v in f_data["groups"].items()}, fname)
                    final_fname = await asyncio.to_thread(compress_if_large, fname)
                    link = await upload_to_cloud(final_fname, selected_api)
                    if link and await is_link_working(link):
                        links.append(f"🔹 <b>الباقة {f_data['id']}:</b> <code>{link}</code>")
                    safe_delete(fname)
                    if final_fname != fname: safe_delete(final_fname)
                except Exception as e: pass
                await asyncio.sleep(5)
            if links:
                try:
                    chunk_size = 10
                    for i in range(0, len(links), chunk_size):
                        chunk_links = links[i:i + chunk_size]
                        links_text = "\n\n".join(chunk_links)
                        caption = LINK_POST_CAPTION.replace("{links}", links_text)
                        if any("pixeldrain" in l or "litterbox" in l or "uguu" in l for l in chunk_links):
                            caption = WARNING_TEXT + caption
                        await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_post_keyboard())
                        await asyncio.sleep(3)
                    await query.edit_message_text(f"✅ تمت المهمة الأوتوماتيكية بنجاح أسطوري!\nتم فحص، رفع، ونشر {len(links)} روابط في القناة.")
                except Exception as e: await query.edit_message_text(f"❌ حدث خطأ أثناء النشر في القناة: {e}")
            else:
                await query.edit_message_text("❌ فشلت عملية الرفع بالكامل. جميع السيرفرات ترفض الاتصال حالياً.")
            return

        elif data_action == "single_dl_link":
            status_msg = await query.message.reply_text("🌐 جاري رفع الملف للسيرفر المختار لإنشاء رابط مباشر...")
            fname = f"{CHANNEL_NAME_FOR_FILE}_Clean_{unique_code}.m3u"
            await asyncio.to_thread(write_m3u_and_get_count, session["groups"], fname)
            final_fname = await asyncio.to_thread(compress_if_large, fname)
            link = await upload_to_cloud(final_fname, selected_api)
            safe_delete(fname)
            if final_fname != fname: safe_delete(final_fname)
            if link and await is_link_working(link):
                await status_msg.edit_text(f"✅ <b>الرابط المباشر جاهز:</b>\n\n<code>{link}</code>\n\n(اضغط على الرابط لنسخه)", parse_mode="HTML")
            else:
                await status_msg.edit_text("❌ الرابط تم إنشاؤه لكنه لا يعمل (معطوب). اختر سيرفراً آخر.")
            return

        elif data_action == "single_pub_link":
            status_msg = await query.message.reply_text("🌐 جاري إنشاء الرابط ونشره في القناة...")
            fname = f"{CHANNEL_NAME_FOR_FILE}_{today_date}_{unique_code}.m3u"
            count = await asyncio.to_thread(write_m3u_and_get_count, session["groups"], fname)
            final_fname = await asyncio.to_thread(compress_if_large, fname)
            link = await upload_to_cloud(final_fname, selected_api)
            safe_delete(fname)
            if final_fname != fname: safe_delete(final_fname)
            if link and await is_link_working(link):
                caption = LINK_POST_CAPTION.replace("{links}", f"<code>{link}</code>")
                if any(x in link for x in ["pixeldrain", "litterbox", "uguu"]): caption = WARNING_TEXT + caption
                await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_post_keyboard())
                await status_msg.edit_text("✅ تم نشر الرابط في القناة بنجاح!")
            else:
                await status_msg.edit_text("❌ فشل رفع الملف أو الرابط معطوب. جرب سيرفر آخر.")
            return

        elif data_action == "batch_dl_links" or data_action == "batch_pub_links":
            merged_groups = get_selected_merged_groups(session["files"])
            if not merged_groups:
                await query.message.reply_text("⚠️ لم تقم بتحديد أي ملف!")
                return
            status_msg = await query.message.reply_text("🌐 جاري دمج الملفات المحددة وإنشاء رابط سحابي...")
            fname = f"{CHANNEL_NAME_FOR_FILE}_Batch_{today_date}_{unique_code}.m3u"
            count = await asyncio.to_thread(write_m3u_and_get_count, merged_groups, fname)
            final_fname = await asyncio.to_thread(compress_if_large, fname)
            link = await upload_to_cloud(final_fname, selected_api)
            safe_delete(fname)
            if final_fname != fname: safe_delete(final_fname)
            if link and await is_link_working(link):
                if data_action == "batch_dl_links":
                    await status_msg.edit_text(f"✅ <b>الرابط المباشر للملفات المدمجة جاهز:</b>\n\n<code>{link}</code>\n\n(اضغط للنسخ)", parse_mode="HTML")
                else:
                    caption = LINK_POST_CAPTION.replace("{links}", f"<code>{link}</code>")
                    if any(x in link for x in ["pixeldrain", "litterbox", "uguu"]): caption = WARNING_TEXT + caption
                    await context.bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_post_keyboard())
                    await status_msg.edit_text("✅ تم نشر الرابط المجمع في القناة بنجاح!")
            else:
                await status_msg.edit_text("❌ فشل الرفع. جرب استخدام سيرفر آخر.")
            return

        elif data_action == "ulink_search":
            found_groups = session["groups"]
            safe_keyword = re.sub(r'[/\?%*:|"<>]', '', session["keyword"])[:20]
            status_msg = await query.message.reply_text("🌐 جاري رفع نتيجة البحث...")
            fname = f"Search_{safe_keyword}_{unique_code}.m3u"
            await asyncio.to_thread(write_m3u_and_get_count, found_groups, fname)
            final_fname = await asyncio.to_thread(compress_if_large, fname)
            link = await upload_to_cloud(final_fname, selected_api)
            safe_delete(fname)
            if final_fname != fname: safe_delete(final_fname)
            if link and await is_link_working(link):
                await status_msg.edit_text(f"✅ <b>الرابط لنتائج البحث:</b>\n\n<code>{link}</code>", parse_mode="HTML")
            else:
                await status_msg.edit_text("❌ فشل الرفع.")
            return

    if data == "cancel_api_menu":
        session = sessions.get(msg_id)
        if not session: return
        if session.get("is_search"):
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 توليد رابط لنتيجة البحث", callback_data="ulink_search")]]))
        elif session.get("is_batch"):
            await query.edit_message_reply_markup(reply_markup=build_batch_keyboard(session["files"], session.get("page", 0)))
        elif session.get("is_cart"):
            keyboard = [
                [InlineKeyboardButton("🔍 تحليل كل روابط السلة الآن", callback_data="analyze_pending")],
                [InlineKeyboardButton("🚀 تحليل ونشر في القناة مباشرة", callback_data="auto_pub_menu")],
                [InlineKeyboardButton("➕ مواصلة إرسال الروابط", callback_data="continue_sending")]
            ]
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_reply_markup(reply_markup=build_single_keyboard(session["group_names"], session.get("page", 0)))
        return

    session = sessions.get(msg_id)
    if not session:
        await safe_answer(query, "⚠️ انتهت الجلسة.", show_alert=True)
        return

    today_date = datetime.now().strftime("%Y-%m-%d")
    unique_code = str(uuid.uuid4().hex)[:4].upper()

    if not session.get("is_batch"):
        if data.startswith("page:"):
            page = int(data.split(":")[1])
            await query.edit_message_reply_markup(reply_markup=build_single_keyboard(session["group_names"], page))
            return

        if data == "single_dl_clean":
            status_msg = await query.message.reply_text("⏳ جاري تجهيز الملف للتحميل...")
            fname = f"{CHANNEL_NAME_FOR_FILE}_Clean_{unique_code}.m3u"
            await asyncio.to_thread(write_m3u_and_get_count, session["groups"], fname)
            final_fname = await asyncio.to_thread(compress_if_large, fname)
            try:
                with open(final_fname, "rb") as f_send:
                    await query.message.reply_document(document=f_send)
                await status_msg.edit_text("✅ تم الإرسال بنجاح!")
            except Exception as e:
                await status_msg.edit_text(f"❌ خطأ: {e}")
            finally:
                safe_delete(fname)
                if final_fname != fname: safe_delete(final_fname)
            return

        if data == "single_pub_clean":
            status_msg = await query.message.reply_text("🚀 جاري النشر في القناة (كملف)...")
            fname = f"{CHANNEL_NAME_FOR_FILE}_{today_date}_{unique_code}.m3u"
            count = await asyncio.to_thread(write_m3u_and_get_count, session["groups"], fname)
            final_fname = await asyncio.to_thread(compress_if_large, fname)
            try:
                caption = POST_CAPTION.replace("{count}", f"{count:,}")
                if final_fname.endswith('.zip'): caption += "\n\n📦 <b>Note:</b> File compressed to ZIP due to large size."
                with open(final_fname, "rb") as f_send:
                    await context.bot.send_document(chat_id=CHANNEL_ID, document=f_send, caption=caption, parse_mode="HTML", reply_markup=build_post_keyboard())
                await status_msg.edit_text("✅ تم النشر في القناة بنجاح!")
            except Exception as e:
                await status_msg.edit_text(f"❌ خطأ: {e}")
            finally:
                safe_delete(fname)
                if final_fname != fname: safe_delete(final_fname)
            return

    else:
        if data.startswith("batch_toggle:"):
            idx = int(data.split(":")[1])
            session["files"][idx]["selected"] = not session["files"][idx].get("selected", False)
            await query.edit_message_reply_markup(reply_markup=build_batch_keyboard(session["files"], session.get("page", 0)))
            return

        if data == "batch_select_all":
            for f in session["files"]: f["selected"] = True
            await query.edit_message_reply_markup(reply_markup=build_batch_keyboard(session["files"], session.get("page", 0)))
            return

        if data == "batch_deselect_all":
            for f in session["files"]: f["selected"] = False
            await query.edit_message_reply_markup(reply_markup=build_batch_keyboard(session["files"], session.get("page", 0)))
            return

        if data.startswith("bpage:"):
            page = int(data.split(":")[1])
            session["page"] = page
            await query.edit_message_reply_markup(reply_markup=build_batch_keyboard(session["files"], page))
            return

        if data == "batch_dl_selected":
            selected_files = [f for f in session["files"] if f.get("selected")]
            if not selected_files:
                await query.message.reply_text("⚠️ لم تقم بتحديد أي ملف!")
                return
            status_msg = await query.message.reply_text("⏳ جاري تجهيز الملفات المحددة للتحميل الفردي...")

            for f_data in selected_files:
                fname = f"{CHANNEL_NAME_FOR_FILE}_Part{f_data['id']}_{unique_code}.m3u"
                await asyncio.to_thread(write_m3u_and_get_count, f_data["groups"], fname)
                final_fname = await asyncio.to_thread(compress_if_large, fname)
                try:
                    with open(final_fname, "rb") as f_send:
                        await query.message.reply_document(document=f_send)
                except Exception as e:
                    await query.message.reply_text(f"❌ خطأ في إرسال الملف {f_data['id']}: {e}")
                finally:
                    safe_delete(fname)
                    if final_fname != fname: safe_delete(final_fname)

            await status_msg.edit_text("✅ تم إرسال جميع الملفات المحددة بنجاح!")
            return

        if data == "batch_pub_selected":
            selected_files = [f for f in session["files"] if f.get("selected")]
            if not selected_files:
                await query.message.reply_text("⚠️ لم تقم بتحديد أي ملف!")
                return
            status_msg = await query.message.reply_text("🚀 جاري تجهيز الملفات كألبوم للنشر في القناة...")

            media_group = []
            open_files = []
            temp_paths = []
            total_count = 0

            try:
                for idx, f_data in enumerate(selected_files):
                    fname = f"{CHANNEL_NAME_FOR_FILE}_Part{f_data['id']}_{unique_code}.m3u"
                    count = await asyncio.to_thread(write_m3u_and_get_count, f_data["groups"], fname)
                    total_count += count
                    final_fname = await asyncio.to_thread(compress_if_large, fname)
                    temp_paths.append((fname, final_fname))

                    f_open = open(final_fname, "rb")
                    open_files.append(f_open)

                caption = POST_CAPTION.replace("{count}", f"{total_count:,}")

                for idx, f_open in enumerate(open_files):
                    if idx == 0:
                        media_group.append(InputMediaDocument(media=f_open, caption=caption, parse_mode="HTML"))
                    else:
                        media_group.append(InputMediaDocument(media=f_open))

                chunk_size = 10
                for i in range(0, len(media_group), chunk_size):
                    chunk = media_group[i:i + chunk_size]
                    await context.bot.send_media_group(chat_id=CHANNEL_ID, media=chunk)
                    await asyncio.sleep(3)

                await status_msg.edit_text("✅ تم النشر في القناة كألبوم بنجاح!")
            except Exception as e:
                await status_msg.edit_text(f"❌ خطأ: {e}")
            finally:
                for f_open in open_files:
                    f_open.close()
                for fname, final_fname in temp_paths:
                    safe_delete(fname)
                    if final_fname != fname: safe_delete(final_fname)
            return

# ================== الدالة الرئيسية لتشغيل البوت ==================
async def send_startup_notification(app):
    print("🟢 جاري إرسال إشعار التشغيل...")
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        payload = {"chat_id": ADMIN_ID, "text": "✅ <b>نظام المايسترو متصل!</b>\nالاستضافة تعمل الآن والبوت مستعد لاستقبال الأوامر 🟢", "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=5)
    except: pass

def main():
    if HAS_KEEP_ALIVE:
        keep_alive()

    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .read_timeout(60)
        .write_timeout(60)
        .connect_timeout(60)
        .pool_timeout(60)
        .build()
    )
    
    # إرسال التنبيه عند تشغيل السيرفر
    import asyncio
    asyncio.get_event_loop().run_until_complete(send_startup_notification(application))

    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("clean", clean_command_handler))
    application.add_handler(CommandHandler("hunt", hunt_command))
    application.add_handler(CommandHandler("hunttxt", hunttxt_command))
    application.add_handler(CommandHandler("scrape", scrape_command))

    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(CallbackQueryHandler(buttons))

    print("🚀 البوت الشامل يعمل الآن بكفاءة بوضع التوربو ونظام التنبيهات مفعل...")
    application.run_polling()

if __name__ == '__main__':
    main()
