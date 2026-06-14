

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
from urllib.parse import quote

from pyrogram import Client, enums
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# ================== كود الكشف والربط بالخزنة السرية ==================
print("🔍 DEBUG: جاري فحص متغيرات البيئة والخزنة السرية...")
s_str = os.environ.get("MY_SESSION_STRING", "").strip()
print(f"🔍 DEBUG: طول كود الجلسة المستلم هو: {len(s_str)} حرف")

if not s_str:
    print("❌ CRITICAL ERROR: كود الجلسة فارغ! تأكد من إعدادات Repository Secrets.")
    exit(1)

# ================== بياناتك السرية المحمية المسترجعة ==================
TOKEN = os.environ.get("MY_TELEGRAM_TOKEN")
GITHUB_TOKEN = os.environ.get("MY_GITHUB_TOKEN")
GITHUB_USER = "Mesbahikarim03-svg"
REPO_NAME = "krimo.-Iptv"
SESSION_STRING = s_str

API_ID = 24974564
API_HASH = "b87511de89b42178862e13e84147952b"

MAX_FILE_SIZE_MB = 150
MIN_CHANNELS_REQUIRED = 1000
CHANNEL_ID = "@free_iptv_world"
CHANNEL_NAME_FOR_FILE = "FREE_IPTV_WORLD"

MY_CHANNELS = ["عالم iptv مجاني", "دردشة مجانية عبر الإنترنت", "تحديث مجاني لعالم البث عبر الإنترنت"]
TARGET_KEYWORDS = ["iptv", "m3u", "xtream", "mac", "portal", "sat", "tv", "server", "stb", "cccam", "streaming", "restream", "codes", "vip", "app"]

ADULT_WORDS = ["xxx", "porn", "adult", "adults", "sex", "18+", "+18", "erotic", "playboy", "amateur", "onlyfans", "brazzers", "vivid", "hustler", "penthouse", "babes", "realitykings", "naughty", "bangbros", "milf", "lesbian", "gay", "cam", "nsfw", "x-art", "babe", "pussy", "dick", "matures", "hardcore", "xnxx", "xvideos", "pornhub", "redtube", "kamasutra", "peep"]
ADULT_REGEX = re.compile(r'(?i)(?:' + '|'.join(map(re.escape, ADULT_WORDS)) + r')')
GROUP_TITLE_REGEX = re.compile(r'group-title="([^"]*)"')

WARNING_TEXT = """<blockquote>⚠️ <b>ATTENTION / انتباه:</b>
Links are valid for <b>10 HOURS</b> from publishing, then they will be deleted automatically. Download them NOW!
مدة الروابط 10 ساعات فقط من وقت النشر ثم سيتم حذفها. يرجى التحميل أو النسخ الآن!</blockquote>\n\n"""

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
... <b>And Many More!</b> 🔥</blockquote>

⚙️ 𝗛𝗼𝘄 𝘁𝗼 𝘂𝘀𝗲?
1️⃣ Copy the link above.
2️⃣ Open your IPTV Player (Smarters, Tivimate, VLC).
3️⃣ Select "Add Playlist / M3U URL".
4️⃣ Paste & Enjoy! 🍿

