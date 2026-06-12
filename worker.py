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
from collections import defaultdict
import aiohttp

from pyrogram import Client, enums
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# ================== بياناتك السرية ==================
TOKEN = "7070246714:AAEW0yicB7oT5sVsnyBNbVIavRxt3iyH-kU"
GITHUB_TOKEN = os.environ.get("MY_GITHUB_TOKEN")
GITHUB_USER = "Mesbahikarim03-svg"
REPO_NAME = "krimo.-Iptv"

API_ID = 24974564
API_HASH = "b87511de89b42178862e13e84147952b"
SESSION_STRING = "BAF9FOQAbltMnvF2hdrEFT2Qk9ZjqWrcvHmmTWPZclpftaZ2CtORF8imvvaJxCfU5jeCS0lCVqFPbEt50i2PUpObRAAiZNG8e6y0M5sA8jKK-wr26fz4fzjLkALcOxyZg9MB9jdKGCr5PbwgboEn8WeIItU0RltnsRSauKfDCmm7dgteqneUatn2QbpGHHw6_QldEPqRiRbKJXi_kMQQ4tDd004CDuuT0SF1XkCn5wHKd43v7iGBQWhJtu2R07NSqVjvaVQWKWMZjrSUDF7NeAdCCbxVkYDSrp9UzlMRhuuF9f1mEY4TsMSg-y7SB3kaKJiOeP2SaJpGPn0ffrAwwm8-MrQ1iAAAAABEOrkgAA"

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

# ================== الرفع السحابي الأصلي ==================
async def upload_to_cloud(filename, selected_api="all"):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0: return None
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    base_name = os.path.basename(filename)
    custom_timeout = aiohttp.ClientTimeout(total=120)
    apis_to_try = ["github", "catbox_m3u8", "pixeldrain", "uguu"] if selected_api == "all" else [selected_api]

    for api in apis_to_try:
        if api == "github" and size_mb > 95: continue
        for attempt in range(1, 4):
            try:
                link = None
                if api == "github":
                    unique_id = str(uuid.uuid4().hex)[:6]
                    safe_name = f"FIW_{int(time.time())}_{attempt}_{unique_id}_{base_name}"
                    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{safe_name}"
                    with open(filename, "rb") as f: encoded = base64.b64encode(f.read()).decode('utf-8')
                    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
                    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
                        async with session.put(api_url, json={"message": f"Upload {safe_name}", "content": encoded}, headers=headers) as response:
                            if response.status in [201, 200]: link = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{safe_name}"
                            elif response.status in [403, 429]: await asyncio.sleep(15 * attempt); continue
                elif api == "catbox_m3u8":
                    def upload_catbox_sync():
                        with open(filename, 'rb') as f:
                            resp = requests.post("https://catbox.moe/user/api.php", data={'reqtype': 'fileupload', 'userhash': '4743fd4cd7b648c176c6e5800'}, files={'fileToUpload': (base_name.replace(".m3u", ".m3u8"), f, 'application/vnd.apple.mpegurl')})
                            if resp.status_code == 200 and resp.text.startswith("http"): return resp.text.strip()
                        return None
                    link = await asyncio.to_thread(upload_catbox_sync)
                elif api == "pixeldrain":
                    auth = aiohttp.BasicAuth(login="", password="6bd803d9-4e6e-402f-a7b1-c355ac2dae63")
                    async with aiohttp.ClientSession(auth=auth, timeout=custom_timeout) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('file', f, filename=base_name)
                            async with session.post("https://pixeldrain.com/api/file", data=data) as response:
                                if response.status in [200, 201]: link = f"https://pixeldrain.com/api/file/{(await response.json()).get('id')}"
                elif api == "uguu":
                    async with aiohttp.ClientSession(timeout=custom_timeout, headers={"User-Agent": "Mozilla/5.0"}) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('files[]', f, filename=base_name.replace(".m3u", ".m3u8"), content_type='application/vnd.apple.mpegurl')
                            async with session.post("https://uguu.se/upload.php", data=data) as response:
                                if response.status == 200: link = (await response.json())["files"][0]["url"]
                if link: return link
            except: await asyncio.sleep(attempt * 4)
    return None

# ================== المحلل الذكي وكتابة M3U الأصلية ==================
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

async def analyze_async(filepath):
    return await asyncio.to_thread(analyze_file, filepath)

def get_clean_size_mb(groups):
    size_bytes = len("#EXTM3U\r\n")
    for g in groups.values():
        for extinf, url, _ in g:
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
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filename, os.path.basename(filename))
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

