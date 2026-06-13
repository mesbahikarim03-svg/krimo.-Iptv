# الكود الكامل الجاهز - ضعه مكان `worker.py`

```python
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

# ================== كود الكشف والربط بالخزنة السرية ==================
print("🔍 DEBUG: جاري فحص متغيرات البيئة والخزنة السرية...")
s_str = os.environ.get("MY_SESSION_STRING", "").strip()
print(f"🔍 DEBUG: طول كود الجلسة المستلم هو: {len(s_str)} حرف")

if not s_str:
    print("❌ CRITICAL ERROR: كود الجلسة فارغ!")
    exit(1)

TOKEN = os.environ.get("MY_TELEGRAM_TOKEN")
GITHUB_TOKEN = os.environ.get("MY_GITHUB_TOKEN")
GITHUB_USER = "Mesbahikarim03-svg"
REPO_NAME = "krimo.-Iptv"
SESSION_STRING = s_str

MAX_FILE_SIZE_MB = 150
MIN_CHANNELS_REQUIRED = 100
CHANNEL_ID = "@free_iptv_world"
CHANNEL_NAME_FOR_FILE = "FREE_IPTV_WORLD"

MY_CHANNELS = ["عالم iptv مجاني", "دردشة مجانية عبر الإنترنت", "تحديث مجاني لعالم البث عبر الإنترنت"]
TARGET_KEYWORDS = ["iptv", "m3u", "xtream", "mac", "portal", "sat", "tv", "server", "stb", "cccam", "streaming", "restream", "codes", "vip", "app", "free", "bein", "sport", "espn", "euro"]

ADULT_WORDS = ["xxx", "porn", "adult", "adults", "sex", "18+", "+18", "erotic", "playboy", "amateur", "onlyfans", "brazzers", "vivid", "hustler", "penthouse", "babes", "realitykings", "naughty", "bangbros", "milf", "lesbian", "gay", "cam", "nsfw", "x-art", "babe", "pussy", "dick", "matures", "hardcore", "xnxx", "xvideos", "pornhub", "redtube", "kamasutra", "peep"]
ADULT_REGEX = re.compile(r'(?i)(?:' + '|'.join(map(re.escape, ADULT_WORDS)) + r')')
GROUP_TITLE_REGEX = re.compile(r'group-title="([^"]*)"')

WARNING_TEXT = """<blockquote>⚠️ <b>ATTENTION / انتباه:</b>
Links are valid for <b>10 HOURS</b> from publishing, then they will be deleted automatically. Download them NOW!
مدة الروابط 10 ساعات فقط من وقت النشر ثم سيتم حذفها. يرجى التحميل أو النسخ الآن!</blockquote>\n\n"""

def build_link_post_caption(links_text, cap_title=None):
    if cap_title is None:
        cap_title = "🔗 𝗗𝗜𝗥𝗘𝗖𝗧 𝗜𝗣𝗧𝗩 𝗟𝗜𝗡𝗞𝗦 🔗"
    return (
        f"{WARNING_TEXT}"
        f"{cap_title}\n"
        f"🌍 𝗙𝗥𝗘𝗘 𝗜𝗣𝗧𝗩 𝗪𝗢𝗥𝗟𝗗 🌍\n\n"
        f"<blockquote>⚠️ <b>إبراء ذمة:</b>\n"
        f"نبرأ إلى الله من أي استخدام سيء أو الدخول لقنوات غير لائقة. 🤲</blockquote>\n\n"
        f"🚀 𝗛𝗶𝗴𝗵-𝗦𝗽𝗲𝗲𝗱 𝗟𝗶𝗻𝗸𝘀:\n"
        f"{links_text}\n\n"
        f"<blockquote>📊 𝗦𝗲𝗿𝘃𝗲𝗿 𝗗𝗲𝘁𝗮𝗶𝗹𝘀:\n"
        f"├ 📦 𝗖𝗼𝗻𝘁𝗲𝗻𝘁: Premium Channels & VODs\n"
        f"├ ⚡ 𝗙𝗼𝗿𝗺𝗮𝘁: M3U & Xtream Codes\n"
        f"├ ⚽️ 𝗦𝗽𝗼𝗿𝘁𝘀: beIN, SSC, Sky, TNT\n"
        f"├ 🎬 𝗠𝗼𝘃𝗶𝗲𝘀: Netflix, OSN, Disney+\n"
        f"└ 📱 𝗗𝗲𝘃𝗶𝗰𝗲𝘀: Smart TV, Android, iOS, PC\n\n"
        f"🌍 𝗪𝗼𝗿𝗹𝗱𝘄𝗶𝗱𝗲 𝗖𝗵𝗮𝗻𝗻𝗲𝗹𝘀 (𝗩𝗜𝗣):\n"
        f"🇩🇿 الجزائر | 🇲🇦 المغرب | 🇹🇳 تونس | 🇪🇬 مصر | 🇸🇦 السعودية | 🇦🇪 الإمارات\n"
        f"🇫🇷 France | 🇬🇧 UK | 🇺🇸 USA | 🇩🇪 Germany | 🇮🇹 Italy | 🇪🇸 Spain\n"
        f"🇨🇦 Canada | 🇳🇱 Netherlands | 🇧🇪 Belgium | 🇸🇪 Sweden | 🇨🇭 Swiss\n"
        f"🇹🇷 Türkiye | ... <b>And Many More!</b> 🔥</blockquote>\n\n"
        f"⚙️ 𝗛𝗼𝘄 𝘁𝗼 𝘂𝘀𝗲?\n"
        f"1️⃣ Copy the link above.\n"
        f"2️⃣ Open your IPTV Player (Smarters, Tivimate, VLC).\n"
        f"3️⃣ Select \"Add Playlist / M3U URL\".\n"
        f"4️⃣ Paste & Enjoy! 🍿\n\n"
        f"♻️ 𝘗𝘭𝘦𝘢𝘴𝘦 𝘚𝘩𝘢𝘳𝘦 & 𝘚𝘶𝘱𝘱𝘰𝘳𝘵 𝘜𝘴!"
    )

def build_post_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📣 𝗢𝘂𝗿 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url="https://t.me/free_iptv_world"),
            InlineKeyboardButton("💬 𝗢𝘂𝗿 𝗚𝗿𝗼𝘂𝗽", url="https://t.me/FREE_IPTV_WORLD_CHAT")
        ],
        [
            InlineKeyboardButton(
                "🔁 𝗦𝗵𝗮𝗿𝗲 𝗣𝗼𝘀𝘁",
                url="https://t.me/share/url?url=https://t.me/free_iptv_world&text=🔥%20أقوى%20سيرفرات%20IPTV%20مجاناً%20🔥"
            )
        ]
    ])

def stop_button():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛑 إيقاف العملية", callback_data="cancel_process")]
    ])

def safe_delete(filepath):
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass

def cleanup_old_github_files():
    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        resp = requests.get(api_url, headers=headers, timeout=15)
        if resp.status_code == 200:
            for file in resp.json():
                name = file.get("name", "")
                if name.startswith("FIW_") and (name.endswith(".m3u") or name.endswith(".zip")):
                    try:
                        file_time = int(name.split("_")[1])
                        if int(time.time()) - file_time > 36000:
                            requests.delete(
                                file.get("url"),
                                json={"message": f"Auto-delete: {name}", "sha": file.get("sha")},
                                headers=headers, timeout=15
                            )
                    except:
                        continue
    except:
        pass

async def upload_to_cloud(filename, selected_api="all"):
    if not os.path.exists(filename) or os.path.getsize(filename) == 0:
        return None
    size_mb = os.path.getsize(filename) / (1024 * 1024)
    base_name = os.path.basename(filename)
    custom_timeout = aiohttp.ClientTimeout(total=120)
    apis_to_try = (
        ["github", "catbox_m3u8", "pixeldrain", "litterbox", "uguu"]
        if selected_api == "all" else [selected_api]
    )
    for api in apis_to_try:
        if api == "github" and size_mb > 95:
            continue
        for attempt in range(1, 4):
            try:
                link = None
                if api == "github":
                    cleanup_old_github_files()
                    safe_name = f"FIW_{int(time.time())}_{uuid.uuid4().hex[:8]}_{base_name}"
                    api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{safe_name}"
                    with open(filename, "rb") as f:
                        encoded_content = base64.b64encode(f.read()).decode('utf-8')
                    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
                    payload = {"message": f"Auto Upload {safe_name}", "content": encoded_content}
                    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
                        async with session.put(api_url, json=payload, headers=headers) as response:
                            if response.status in [200, 201]:
                                link = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{safe_name}"
                elif api == "catbox_m3u8":
                    def up_cat():
                        with open(filename, 'rb') as f:
                            resp = requests.post(
                                "https://catbox.moe/user/api.php",
                                data={'reqtype': 'fileupload', 'userhash': '4743fd4cd7b648c176c6e5800'},
                                files={'fileToUpload': (base_name, f, 'application/vnd.apple.mpegurl')},
                                timeout=90
                            )
                            if resp.status_code == 200 and resp.text.startswith("http"):
                                return resp.text.strip()
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
                                    if res.get("success"):
                                        link = f"https://pixeldrain.com/api/file/{res.get('id')}"
                elif api == "litterbox":
                    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('reqtype', 'fileupload')
                            data.add_field('time', '72h')
                            data.add_field('fileToUpload', f, filename=base_name)
                            async with session.post(
                                "https://litterbox.catbox.moe/resources/internals/api.php", data=data
                            ) as response:
                                if response.status == 200:
                                    res = await response.text()
                                    if res.startswith("http"):
                                        link = res.strip()
                elif api == "uguu":
                    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('files[]', f, filename=base_name)
                            async with session.post("https://uguu.se/upload.php", data=data) as response:
                                if response.status == 200:
                                    res = await response.json()
                                    if res.get("success"):
                                        link = res["files"][0]["url"]
                if link:
                    return link
            except Exception:
                await asyncio.sleep(attempt * 3)
    return None

def analyze_file(filepath):
    groups = defaultdict(list)
    seen_urls_hashes = set()
    total, adult = 0, 0
    current_extinf = ""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#EXTM3U"):
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
                    is_adult = (
                        bool(ADULT_REGEX.search(current_extinf)) or
                        bool(ADULT_REGEX.search(url)) or
                        bool(ADULT_REGEX.search(group))
                    )
                    if is_adult:
                        adult += 1
                    else:
                        url_hash = hash(url)
                        if url_hash not in seen_urls_hashes:
                            seen_urls_hashes.add(url_hash)
                            groups[group].append((current_extinf, url, False))
                    current_extinf = ""
    clean_groups = defaultdict(list)
    for g_name, entries in groups.items():
        if not bool(ADULT_REGEX.search(g_name)):
            clean_groups[g_name] = entries
    return clean_groups, total, adult

async def analyze_async(filepath):
    return await asyncio.to_thread(analyze_file, filepath)

def get_clean_size_mb(groups):
    size_bytes = len("#EXTM3U\r\n")
    for g in groups.values():
        for extinf, url, _ in g:
            size_bytes += (
                len(extinf.replace('\n', '\r\n').encode('utf-8')) +
                len(url.encode('utf-8')) + 4
            )
    return size_bytes / (1024 * 1024)

def write_m3u_and_get_count(groups, filename):
    count = 0
    promo = (
        '#EXTINF:-1 tvg-id="Free.IPTV" tvg-name="FREE IPTV WORLD PROMO" '
        'tvg-logo="https://files.catbox.moe/goe4nn.jpg" '
        'group-title="🌟 FREE IPTV WORLD 🌟",📺 Welcome to FREE IPTV WORLD\r\n'
        'https://files.catbox.moe/npglfu.mp4\r\n'
    )
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write("#EXTM3U\r\n" + promo)
        count += 1
        for g in groups.keys():
            for extinf, url, _ in groups[g]:
                extinf_fixed = extinf.replace('\n', '\r\n')
                if ',' in extinf_fixed:
                    parts = extinf_fixed.rsplit(',', 1)
                    if "FREE IPTV WORLD" not in parts[1]:
                        extinf_branded = f"{parts[0]},{parts[1]} | 🌟 FREE IPTV WORLD 🌟"
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
    if os.path.getsize(filename) / (1024 * 1024) > MAX_FILE_SIZE_MB:
        zip_filename = filename.replace(".m3u", ".zip")
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filename, os.path.basename(filename))
        return zip_filename
    return filename

async def is_playlist_alive(groups):
    all_valid_urls = [
        curl for g in groups.values()
        for _, curl, _ in g
        if curl.lower().startswith("http")
    ]
    if not all_valid_urls:
        return False
    test_urls = random.sample(all_valid_urls, min(3, len(all_valid_urls)))
    headers = {"User-Agent": "TiviMate/4.7.0 (Linux; Android 11)"}
    async with aiohttp.ClientSession(
        headers=headers,
        timeout=aiohttp.ClientTimeout(sock_connect=5, sock_read=5)
    ) as session:
        async def check(url):
            try:
                async with session.get(url, allow_redirects=True) as resp:
                    if resp.status in [200, 206, 301, 302, 307, 308, 403, 401]:
                        return True
            except:
                pass
            return False
        results = await asyncio.gather(*[check(u) for u in test_urls])
        return any(results)

async def fetch_and_analyze(session, url, idx):
    print(f"🔍 [{idx}] فحص: {url[:80]}...")
    async def _fetch():
        try:
            async with session.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                allow_redirects=True,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"📡 [{idx}] Status: {response.status}")
                if response.status in [200, 206]:
                    temp = f"temp_{uuid.uuid4().hex}.m3u"
                    total_bytes = 0
                    with open(temp, 'wb') as f:
                        async for chunk in response.content.iter_chunked(1024 * 1024):
                            f.write(chunk)
                            total_bytes += len(chunk)
                    size_mb = total_bytes / (1024 * 1024)
                    print(f"📦 [{idx}] حجم: {size_mb:.2f} MB")
                    groups, total, adult = await analyze_async(temp)
                    safe_delete(temp)
                    clean_count = sum(len(v) for v in groups.values())
                    print(f"📊 [{idx}] القنوات: {total} إجمالي | {clean_count} نظيف | {adult} إباحي")
                    if clean_count < MIN_CHANNELS_REQUIRED:
                        print(f"❌ [{idx}] رُفض: {clean_count} < {MIN_CHANNELS_REQUIRED}")
                        return {"id": idx, "success": False, "reason": "few_channels"}
                    if size_mb > 0.5:
                        alive = await is_playlist_alive(groups)
                        if not alive:
                            print(f"❌ [{idx}] رُفض: URLs ميتة")
                            return {"id": idx, "success": False, "reason": "dead_urls"}
                    print(f"✅ [{idx}] قُبول! {clean_count} قناة")
                    return {
                        "id": idx, "groups": groups, "total": total,
                        "clean_count": clean_count,
                        "size_mb": get_clean_size_mb(groups),
                        "success": True
                    }
                else:
                    print(f"❌ [{idx}] HTTP {response.status}")
        except asyncio.TimeoutError:
            print(f"⏰ [{idx}] Timeout")
        except Exception as e:
            print(f"❌ [{idx}] خطأ: {type(e).__name__}: {e}")
        return {"id": idx, "success": False, "reason": "error"}
    try:
        return await asyncio.wait_for(_fetch(), timeout=35.0)
    except asyncio.TimeoutError:
        return {"id": idx, "success": False, "reason": "global_timeout"}

async def safe_edit(bot, chat_id, message_id, text, edit_state, markup=None, force=False):
    if force or (time.time() - edit_state["time"] > 3.0):
        try:
            await bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=text, parse_mode="Markdown", reply_markup=markup
            )
            edit_state["time"] = time.time()
        except:
            pass

# ================== ✅ دالة إرسال الروابط - بدون حد - منشور واحد ==================
async def send_links_to_channel(bot, collected_links, keyword=None):
    if not collected_links:
        return False

    if keyword:
        cap_title = f"🔥 𝗘𝗫𝗖𝗟𝗨𝗦𝗜𝗩𝗘 𝗦𝗘𝗥𝗩𝗘𝗥: {keyword.upper()} 🔥"
    else:
        cap_title = "🔗 𝗗𝗜𝗥𝗘𝗖𝗧 𝗜𝗣𝗧𝗩 𝗟𝗜𝗡𝗞𝗦 🔗"

    # ✅ كل الروابط في منشور واحد بدون أي تقسيم
    links_text = "\n\n".join(collected_links)
    caption = build_link_post_caption(links_text, cap_title)

    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=caption,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=build_post_keyboard()
        )
        print(f"✅ تم إرسال {len(collected_links)} رابط في منشور واحد")
        return True
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")
        # ✅ محاولة بديلة إذا تجاوز حد تيليجرام 4096 حرف
        if "MESSAGE_TOO_LONG" in str(e) or "message is too long" in str(e).lower():
            print("⚠️ الرسالة طويلة جداً، جاري الإرسال بنص مبسط...")
            simple_caption = (
                f"{WARNING_TEXT}"
                f"{cap_title}\n"
                f"🌍 𝗙𝗥𝗘𝗘 𝗜𝗣𝗧𝗩 𝗪𝗢𝗥𝗟𝗗 🌍\n\n"
                f"🚀 𝗛𝗶𝗴𝗵-𝗦𝗽𝗲𝗲𝗱 𝗟𝗶𝗻𝗸𝘀:\n"
                f"{links_text}\n\n"
                f"♻️ 𝘚𝘩𝘢𝘳𝘦 & 𝘚𝘶𝘱𝘱𝘰𝘳𝘵 𝘜𝘴! @free_iptv_world"
            )
            try:
                await bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=simple_caption,
                    parse_mode="HTML",
                    disable_web_page_preview=True,
                    reply_markup=build_post_keyboard()
                )
                print("✅ تم الإرسال بالنص المبسط")
                return True
            except Exception as e2:
                print(f"❌ فشل الإرسال المبسط: {e2}")
                return False
        return False
# ============================================================

async def run_hunter_action(bot, chat_id, message_id, args):
    try:
        edit_state = {"time": 0}
        if not args:
            await safe_edit(bot, chat_id, message_id, "❌ يرجى تحديد العدد.", edit_state, force=True)
            return
        target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
        keyword = (
            " ".join(args[:-1]).lower()
            if len(args) > 1 and args[-1].isdigit()
            else ""
        )
        print(f"🎯 هدف: {target_count} سيرفر | كلمة: '{keyword}'")
        await safe_edit(
            bot, chat_id, message_id,
            f"🚀 **بدأ الصيد التوربو...**\n🎯 الهدف: {target_count} سيرفر"
            + (f"\n🔍 الفلتر: {keyword}" if keyword else ""),
            edit_state, stop_button(), force=True
        )
        app = Client(
            "wassim_fast_scraper",
            api_id=24974564,
            api_hash="b87511de89b42178862e13e84147952b",
            session_string=SESSION_STRING
        )
        await app.start()
        found_count = 0
        scanned = 0
        rejected = 0
        collected_links = []
        tested_urls = set()

        connector = aiohttp.TCPConnector(limit=20, limit_per_host=5)
        async with aiohttp.ClientSession(connector=connector) as session_req:
            async for dialog in app.get_dialogs():
                if found_count >= target_count:
                    break
                chat = dialog.chat
                if chat.type not in [
                    enums.ChatType.CHANNEL,
                    enums.ChatType.SUPERGROUP,
                    enums.ChatType.GROUP
                ]:
                    continue
                chat_name = (chat.title or str(chat.id)).lower()
                if not any(kw in chat_name for kw in TARGET_KEYWORDS):
                    continue
                scanned += 1
                await safe_edit(
                    bot, chat_id, message_id,
                    f"🔍 **فحص:** `{chat.title or chat.id}`\n"
                    f"✅ مجهز: {found_count}/{target_count}\n"
                    f"❌ مرفوض: {rejected}\n"
                    f"📡 مفحوص: {scanned}",
                    edit_state, stop_button()
                )
                urls_to_test = set()
                try:
                    async for msg in app.get_chat_history(chat.id, limit=100):
                        text = str(msg.text or msg.caption or "")
                        urls = re.findall(r'(https?://[^\s<>"]+)', text)
                        for u in urls:
                            u_lower = u.lower()
                            if any(x in u_lower for x in ['m3u', 'get.php', 'm3u8', 'playlist', 'list=']):
                                urls_to_test.add(u.rstrip('.,)'))
                except:
                    pass
                valid_urls = [u for u in urls_to_test if u not in tested_urls]
                tested_urls.update(valid_urls)
                if not valid_urls:
                    continue

                semaphore = asyncio.Semaphore(5)
                async def bounded_fetch(url, idx):
                    async with semaphore:
                        return await fetch_and_analyze(session_req, url, idx)
                tasks = [
                    bounded_fetch(u, found_count + 1 + i)
                    for i, u in enumerate(valid_urls)
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if found_count >= target_count:
                        break
                    if isinstance(res, Exception) or not res:
                        continue
                    if not res.get("success"):
                        rejected += 1
                        continue
                    groups = res["groups"]
                    if keyword:
                        filtered = defaultdict(list)
                        for g_name, entries in groups.items():
                            for extinf, curl, _ in entries:
                                if keyword in g_name.lower() or keyword in extinf.lower():
                                    filtered[g_name].append((extinf, curl, False))
                        groups = filtered
                        if not groups:
                            continue
                    clean_count = sum(len(v) for v in groups.values())
                    fname = f"Hunter_{uuid.uuid4().hex[:6].upper()}.m3u"
                    write_m3u_and_get_count(groups, fname)
                    final_fname = compress_if_large(fname)
                    link = await upload_to_cloud(final_fname, "all")
                    safe_delete(fname)
                    if final_fname != fname:
                        safe_delete(final_fname)
                    if link:
                        link_entry = (
                            f"🔹 <b>الباقة {found_count + 1}:</b> ({clean_count:,} قناة)\n"
                            f"<code>{link}</code>"
                        )
                        collected_links.append(link_entry)
                        found_count += 1
                        await safe_edit(
                            bot, chat_id, message_id,
                            f"🎉 **صيد ناجح!** الباقة {found_count}\n"
                            f"✅ المجهز: {found_count}/{target_count}\n"
                            f"❌ المرفوض: {rejected}",
                            edit_state, stop_button(), force=True
                        )
                    else:
                        rejected += 1
        await app.stop()
        print(f"📊 النتيجة: {found_count} نجح | {rejected} مرفوض | {scanned} مفحوص")

        if collected_links:
            await safe_edit(bot, chat_id, message_id, f"📤 **جاري النشر...** ✅ {found_count} سيرفر", edit_state, force=True)
            success = await send_links_to_channel(bot, collected_links, keyword)
            status = "✅ تم النشر بنجاح!" if success else "⚠️ نُشر مع بعض الأخطاء"
            await bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=(
                    f"🏁 **اكتملت العملية!** {status}\n\n"
                    f"📊 الإحصائيات:\n"
                    f"✅ تم نشر: {found_count} سيرفر\n"
                    f"❌ مرفوض: {rejected}\n"
                    f"📡 مفحوص: {scanned} قناة"
                )
            )
        else:
            await bot.edit_message_text(
                chat_id=chat_id, message_id=message_id,
                text=(
                    f"❌ **لم أجد نتائج!**\n\n"
                    f"📡 مفحوص: {scanned} | ❌ مرفوض: {rejected}\n\n"
                    f"💡 جرب تخفيض العدد."
                )
            )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ: {str(e)[:200]}")
        except:
            pass

async def run_hunttxt_action(bot, chat_id, message_id, args):
    try:
        edit_state = {"time": 0}
        target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
        keyword = (
            " ".join(args[:-1]).lower()
            if len(args) > 1 and args[-1].isdigit()
            else ""
        )
        await safe_edit(bot, chat_id, message_id, f"🚀 **بدأ الصيد النصي...**\n🎯 {target_count}", edit_state, stop_button(), force=True)
        app = Client("wassim_fast_scraper", api_id=24974564, api_hash="b87511de89b42178862e13e84147952b", session_string=SESSION_STRING)
        await app.start()
        found_count, rejected, scanned = 0, 0, 0
        collected_links_raw, tested_urls = [], set()
        connector = aiohttp.TCPConnector(limit=20, limit_per_host=5)
        async with aiohttp.ClientSession(connector=connector) as session_req:
            async for dialog in app.get_dialogs():
                if found_count >= target_count:
                    break
                chat = dialog.chat
                if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
                    continue
                chat_name = (chat.title or str(chat.id)).lower()
                if not any(kw in chat_name for kw in TARGET_KEYWORDS):
                    continue
                scanned += 1
                await safe_edit(bot, chat_id, message_id, f"🔍 `{chat.title}`\n✅ {found_count}/{target_count}", edit_state, stop_button())
                urls_to_test = set()
                try:
                    async for msg in app.get_chat_history(chat.id, limit=100):
                        text = str(msg.text or msg.caption or "")
                        urls = re.findall(r'(https?://[^\s<>"]+)', text)
                        for u in urls:
                            if any(x in u.lower() for x in ['m3u', 'get.php', 'm3u8', 'playlist', 'list=']):
                                urls_to_test.add(u.rstrip('.,)'))
                except:
                    pass
                valid_urls = [u for u in urls_to_test if u not in tested_urls]
                tested_urls.update(valid_urls)
                if not valid_urls:
                    continue
                semaphore = asyncio.Semaphore(5)
                async def bounded_fetch(url, idx):
                    async with semaphore:
                        return await fetch_and_analyze(session_req, url, idx)
                tasks = [bounded_fetch(u, i) for i, u in enumerate(valid_urls)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for res in results:
                    if found_count >= target_count:
                        break
                    if isinstance(res, Exception) or not res or not res.get("success"):
                        rejected += 1
                        continue
                    groups = res["groups"]
                    if keyword:
                        filtered = defaultdict(list)
                        for g_name, entries in groups.items():
                            for extinf, curl, _ in entries:
                                if keyword in g_name.lower() or keyword in extinf.lower():
                                    filtered[g_name].append((extinf, curl, False))
                        groups = filtered
                    if not groups:
                        continue
                    fname = f"Hunter_{uuid.uuid4().hex[:6].upper()}.m3u"
                    write_m3u_and_get_count(groups, fname)
                    final_fname = compress_if_large(fname)
                    link = await upload_to_cloud(final_fname, "all")
                    safe_delete(fname)
                    if final_fname != fname:
                        safe_delete(final_fname)
                    if link:
                        collected_links_raw.append(link)
                        found_count += 1
                    else:
                        rejected += 1
        await app.stop()
        if collected_links_raw:
            txt_filename = f"Cloud_Links_{len(collected_links_raw)}_{uuid.uuid4().hex[:4]}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write("\n".join(collected_links_raw))
            with open(txt_filename, "rb") as f_send:
                await bot.send_document(chat_id=chat_id, document=f_send, caption=f"✅ **اكتمل الصيد النصي!**\n📦 {len(collected_links_raw)} روابط")
            safe_delete(txt_filename)
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ لم أجد نتائج.\n📡 {scanned} | ❌ {rejected}")
    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ: {str(e)[:200]}")

async def run_scrape_action(bot, chat_id, message_id, args):
    try:
        edit_state = {"time": 0}
        target_count = int(args[0])
        await safe_edit(bot, chat_id, message_id, f"⚡ **بدأ السحب السريع...** 🎯 {target_count}", edit_state, stop_button(), force=True)
        app = Client("wassim_fast_scraper", api_id=24974564, api_hash="b87511de89b42178862e13e84147952b", session_string=SESSION_STRING)
        await app.start()
        all_links = []
        async for dialog in app.get_dialogs():
            chat = dialog.chat
            if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
                continue
            try:
                async for msg in app.get_chat_history(chat.id, limit=100):
                    text = str(msg.text or msg.caption or "")
                    urls = re.findall(r'(https?://[^\s<>"]+)', text)
                    for u in urls:
                        if any(x in u.lower() for x in ['m3u', 'get.php', 'm3u8', 'playlist']):
                            all_links.append(u.rstrip('.,)'))
                if len(all_links) >= target_count * 3:
                    break
            except:
                pass
        await app.stop()
        final_links = list(dict.fromkeys(all_links))[:target_count]
        if final_links:
            txt_filename = f"Scraped_{len(final_links)}_{uuid.uuid4().hex[:4]}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f:
                f.write("\n".join(final_links))
            with open(txt_filename, "rb") as f_send:
                await bot.send_document(chat_id=chat_id, document=f_send, caption=f"⚡ **اكتمل السحب!**\n📦 {len(final_links)} رابط")
            safe_delete(txt_filename)
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ لم يتم العثور على روابط.")
    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ: {str(e)[:200]}")

# ================== المحرك الرئيسي ==================
async def main():
    if not SESSION_STRING:
        exit(1)
    bot = Bot(token=TOKEN)
    payload = json.loads(os.environ.get("PAYLOAD", "{}"))
    action = payload.get("action")
    chat_id = payload.get("chat_id")
    message_id = payload.get("message_id")
    print(f"🚀 Action: {action} | Chat: {chat_id} | Msg: {message_id}")
    if not chat_id or not action:
        return
    try:
        if action == "hunt":
            await run_hunter_action(bot, chat_id, message_id, payload.get("args", []))
        elif action == "hunttxt":
            await run_hunttxt_action(bot, chat_id, message_id, payload.get("args", []))
        elif action == "scrape":
            await run_scrape_action(bot, chat_id, message_id, payload.get("args", []))
        elif action == "process_file":
            await safe_edit(bot, chat_id, message_id, "⚙️ **المصنع يعالج الملف...** ⏳", {"time": 0}, stop_button(), force=True)
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
            if final_file != out_file:
                safe_delete(final_file)
            msg = (
                f"✅ **اكتمل التنظيف!**\n\n"
                f"📡 إجمالي: {total:,}\n"
                f"🔞 محذوف: {adult:,}\n\n"
                f"🔗 **GitHub:**\n`{git_link or '❌ فشل'}`\n\n"
                f"🔗 **Catbox:**\n`{catbox_link or '❌ فشل'}`"
            )
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=msg, parse_mode="Markdown")
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ: {str(e)[:200]}")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(main())