♻️ 𝘗𝘭𝘦𝘢𝘴𝘦 𝘚𝘩𝘢𝘳𝗲 & 𝘚𝘶𝘱𝘱𝘰𝘳𝘵 𝘜𝘴!"""

def build_post_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📣 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url="https://t.me/free_iptv_world"), InlineKeyboardButton("💬 𝗢𝘂𝗿 𝗚𝗿𝗼𝘂𝗽", url="https://t.me/FREE_IPTV_WORLD_CHAT")],
        [InlineKeyboardButton("🔁 𝗦𝗵𝗮𝗿𝗲 𝗣𝗼𝘀𝘁", url="https://t.me/share/url?url=https://t.me/free_iptv_world&text=🔥%20أقوى%20سيرفرات%20IPTV%20مجاناً%20🔥")]
    ])

def stop_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🛑 إيقاف العملية", callback_data="cancel_process")]])

def safe_delete(filepath):
    try:
        if os.path.exists(filepath): os.remove(filepath)
    except: pass

async def is_link_working(url):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
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
                        if int(time.time()) - int(name.split("_")[1]) > 36000:
                            requests.delete(file.get("url"), json={"message": f"Auto-delete: {name}", "sha": file.get("sha")}, headers=headers)
                    except: continue
    except: pass

async def upload_to_cloud(filename, selected_api="all"):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0: return None
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    base_name = os.path.basename(filename)
    custom_timeout = aiohttp.ClientTimeout(total=90)
    apis_to_try = ["github", "catbox_m3u8", "pixeldrain", "uguu", "litterbox"] if selected_api == "all" else [selected_api]
    for api in apis_to_try:
        if api == "github" and size_mb > 95: continue
        for attempt in range(1, 3):
            try:
                link = None
                if api == "github":
                    cleanup_old_github_files()
                    safe_name = f"FIW_{int(time.time())}_{attempt}_{uuid.uuid4().hex[:6]}_{base_name}"
                    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{safe_name}"
                    with open(filename, "rb") as f: encoded_content = base64.b64encode(f.read()).decode('utf-8')
                    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
                    payload = {"message": f"Auto Upload {safe_name}", "content": encoded_content}
                    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
                        async with session.put(api_url, json=payload, headers=headers) as response:
                            if response.status in [201, 200]: link = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{safe_name}"
                elif api == "catbox_m3u8":
                    def up_cat():
                        with open(filename, 'rb') as f:
                            resp = requests.post("https://catbox.moe/user/api.php", data={'reqtype': 'fileupload', 'userhash': '4743fd4cd7b648c176c6e5800'}, files={'fileToUpload': (base_name, f, 'application/vnd.apple.mpegurl')}, headers={'User-Agent': 'Mozilla/5.0'})
                            if resp.status_code == 200 and resp.text.startswith("http"): return resp.text.strip()
                        return None
                    link = await asyncio.to_thread(up_cat)
                elif api == "pixeldrain":
                    auth = aiohttp.BasicAuth(login="", password="6bd803d9-4e6e-402f-a7b1-c355ac2dae63")
                    async with aiohttp.ClientSession(auth=auth, timeout=custom_timeout) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('file', f, filename=base_name)
                            async with session.post("https://pixeldrain.com/api/file", data=data) as response:
                                if response.status in [200, 201]:
                                    res = await response.json()
                                    if res.get("success"): link = f"https://pixeldrain.com/api/file/{res.get('id')}"
                elif api == "uguu":
                    async with aiohttp.ClientSession(timeout=custom_timeout, headers={'User-Agent': 'Mozilla/5.0'}) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('files[]', f, filename=base_name)
                            async with session.post("https://uguu.se/upload.php", data=data) as response:
                                if response.status == 200:
                                    res = await response.json()
                                    if res.get("success"): link = res["files"][0]["url"]
                elif api == "litterbox":
                    async with aiohttp.ClientSession(timeout=custom_timeout, headers={'User-Agent': 'Mozilla/5.0'}) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('reqtype', 'fileupload')
                            data.add_field('time', '72h')
                            data.add_field('fileToUpload', f, filename=base_name)
                            async with session.post("https://litterbox.catbox.moe/resources/internals/api.php", data=data) as response:
                                if response.status == 200:
                                    res = await response.text()
                                    if res.startswith("http"): link = res.strip()
                if link: return link
            except Exception: await asyncio.sleep(attempt * 2)
    return None

def analyze_file(filepath):
    groups = defaultdict(list)
    seen_urls_hashes = set()
    total, adult = 0, 0
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
                        if url_hash not in seen_urls_hashes:
                            seen_urls_hashes.add(url_hash)
                            groups[group].append((current_extinf, url, False))
                    current_extinf = ""
    clean_groups = defaultdict(list)
    for g_name, entries in groups.items():
        if not bool(ADULT_REGEX.search(g_name)): clean_groups[g_name] = entries
    return clean_groups, total, adult

async def analyze_async(filepath): return await asyncio.to_thread(analyze_file, filepath)

def get_clean_size_mb(groups):
    size_bytes = len("#EXTM3U\r\n")
    for g in groups.values():
        for extinf, url, _ in g:
            size_bytes += len(extinf.replace('\n', '\r\n').encode('utf-8')) + len(url.encode('utf-8')) + 4
    return size_bytes / (1024 * 1024)

def write_m3u_and_get_count(groups, filename):
    count = 0
    promo = '#EXTINF:-1 tvg-id="Free.IPTV" tvg-name="FREE IPTV WORLD PROMO" tvg-logo="https://files.catbox.moe/goe4nn.jpg" group-title="🌟 FREE IPTV WORLD 🌟",📺 Welcome to FREE IPTV WORLD\r\nhttps://files.catbox.moe/npglfu.mp4\r\n'
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write("#EXTM3U\r\n" + promo)
        count += 1
        for g in groups.keys():
            for extinf, url, _ in groups[g]:
                extinf_fixed = extinf.replace('\n', '\r\n')
                if ',' in extinf_fixed:
                    parts = extinf_fixed.rsplit(',', 1)
                    if "FREE IPTV WORLD" not in parts[1]: extinf_branded = f"{parts[0]},{parts[1]} | 🌟 FREE IPTV WORLD 🌟"
                    else: extinf_branded = extinf_fixed
                else: extinf_branded = extinf_fixed
                f.write(extinf_branded + "\r\n" + url + "\r\n")
                count += 1
    return count

def compress_if_large(filename):
    if not os.path.exists(filename): return filename
    if os.path.getsize(filename) / (1024 * 1024) > MAX_FILE_SIZE_MB:
        zip_filename = filename.replace(".m3u", ".zip")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf: zipf.write(filename, os.path.basename(filename))
        return zip_filename
    return filename

async def is_playlist_alive(groups):
    all_valid_urls = [curl for g in groups.values() for _, curl, _ in g if curl.lower().startswith("http")]
    if not all_valid_urls: return False
    test_urls = random.sample(all_valid_urls, min(6, len(all_valid_urls)))
    headers = {"User-Agent": "TiviMate/4.7.0 (Linux; Android 11)"}
    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(sock_connect=3, sock_read=4)) as session:
        async def check(url):
            try:
                async with session.get(url, allow_redirects=True) as resp:
                    if resp.status in [200, 206, 301, 302, 307]:
                        chunk = await resp.content.read(256)
                        if chunk and b"<html>" not in chunk.lower() and b"<!doctype" not in chunk.lower(): return True
            except: pass
            return False
        results = await asyncio.gather(*[check(u) for u in test_urls])
        return any(results)

async def fetch_and_analyze(session, url, idx):
    async def _fetch():
        try:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True) as response:
                if response.status in [200, 206]:
                    temp = f"temp_{uuid.uuid4().hex}.m3u"
                    with open(temp, 'wb') as f:
                        async for chunk in response.content.iter_chunked(1024*1024): f.write(chunk)
                    groups, total, adult = await analyze_async(temp)
                    safe_delete(temp)
                    if total < MIN_CHANNELS_REQUIRED or not await is_playlist_alive(groups): return {"id": idx, "success": False}
                    return {"id": idx, "groups": groups, "total": total, "size_mb": get_clean_size_mb(groups), "success": True}
        except: pass
        return {"id": idx, "success": False}
    try: return await asyncio.wait_for(_fetch(), timeout=20.0)
    except: return {"id": idx, "success": False}

async def safe_edit(bot, chat_id, message_id, text, edit_state, markup=None, force=False):
    if force or (time.time() - edit_state["time"] > 3.0):
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode="Markdown", reply_markup=markup)
            edit_state["time"] = time.time()
        except: pass

# ================== دالة الانتظار الصارم لتنزيل صورة الذكاء الاصطناعي ==================
async def generate_and_download_image(bot, chat_id, message_id, keyword, edit_state):
    await safe_edit(bot, chat_id, message_id, "🎨 **جاري رسم الصورة بالذكاء الاصطناعي (يرجى الانتظار، السيرفر يجهز في الصورة)...**", edit_state, force=True)
    
    prompt = f"Luxury Premium {keyword} sports tv broadcast, 4k resolution, cinematic lighting, neon dark background, iptv concept" if keyword else "Luxury Premium Smart TV IPTV worldwide channels broadcast, 4k resolution, cinematic lighting, neon dark background"
    encoded_prompt = quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1, 999999)}"
    img_path = f"ai_cover_{uuid.uuid4().hex[:4]}.jpg"
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # حلقة انتظار صارمة: البوت مستحيل يفوت للروابط حتى يتأكد بلي الصورة هبطت
    for attempt in range(1, 10): # راح يستنى حتى 40 ثانية لو تطلب الأمر
        try:
            await safe_edit(bot, chat_id, message_id, f"⏳ **جلب الصورة الفخمة من السيرفر... المحاولة ({attempt}/9)**", edit_state, force=True)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                    if resp.status == 200:
                        content = await resp.read()
                        if len(content) > 15000:  # صورة حقيقية ماشي رسالة خطأ
                            with open(img_path, 'wb') as f:
                                f.write(content)
                            return img_path
        except Exception: pass
        await asyncio.sleep(4) # انتظار 4 ثواني بين كل محاولة
        
    return None # يرجع None إذا فشل قاع بعد 9 محاولات

# ================== أوامر الصيد والسحب ==================
async def run_hunter_action(bot, chat_id, message_id, args):
    try:
        edit_state = {"time": 0}
        target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
        keyword = " ".join(args[:-1]).lower() if len(args) > 1 and args[-1].isdigit() else (" ".join(args[1:]).lower() if len(args) > 1 else "")
        
        await safe_edit(bot, chat_id, message_id, "🚀 **بدأ الصيد المباشر بالتوربو...**", edit_state, stop_button(), force=True)
        
        app = Client("wassim_fast_scraper", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
        await app.start()

        found_count, scanned, collected_links, tested_urls = 0, 0, [], set()

        async with aiohttp.ClientSession() as session_req:
            async for dialog in app.get_dialogs():
                if found_count >= target_count: break
                chat = dialog.chat
                if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
                chat_name = chat.title or str(chat.id)
                if any(kw in chat_name.lower() for kw in TARGET_KEYWORDS):
                    scanned += 1
                    await safe_edit(bot, chat_id, message_id, f"🔍 **فحص القناة:** {chat_name}\n✅ المجهز: {found_count}/{target_count}", edit_state, stop_button())
                    
                    urls_to_test = set()
                    try:
                        async for msg in app.get_chat_history(chat.id, limit=150):
                            text = str(msg.text or msg.caption)
                            urls = re.findall(r'(https?://[^\s]+)', text)
                            for u in urls:
                                if 'm3u' in u.lower() or 'get.php' in u.lower(): urls_to_test.add(u)
                    except: pass

                    valid_urls = [u for u in urls_to_test if u not in tested_urls]
                    tested_urls.update(valid_urls)

                    if valid_urls:
                        tasks = [fetch_and_analyze(session_req, u, found_count+1+i) for i, u in enumerate(valid_urls)]
                        results = await asyncio.gather(*tasks)
                        for res in results:
                            if found_count >= target_count: break
                            if res and res.get("success"):
                                groups = res["groups"]
                                if keyword:
                                    filtered = defaultdict(list)
                                    for g_name, entries in groups.items():
                                        for extinf, curl, _ in entries:
                                            if keyword in g_name.lower() or keyword in extinf.lower(): filtered[g_name].append((extinf, curl, False))
                                    groups = filtered
                                if not groups: continue
                                
                                fname = f"Hunter_{uuid.uuid4().hex[:4].upper()}.m3u"
                                write_m3u_and_get_count(groups, fname)
                                link = await upload_to_cloud(compress_if_large(fname), "all")
                                safe_delete(fname)
                                if link:
                                    collected_links.append(f"🔹 <b>الباقة {found_count + 1}:</b> <code>{link}</code>")
                                    found_count += 1
                                    await safe_edit(bot, chat_id, message_id, f"🎉 **صيد قوي!**\n✅ المجهز: {found_count}/{target_count}", edit_state, stop_button(), force=True)
        await app.stop()

        if collected_links:
            # هنا البوت راح يحبس ويستنى الصورة حتى تهبط
            img_path = await generate_and_download_image(bot, chat_id, message_id, keyword, edit_state)
            
            await safe_edit(bot, chat_id, message_id, "🚀 **الصورة جاهزة! جاري النشر في القناة (الصورة أولاً ثم الروابط)...**", edit_state, None, force=True)
            
            if keyword: cap_title = f"🔥 𝗘𝗫𝗖𝗟𝗨𝗦𝗜𝗩𝗘 𝗦𝗘𝗥𝗩𝗘𝗥: {keyword.upper()} 🔥"
            else: cap_title = "🔗 𝗗𝗜𝗥𝗘𝗖𝗧 𝗜𝗣𝗧𝗩 𝗟𝗜𝗡𝗞𝗦 🔗"
            
            # --- الخطوة 1: نشر الصورة الفخمة بقالب بسيط جداً وبدون روابط ---
            simple_img_caption = f"🏆 <b>𝗙𝗥𝗘𝗘 𝗜𝗣𝗧𝗩 𝗪𝗢𝗥𝗟𝗗</b> 🏆\n⚡ <i>New Exclusive {keyword.upper() if keyword else 'Premium'} Package Uploaded!</i>\n\n👇 <b>Check the links in the messages below</b> 👇"
            
            try:
                if img_path and os.path.exists(img_path):
                    with open(img_path, 'rb') as f_img:
                        await bot.send_photo(chat_id=CHANNEL_ID, photo=f_img, caption=simple_img_caption, parse_mode="HTML")
                    safe_delete(img_path)
                else:
                    fallback_img = "https://files.catbox.moe/goe4nn.jpg"
                    await bot.send_photo(chat_id=CHANNEL_ID, photo=fallback_img, caption=simple_img_caption, parse_mode="HTML")
            except Exception as e: 
                await bot.send_message(chat_id=CHANNEL_ID, text=simple_img_caption, parse_mode="HTML")
            
            await asyncio.sleep(2)
            
            # --- الخطوة 2: إرسال جميع الروابط (مقسّمة عشرات) كرسائل نصية بقوالبك الأصلية ---
            all_chunks = []
            for i in range(0, len(collected_links), 10):
                all_chunks.append(collected_links[i:i+10])
            
            for chunk in all_chunks:
                if not chunk: continue
                caption_n = LINK_POST_CAPTION.replace("🔗 𝗗𝗜𝗥𝗘𝗖𝗧 𝗜𝗣𝗧𝗩 𝗟𝗜𝗡𝗞𝗦 🔗", cap_title).replace("{links}", "\n\n".join(chunk))
                if keyword: caption_n = caption_n.replace("Premium Channels & VODs", f"Focus: {keyword.upper()} Channels")
                if any("pixeldrain" in l or "litterbox" in l or "uguu" in l for l in chunk):
                    caption_n = WARNING_TEXT + caption_n
                    
                await bot.send_message(chat_id=CHANNEL_ID, text=caption_n, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_post_keyboard())
                await asyncio.sleep(3)
                    
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🏁 **اكتملت العملية بنجاح!** تم نشر الصورة الفخمة وتحتها {found_count} روابط بالقوالب الأصلية.")
        else: 
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ لم أجد نتائج مطابقة.")
    except Exception as e: 
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ أثناء النشر: {e}")

async def run_hunttxt_action(bot, chat_id, message_id, args):
    try:
        edit_state = {"time": 0}
        target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
        keyword = " ".join(args[:-1]).lower() if len(args) > 1 and args[-1].isdigit() else (" ".join(args[1:]).lower() if len(args) > 1 else "")
        
        await safe_edit(bot, chat_id, message_id, "🚀 **بدأ الصيد النصي المتوازي...**", edit_state, stop_button(), force=True)
        
        app = Client("wassim_fast_scraper", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
        await app.start()

        found_count, scanned, collected_links_raw, tested_urls = 0, 0, [], set()

        async with aiohttp.ClientSession() as session_req:
            async for dialog in app.get_dialogs():
                if found_count >= target_count: break
                chat = dialog.chat
                if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
                chat_name = chat.title or str(chat.id)
                if any(kw in chat_name.lower() for kw in TARGET_KEYWORDS):
                    scanned += 1
                    await safe_edit(bot, chat_id, message_id, f"🔍 **فحص:** {chat_name}\n✅ المستخرج: {found_count}/{target_count}", edit_state, stop_button())
                    
                    urls_to_test = set()
                    try:
                        async for msg in app.get_chat_history(chat.id, limit=50):
                            text = str(msg.text or msg.caption)
                            urls = re.findall(r'(https?://[^\s]+)', text)
                            for u in urls:
                                if 'm3u' in u.lower() or 'get.php' in u.lower(): urls_to_test.add(u)
                    except: pass

                    valid_urls = [u for u in urls_to_test if u not in tested_urls]
                    tested_urls.update(valid_urls)

                    if valid_urls:
                        tasks = [fetch_and_analyze(session_req, u, found_count+1+i) for i, u in enumerate(valid_urls)]
                        results = await asyncio.gather(*tasks)
                        for res in results:
                            if found_count >= target_count: break
                            if res and res.get("success"):
                                groups = res["groups"]
                                if keyword:
                                    filtered = defaultdict(list)
                                    for g_name, entries in groups.items():
                                        for extinf, curl, _ in entries:
                                            if keyword in g_name.lower() or keyword in extinf.lower(): filtered[g_name].append((extinf, curl, False))
                                    groups = filtered
                                if not groups: continue
                                
                                fname = f"Hunter_{uuid.uuid4().hex[:4].upper()}.m3u"
                                write_m3u_and_get_count(groups, fname)
                                link = await upload_to_cloud(compress_if_large(fname), "all")
                                safe_delete(fname)
                                if link:
                                    collected_links_raw.append(link)
                                    found_count += 1
                                    await safe_edit(bot, chat_id, message_id, f"🎉 **تم التجهيز!**\n✅ المستخرج: {found_count}/{target_count}", edit_state, stop_button(), force=True)
        await app.stop()

        if collected_links_raw:
            txt_filename = f"Cloud_Links_{target_count}_{uuid.uuid4().hex[:4]}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f: f.write("\n".join(collected_links_raw))
            with open(txt_filename, "rb") as f_send:
                await bot.send_document(chat_id=chat_id, document=f_send, caption=f"✅ **اكتمل صيد الملف النصي!**\nإليك {len(collected_links_raw)} روابط سحابية.")
            safe_delete(txt_filename)
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        else: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ لم أجد نتائج.")
    except Exception as e: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ: {e}")

async def run_scrape_action(bot, chat_id, message_id, args):
    try:
        edit_state = {"time": 0}
        target_count = int(args[0])
        await safe_edit(bot, chat_id, message_id, "⚡ **بدأ السحب السريع الخام للمصنع...**", edit_state, stop_button(), force=True)
        
        app = Client("wassim_fast_scraper", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
        await app.start()

        all_links = []
        async for dialog in app.get_dialogs():
            chat = dialog.chat
            if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
            try:
                async for msg in app.get_chat_history(chat.id, limit=50):
                    text = str(msg.text or msg.caption)
                    urls = re.findall(r'(https?://[^\s]+)', text)
                    for u in urls:
                        if 'm3u' in u.lower() or 'get.php' in u.lower(): all_links.append(u)
                    if len(all_links) >= target_count * 2: break
            except: pass
            if len(all_links) >= target_count * 2: break

        await app.stop()
        final_links = list(set(all_links))[:target_count]
        if final_links:
            txt_filename = f"Scraped_{len(final_links)}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f: f.write("\n".join(final_links))
            with open(txt_filename, "rb") as f_send:
                await bot.send_document(chat_id=chat_id, document=f_send, caption=f"⚡ **اكتمل السحب السريع بنجاح!**\nتم جلب {len(final_links)} روابط.")
            safe_delete(txt_filename)
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        else: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ لم يتم العثور على روابط جديدة.")
    except Exception as e: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ: {e}")

# ================== المحرك السحابي الأساسي المتحكم ==================
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
            await safe_edit(bot, chat_id, message_id, "⚙️ **المصنع يقوم بتنظيف وتفريغ الملف بالفورمات الأصلي الشرعي...** ⏳", {"time": 0}, stop_button(), force=True)
            tg_file = await bot.get_file(payload.get("file_id"))
            filepath = "temp_dl.m3u"
            await tg_file.download_to_drive(filepath)
            
            groups, total, adult = await analyze_async(filepath)
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
