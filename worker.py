import os
import json
import asyncio
import re
import requests
import base64
import time
import uuid
import zipfile
import random
from datetime import datetime
from collections import defaultdict
import aiohttp

from pyrogram import Client, enums
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# ================== كود الكشف والربط الذكي بالخزنة السرية ==================
print("🔍 DEBUG: جاري فحص متغيرات البيئة والخزنة السرية...")
s_str = os.environ.get("MY_SESSION_STRING", "").strip()
print(f"🔍 DEBUG: طول كود الجلسة المستلم هو: {len(s_str)} حرف")

if not s_str:
    print("❌ CRITICAL ERROR: كود الجلسة فارغ! تأكد من إعدادات Repository Secrets.")
    exit(1)

# ================== بياناتك السرية المحمية ==================
TOKEN = os.environ.get("MY_TELEGRAM_TOKEN")
GITHUB_TOKEN = os.environ.get("MY_GITHUB_TOKEN")
GITHUB_USER = "Mesbahikarim03-svg"
REPO_NAME = "krimo.-Iptv"
SESSION_STRING = s_str

MAX_GROUPS_PER_PAGE = 10
MAX_FILE_SIZE_MB = 150
MIN_CHANNELS_REQUIRED = 1000
CHANNEL_ID = "@free_iptv_world"
CHANNEL_NAME_FOR_FILE = "FREE_IPTV_WORLD"

MY_CHANNELS = ["عالم iptv مجاني", "دردشة مجانية عبر الإنترنت", "تحديث مجاني لعالم البث عبر الإنترنت"]
TARGET_KEYWORDS = ["iptv", "m3u", "xtream", "mac", "portal", "sat", "tv", "server", "stb", "cccam", "streaming", "restream", "codes", "vip", "app"]

# ================== فلتر الحماية الشرس (النووي) الأصلي ==================
ADULT_WORDS = ["xxx", "porn", "adult", "adults", "sex", "18+", "+18", "erotic", "playboy", "amateur", "onlyfans", "brazzers", "vivid", "hustler", "penthouse", "babes", "realitykings", "naughty", "bangbros", "milf", "lesbian", "gay", "cam", "nsfw", "x-art", "babe", "pussy", "dick", "matures", "hardcore", "xnxx", "xvideos", "pornhub", "redtube", "kamasutra", "peep"]
ADULT_REGEX = re.compile(r'(?i)(?:' + '|'.join(map(re.escape, ADULT_WORDS)) + r')')
GROUP_TITLE_REGEX = re.compile(r'group-title="([^"]*)"')

# ================== القوالب نتاع النشر الأصلية ==================
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

def build_post_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📣 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url="https://t.me/free_iptv_world"), InlineKeyboardButton("💬 𝗢𝘂𝗿 𝗚𝗿𝗼𝘂𝗽", url="https://t.me/FREE_IPTV_WORLD_CHAT")],
        [InlineKeyboardButton("🔁 𝗦𝗵𝗮𝗿𝗲 𝗣𝗼𝘀𝘁", url="https://t.me/share/url?url=https://t.me/free_iptv_world&text=🔥%20أقوى%20سيرفرات%20IPTV%20مجاناً%20🔥")],
        [InlineKeyboardButton("⚙️ طريقة استخدام روابط", url="https://t.me/free_iptv_world/2763")]
    ])

def stop_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🛑 إيقاف هذه العملية", callback_data="cancel_process")]])

def safe_delete(filepath):
    try:
        if os.path.exists(filepath): os.remove(filepath)
    except: pass

async def is_link_working(url):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                return response.status == 200
    except: return False

def cleanup_old_github_files():
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        resp = requests.get(api_url, headers=headers)
        if resp.status_code == 200:
            for file in resp.json():
                name = file.get("name", "")
                if name.startswith("FIW_") and name.endswith(".m3u"):
                    try:
                        if int(time.time()) - int(name.split("_")[1]) > 36000: # 10 ساعات
                            requests.delete(file.get("url"), json={"message": f"Auto-delete: {name}", "sha": file.get("sha")}, headers=headers)
                    except: continue
    except: pass