async def fetch_and_analyze(session, url, idx):
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with session.get(url, headers=headers, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=60)) as response:
            if response.status in [200, 206]:
                temp_path = f"temp_url_{uuid.uuid4().hex}.m3u"
                with open(temp_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024 * 1024): f.write(chunk)
                with open(temp_path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_lines = "".join([f.readline() for _ in range(50)])
                if "#EXTM3U" not in first_lines and "#EXTINF" not in first_lines:
                    safe_delete(temp_path)
                    return {"id": idx, "success": False, "error": "Not a valid M3U"}
                groups, total, duplicates, adult = await analyze_async(temp_path)
                safe_delete(temp_path)
                if total < MIN_CHANNELS_REQUIRED: return {"id": idx, "success": False, "error": f"Only {total} channels"}
                if not await is_playlist_alive(groups): return {"id": idx, "success": False, "error": "Dead Server"}
                return {"id": idx, "groups": groups, "total": total, "adult": adult, "size_mb": get_clean_size_mb(groups), "success": True}
            return {"id": idx, "success": False, "error": f"Status {response.status}"}
    except: return {"id": idx, "success": False, "error": "Timeout"}

# ================== معالجة الصيد ونشر القناة ==================
async def run_hunter_action(bot, chat_id, message_id, args):
    try:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🚀 **بدأ الصيد الآلي...**\n⏳ جاري الدخول لحساب Pyrogram...", parse_mode="Markdown")
        target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
        keyword = " ".join(args[:-1]).lower() if len(args) > 1 and args[-1].isdigit() else (" ".join(args[1:]).lower() if len(args) > 1 else "")
        
        app = Client("wassim_fast_scraper", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
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
                chat_name = chat.title or chat.username or str(chat.id)
                if any(my_chat.lower() in chat_name.lower() for my_chat in MY_CHANNELS): continue
                if not any(kw in chat_name.lower() for kw in TARGET_KEYWORDS): continue

                scanned_channels += 1
                try: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🔍 **جاري فحص القناة:** {chat_name}\n📊 القنوات المفحوصة: {scanned_channels}\n✅ المجهز: {found_count}/{target_count}", parse_mode="Markdown")
                except: pass

                async for msg in app.get_chat_history(chat.id, limit=100):
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

                        try: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"⚙️ **يتم الآن تحليل واختبار سيرفر محتمل...**\n✅ المجهز: {found_count}/{target_count}", parse_mode="Markdown")
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
                            await asyncio.to_thread(write_m3u_and_get_count, groups_to_write, fname)
                            final_fname = await asyncio.to_thread(compress_if_large, fname)
                            link = await upload_to_cloud(final_fname, "all") # الرفع للسيرفرات الأصلية

                            safe_delete(fname)
                            if final_fname != fname: safe_delete(final_fname)

                            if link and await is_link_working(link):
                                collected_links.append(f"🔹 <b>الباقة {found_count + 1}:</b> <code>{link}</code>")
                                found_count += 1
                                try: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🎉 **تم صيد وتجهيز سيرفر قوي!**\n✅ المجهز للنشر: {found_count}/{target_count}", parse_mode="Markdown")
                                except: pass
        await app.stop()

        if collected_links:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🚀 **انتهى الصيد!**\nجاري نشر {len(collected_links)} روابط في القناة دفعة واحدة...", parse_mode="Markdown")
            for i in range(0, len(collected_links), 10):
                chunk_links = collected_links[i:i + 10]
                caption = LINK_POST_CAPTION.replace("{links}", "\n\n".join(chunk_links))
                if keyword:
                    caption = caption.replace("🔗 𝗗𝗜𝗥𝗘𝗖𝗧 𝗜𝗣𝗧𝗩 𝗟𝗜𝗡𝗞𝗦 🔗", f"🔥 𝗘𝗫𝗖𝗟𝗨𝗦𝗜𝗩𝗘 𝗦𝗘𝗥𝗩𝗘𝗥: {keyword.upper()} 🔥")
                    caption = caption.replace("Premium Channels & VODs", f"Focus: {keyword.upper()} Channels")
                if any("pixeldrain" in l or "litterbox" in l or "uguu" in l for l in chunk_links): caption = WARNING_TEXT + caption
                
                await bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML", disable_web_page_preview=True, reply_markup=build_post_keyboard())
                await asyncio.sleep(3)
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🏁 **اكتملت مهمة الصيد الأسطورية!**\nتم جلب، فحص، ونشر {found_count} سيرفر بنجاح في القناة.", parse_mode="Markdown")
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ **انتهى البحث ولم أجد أي سيرفرات تلبي طلبك للأسف!**", parse_mode="Markdown")
    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ: {e}")

async def main():
    bot = Bot(token=TOKEN)
    payload = json.loads(os.environ.get("PAYLOAD", "{}"))
    action = payload.get("action")
    chat_id = payload.get("chat_id")
    message_id = payload.get("message_id")
    if not chat_id or not action: return

    try:
        if action == "hunt":
            await run_hunter_action(bot, chat_id, message_id, payload.get("args", []))
        elif action == "process_file":
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="⚙️ المصنع (GitHub) يقوم بتنظيف الملف وتجهيزه بالنسخة الأصلية... ⏳")
            tg_file = await bot.get_file(payload.get("file_id"))
            filepath = "temp_dl.m3u"
            await tg_file.download_to_drive(filepath)
            
            groups, total, duplicates, adult = await analyze_async(filepath)
            os.remove(filepath)
            
            out_file = "clean_original.m3u"
            write_m3u_and_get_count(groups, out_file)
            git_link = await upload_to_cloud(out_file, "github")
            catbox_link = await upload_to_cloud(out_file, "catbox_m3u8")
            os.remove(out_file)
            
            msg = f"✅ اكتمل التنظيف والفورمات الأصلي!\n📡 القنوات: {total:,}\n🔞 المحذوف: {adult:,}\n\n🔗 رابط GitHub:\n`{git_link}`\n\n🔗 رابط Catbox:\n`{catbox_link}`"
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=msg, parse_mode="Markdown")
            
    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ في المصنع: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