# ================== الرفع السحابي ==================
async def upload_to_cloud(filename, selected_api="all"):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0: return None
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    base_name = os.path.basename(filename)
    custom_timeout = aiohttp.ClientTimeout(total=120)
    apis_to_try = ["github", "catbox_m3u8", "catbox_txt", "pixeldrain", "uguu", "litterbox"] if selected_api == "all" else [selected_api]

    for api in apis_to_try:
        if api == "github" and size_mb > 95: continue
        for attempt in range(1, 4):
            try:
                link = None
                if api == "github":
                    cleanup_old_github_files()
                    unique_id = str(uuid.uuid4().hex)[:6]
                    safe_name = f"FIW_{int(time.time())}_{attempt}_{unique_id}_{base_name}"
                    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{safe_name}"
                    with open(filename, "rb") as f: encoded_content = base64.b64encode(f.read()).decode('utf-8')
                    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
                    payload = {"message": f"Auto Upload {safe_name}", "content": encoded_content}
                    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
                        async with session.put(api_url, json=payload, headers=headers) as response:
                            if response.status in [201, 200]: link = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{safe_name}"
                elif api == "catbox_m3u8":
                    upload_name_m3u8 = base_name.replace(".m3u", ".m3u8").replace(".txt", ".m3u8")
                    def upload_catbox_sync():
                        url = "https://catbox.moe/user/api.php"
                        data_payload = {'reqtype': 'fileupload', 'userhash': '4743fd4cd7b648c176c6e5800'}
                        with open(filename, 'rb') as f:
                            files_req = {'fileToUpload': (upload_name_m3u8, f, 'application/vnd.apple.mpegurl')}
                            resp = requests.post(url, data=data_payload, files=files_req, headers={'User-Agent': 'Mozilla/5.0'})
                            if resp.status_code == 200 and resp.text.startswith("http"): return resp.text.strip()
                        return None
                    link = await asyncio.to_thread(upload_catbox_sync)
                elif api == "catbox_txt":
                    upload_name_txt = base_name.replace(".m3u", ".txt").replace(".m3u8", ".txt")
                    def upload_catbox_txt_sync():
                        url = "https://catbox.moe/user/api.php"
                        data_payload = {'reqtype': 'fileupload', 'userhash': '4743fd4cd7b648c176c6e5800'}
                        with open(filename, 'rb') as f:
                            files_req = {'fileToUpload': (upload_name_txt, f, 'text/plain')}
                            resp = requests.post(url, data=data_payload, files=files_req, headers={'User-Agent': 'Mozilla/5.0'})
                            if resp.status_code == 200 and resp.text.startswith("http"): return resp.text.strip()
                        return None
                    link = await asyncio.to_thread(upload_catbox_txt_sync)
                elif api == "pixeldrain":
                    url = "https://pixeldrain.com/api/file"
                    auth = aiohttp.BasicAuth(login="", password="6bd803d9-4e6e-402f-a7b1-c355ac2dae63")
                    async with aiohttp.ClientSession(auth=auth, timeout=custom_timeout) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('file', f, filename=base_name)
                            async with session.post(url, data=data) as response:
                                if response.status in [200, 201]:
                                    res_data = await response.json()
                                    if res_data.get("success"): link = f"https://pixeldrain.com/api/file/{res_data.get('id')}"
                elif api == "uguu":
                    upload_name = base_name.replace(".m3u", ".m3u8")
                    async with aiohttp.ClientSession(timeout=custom_timeout, headers={"User-Agent": "Mozilla/5.0"}) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('files[]', f, filename=upload_name, content_type='application/vnd.apple.mpegurl')
                            async with session.post("https://uguu.se/upload.php", data=data) as response:
                                if response.status == 200:
                                    res_data = await response.json()
                                    if res_data.get("success") and res_data.get("files"): link = res_data["files"][0]["url"]
                elif api == "litterbox":
                    async with aiohttp.ClientSession(timeout=custom_timeout, headers={"User-Agent": "Mozilla/5.0"}) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('reqtype', 'fileupload')
                            data.add_field('time', '72h')
                            data.add_field('fileToUpload', f, filename=base_name)
                            async with session.post("https://litterbox.catbox.moe/resources/internals/api.php", data=data) as response:
                                if response.status == 200:
                                    res_text = await response.text()
                                    if res_text.startswith("http"): link = res_text.strip()
                if link: return link
                else: raise Exception("Error")
            except Exception: await asyncio.sleep(attempt * 4)
    return None

# ================== المحلل الذكي ونظام الـ Hash ==================
def analyze_file(filepath):
    groups = defaultdict(list)
    seen_urls_hashes = set()
    total, duplicates, adult = 0, 0, 0
    current_extinf = ""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#EXTM3U"): continue
            if line.startswith("#EXTINF"): current_extinf = line
            elif line.startswith("#"):
                if current_extinf: current_extinf += "\n" + line
            else:
                if current_extinf:
                    url = line
                    total += 1
                    match = GROUP_TITLE_REGEX.search(current_extinf)
                    group = match.group(1) if match else "Unknown"
                    is_adult = bool(ADULT_REGEX.search(current_extinf)) or bool(ADULT_REGEX.search(url)) or bool(ADULT_REGEX.search(group))
                    if is_adult: adult += 1
                    else:
                        url_hash = hash(url)
                        if url_hash in seen_urls_hashes: duplicates += 1
                        else:
                            seen_urls_hashes.add(url_hash)
                            groups[group].append((current_extinf, url, False))
                    current_extinf = ""
    clean_groups = defaultdict(list)
    for g_name, entries in groups.items():
        if not bool(ADULT_REGEX.search(g_name)): clean_groups[g_name] = entries
        else: adult += len(entries)
    return clean_groups, total, duplicates, adult

async def analyze_async(filepath): return await asyncio.to_thread(analyze_file, filepath)

def get_clean_size_mb(groups):
    size_bytes = len("#EXTM3U\r\n")
    for g in groups.values():
        for extinf, url, is_adult in g:
            if not is_adult:
                extinf_fixed = extinf.replace('\n', '\r\n')
                size_bytes += len(extinf_fixed.encode('utf-8')) + len(url.encode('utf-8')) + 4
    return size_bytes / (1024 * 1024)

# ================== دالة كتابة باقات الـ M3U بنظام الـ \r\n ==================
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
                        if "FREE IPTV WORLD" not in channel_name: extinf_branded = f"{parts[0]},{channel_name} | 🌟 FREE IPTV WORLD 🌟"
                        else: extinf_branded = extinf_fixed
                    else: extinf_branded = extinf_fixed
                    f.write(extinf_branded + "\r\n" + url + "\r\n")
                    count += 1
    return count

def compress_if_large(filename):
    if not os.path.exists(filename): return filename
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        zip_filename = filename.replace(".m3u", ".zip")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf: zipf.write(filename, os.path.basename(filename))
        return zip_filename
    return filename

async def is_playlist_alive(groups):
    all_valid_urls = [curl for g in groups.values() for _, curl, _ in g if curl.lower().startswith("http")]
    if not all_valid_urls: return False
    test_urls = random.sample(all_valid_urls, min(10, len(all_valid_urls)))
    headers = {"User-Agent": "TiviMate/4.7.0 (Linux; Android 11)", "Accept": "*/*", "Connection": "keep-alive"}
    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(sock_connect=3, sock_read=4)) as session:
        async def check(url):
            try:
                async with session.get(url, allow_redirects=True) as resp:
                    if resp.status in [200, 206, 301, 302, 303, 307, 308]:
                        chunk = await resp.content.read(256)
                        if chunk and b"<html>" not in chunk.lower() and b"<!doctype" not in chunk.lower(): return True
            except: pass
            return False
        results = await asyncio.gather(*[check(u) for u in test_urls])
        return any(results)

# ================== نظام الفحص المحمي بالمقص الزمني ==================
async def fetch_and_analyze(session, url, idx):
    async def _fetch():
        try:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True) as response:
                if response.status in [200, 206]:
                    temp_path = f"temp_url_{uuid.uuid4().hex}.m3u"
                    with open(temp_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(1024 * 1024): f.write(chunk)
                    with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                        first_lines = "".join([f.readline() for _ in range(50)])
                    if "#EXTM3U" not in first_lines and "#EXTINF" not in first_lines:
                        safe_delete(temp_path)
                        return {"id": idx, "success": False}
                    groups, total, duplicates, adult = await analyze_async(temp_path)
                    safe_delete(temp_path)
                    if total < MIN_CHANNELS_REQUIRED: return {"id": idx, "success": False}
                    if not await is_playlist_alive(groups): return {"id": idx, "success": False}
                    return {"id": idx, "groups": groups, "total": total, "adult": adult, "size_mb": get_clean_size_mb(groups), "success": True}
        except: pass
        return {"id": idx, "success": False}

    try:
        return await asyncio.wait_for(_fetch(), timeout=30.0)
    except asyncio.TimeoutError: return {"id": idx, "success": False, "error": "Timeout"}
    except Exception: return {"id": idx, "success": False}

# ================== أوامر الصيد والسحب المدمجة ==================
async def run_hunter_action(bot, chat_id, message_id, args):
    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🚀 **بدأ الصيد الآلي للمصنع...**\n⏳ جاري الدخول لحساب Pyrogram وقراءة القنوات الحية...", parse_mode="Markdown", reply_markup=stop_button())
        target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
        keyword = " ".join(args[:-1]).lower() if len(args) > 1 and args[-1].isdigit() else (" ".join(args[1:]).lower() if len(args) > 1 else "")
        
        app = Client("wassim_fast_scraper", api_id=24974564, api_hash="b87511de89b42178862e13e84147952b", session_string=SESSION_STRING)
        await app.start()

        found_count = 0
        scanned_channels = 0
        collected_links = []
        tested_urls = set()

        async with aiohttp.ClientSession() as session_req:
            async for dialog in app.get_dialogs():
                if found_count >= target_count: break
                chat = dialog.chat
                if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
                chat_name = chat.title or str(chat.id)
                if any(my_chat.lower() in chat_name.lower() for my_chat in MY_CHANNELS): continue
                if not any(kw in chat_name.lower() for kw in TARGET_KEYWORDS): continue

                scanned_channels += 1
                try: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🔍 **جاري فحص القناة:** {chat_name}\n📊 القنوات المفحوصة: {scanned_channels}\n✅ المجهز: {found_count}/{target_count}", parse_mode="Markdown", reply_markup=stop_button())
                except: pass

                try:
                    async for msg in app.get_chat_history(chat.id, limit=60):
                        if found_count >= target_count: break
                        text = str(msg.text or msg.caption)
                        if not text.strip(): continue
                        urls_to_test = [u for u in re.findall(r'(https?://[^\s]+)', text) if 'm3u' in u.lower() or 'get.php' in u.lower()]
                        
                        host = re.search(r'(https?://[a-zA-Z0-9.-]+(:\d+)?)/?', text)
                        user = re.search(r'(?:user|username|usr)[:\s=]+([a-zA-Z0-9_.-]+)', text, re.IGNORECASE)
                        pw = re.search(r'(?:pass|password|pwd)[:\s=]+([a-zA-Z0-9_.-]+)', text, re.IGNORECASE)
                        if host and user and pw: urls_to_test.append(f"{host.group(1)}/get.php?username={user.group(1)}&password={pw.group(1)}&type=m3u_plus&output=ts")

                        for u in set(urls_to_test):
                            if found_count >= target_count: break
                            if u in tested_urls: continue
                            tested_urls.add(u)

                            try: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"⚙️ **يتم الآن تحليل واختبار سيرفر محتمل...**\n✅ المجهز: {found_count}/{target_count}", parse_mode="Markdown", reply_markup=stop_button())
                            except: pass

                            res = await fetch_and_analyze(session_req, u, found_count+1)
                            if res.get("success"):
                                groups_to_write = {k: v for k, v in res["groups"].items()}
                                if keyword:
                                    filtered = defaultdict(list)
                                    has_keyword = False
                                    for g_name, entries in groups_to_write.items():
                                        for extinf, curl, is_adult in entries:
                                            if keyword in g_name.lower() or keyword in extinf.lower():
                                                filtered[g_name].append((extinf, curl, is_adult))
                                                has_keyword = True
                                    if not has_keyword: continue
                                    groups_to_write = filtered

                                fname = f"{CHANNEL_NAME_FOR_FILE}_Hunter_{uuid.uuid4().hex[:4].upper()}.m3u"
                                write_m3u_and_get_count(groups_to_write, fname)
                                final_fname = compress_if_large(fname)
                                link = await upload_to_cloud(final_fname, "all")

                                safe_delete(fname)
                                if final_fname != fname: safe_delete(final_fname)

                                if link:
                                    collected_links.append(f"🔹 <b>الباقة {found_count + 1}:</b> <code>{link}</code>")
                                    found_count += 1
                                    try: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🎉 **تم صيد وتجهيز سيرفر قوي!**\n✅ المجهز للنشر: {found_count}/{target_count}", parse_mode="Markdown", reply_markup=stop_button())
                                    except: pass
                except Exception: pass
        await app.stop()

        if collected_links:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🚀 **انتهى الصيد بنجاح!**\nجاري النشر في القناة الرسمية...", parse_mode="Markdown")
            caption = WARNING_TEXT + LINK_POST_CAPTION.replace("{links}", "\n\n".join(collected_links))
            await bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_post_keyboard())
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🏁 **اكتملت مهمة الصيد بنجاح أسطوري!**\nتم جلب ونشر {found_count} سيرفر مريقل في القناة.")
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ **انتهى البحث ولم يتم العثور على أي سيرفرات تلبي شروط الحد الأدنى للحماية.**")
    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ غير متوقع في المصنع: {e}")

async def run_hunttxt_action(bot, chat_id, message_id, args):
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🚀 **بدأ صيد الروابط السحابية كملف نصي...**", parse_mode="Markdown", reply_markup=stop_button())
    target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
    keyword = " ".join(args[:-1]).lower() if len(args) > 1 and args[-1].isdigit() else (" ".join(args[1:]).lower() if len(args) > 1 else "")
    
    app = Client("wassim_fast_scraper", api_id=24974564, api_hash="b87511de89b42178862e13e84147952b", session_string=SESSION_STRING)
    await app.start()

    found_count = 0
    scanned_channels = 0
    collected_links_raw = []
    tested_urls = set()

    async with aiohttp.ClientSession() as session_req:
        async for dialog in app.get_dialogs():
            if found_count >= target_count: break
            chat = dialog.chat
            if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
            chat_name = chat.title or str(chat.id)
            if any(my_chat.lower() in chat_name.lower() for my_chat in MY_CHANNELS): continue
            if not any(kw in chat_name.lower() for kw in TARGET_KEYWORDS): continue

            scanned_channels += 1
            try: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🔍 **جاري فحص القناة:** {chat_name}\n✅ المستخرج: {found_count}/{target_count}", parse_mode="Markdown", reply_markup=stop_button())
            except: pass

            try:
                async for msg in app.get_chat_history(chat.id, limit=60):
                    if found_count >= target_count: break
                    text = str(msg.text or msg.caption)
                    urls_to_test = [u for u in re.findall(r'(https?://[^\s]+)', text) if 'm3u' in u.lower() or 'get.php' in u.lower()]
                    
                    host = re.search(r'(https?://[a-zA-Z0-9.-]+(:\d+)?)/?', text)
                    user = re.search(r'(?:user|username|usr)[:\s=]+([a-zA-Z0-9_.-]+)', text, re.IGNORECASE)
                    pw = re.search(r'(?:pass|password|pwd)[:\s=]+([a-zA-Z0-9_.-]+)', text, re.IGNORECASE)
                    if host and user and pw: urls_to_test.append(f"{host.group(1)}/get.php?username={user.group(1)}&password={pw.group(1)}&type=m3u_plus&output=ts")

                    for u in set(urls_to_test):
                        if found_count >= target_count: break
                        if u in tested_urls: continue
                        tested_urls.add(u)

                        res = await fetch_and_analyze(session_req, u, found_count+1)
                        if res.get("success"):
                            groups_to_write = {k: v for k, v in res["groups"].items()}
                            if keyword:
                                filtered = defaultdict(list)
                                for g_name, entries in groups_to_write.items():
                                    for extinf, curl, is_adult in entries:
                                        if keyword in g_name.lower() or keyword in extinf.lower(): filtered[g_name].append((extinf, curl, is_adult))
                                groups_to_write = filtered

                            unique_code = str(uuid.uuid4().hex)[:4].upper()
                            fname = f"Hunter_{unique_code}.m3u"
                            write_m3u_and_get_count(groups_to_write, fname)
                            final_fname = compress_if_large(fname)
                            link = await upload_to_cloud(final_fname, "all")

                            safe_delete(fname)
                            if final_fname != fname: safe_delete(final_fname)

                            if link:
                                collected_links_raw.append(link)
                                found_count += 1
            except Exception: pass

    await app.stop()
    if collected_links_raw:
        txt_filename = f"Cloud_Links_{target_count}_{uuid.uuid4().hex[:4]}.txt"
        with open(txt_filename, "w", encoding="utf-8") as f: f.write("\n".join(collected_links_raw))
        with open(txt_filename, "rb") as f_send:
            await bot.send_document(chat_id=chat_id, document=f_send, caption=f"✅ **اكتمل صيد الملف النصي!**\nإليك {len(collected_links_raw)} روابط سحابية مباشرة وفعالة.")
        safe_delete(txt_filename)
    else: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ لم أجد سيرفرات قوية لتوليد الملف النصي.")

async def run_scrape_action(bot, chat_id, message_id, args):
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="⚡ **بدأ السحب السريع للروابط الخام للمصنع...**", parse_mode="Markdown", reply_markup=stop_button())
    target_count = int(args[0])
    app = Client("wassim_fast_scraper", api_id=24974564, api_hash="b87511de89b42178862e13e84147952b", session_string=SESSION_STRING)
    await app.start()

    all_links = []
    async for dialog in app.get_dialogs():
        chat = dialog.chat
        if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
        
        try:
            async for msg in app.get_chat_history(chat.id, limit=80):
                text = str(msg.text or msg.caption)
                urls = re.findall(r'(https?://[^\s]+)', text)
                for u in urls:
                    if 'm3u' in u.lower() or 'get.php' in u.lower(): all_links.append(u)
                if len(all_links) >= target_count * 2: break
        except Exception: pass
        if len(all_links) >= target_count * 2: break

    await app.stop()
    final_links = list(set(all_links))[:target_count]
    if final_links:
        txt_filename = f"Scraped_{len(final_links)}.txt"
        with open(txt_filename, "w", encoding="utf-8") as f: f.write("\n".join(final_links))
        with open(txt_filename, "rb") as f_send:
            await bot.send_document(chat_id=chat_id, document=f_send, caption=f"⚡ **اكتمل السحب السريع بنجاح!**\nتم جلب {len(final_links)} روابط فريدة وجاهزة للفحص.")
        safe_delete(txt_filename)
    else: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ لم يتم العثور على سيرفرات جديدة.")

# ================== الدالة الحاكمة لتشغيل المصنع السحابي ==================
async def main():
    if not SESSION_STRING: exit(1)
    bot = Bot(token=TOKEN)
    payload = json.loads(os.environ.get("PAYLOAD", "{}"))
    action = payload.get("action")
    chat_id = payload.get("chat_id")
    message_id = payload.get("message_id")
    if not chat_id or not action: return

    try:
        if action == "hunt":
            await run_hunter_action(bot, chat_id, message_id, payload.get("args", []))
        elif action == "hunttxt":
            await run_hunttxt_action(bot, chat_id, message_id, payload.get("args", []))
        elif action == "scrape":
            await run_scrape_action(bot, chat_id, message_id, payload.get("args", []))
        elif action == "process_file":
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="⚙️ **المصنع يقوم بتنظيف وتفريغ الملف بالفورمات الأصلي الشرعي...** ⏳", reply_markup=stop_button())
            tg_file = await bot.get_file(payload.get("file_id"))
            filepath = "temp_dl.m3u"
            await tg_file.download_to_drive(filepath)
            
            groups, total, duplicates, adult = await analyze_async(filepath)
            os.remove(filepath)
            
            out_file = "clean_original.m3u"
            write_m3u_and_get_count(groups, out_file)
            final_file = compress_if_large(out_file)
            
            git_link = await upload_to_cloud(final_file, "github")
            catbox_link = await upload_to_cloud(final_file, "catbox_m3u8")
            
            safe_delete(out_file)
            if final_file != out_file: safe_delete(final_file)
            
            msg = f"✅ **اكتمل التنظيف والفورمات الأصلي!**\n\n📡 إجمالي القنوات: {total:,}\n🔞 محذوف وفلترة إباحي: {adult:,}\n\n🔗 **رابط المستودع (GitHub):**\n`{git_link}`\n\n🔗 **رابط البث (Catbox):**\n`{catbox_link}`"
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=msg, parse_mode="Markdown")
            
    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ داخلي في عمل المصنع: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
