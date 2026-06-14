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
import urllib.parse
from datetime import datetime
from collections import defaultdict
import aiohttp

from pyrogram import Client, enums
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

# ================== ظƒظˆط¯ ط§ظ„ظƒط´ظپ ظˆط§ظ„ط±ط¨ط· ط¨ط§ظ„ط®ط²ظ†ط© ط§ظ„ط³ط±ظٹط© ==================
print("ًں”چ DEBUG: ط¬ط§ط±ظٹ ظپط­طµ ظ…طھط؛ظٹط±ط§طھ ط§ظ„ط¨ظٹط¦ط© ظˆط§ظ„ط®ط²ظ†ط© ط§ظ„ط³ط±ظٹط©...")
s_str = os.environ.get("MY_SESSION_STRING", "").strip()
print(f"ًں”چ DEBUG: ط·ظˆظ„ ظƒظˆط¯ ط§ظ„ط¬ظ„ط³ط© ط§ظ„ظ…ط³طھظ„ظ… ظ‡ظˆ: {len(s_str)} ط­ط±ظپ")

if not s_str:
    print("â‌Œ CRITICAL ERROR: ظƒظˆط¯ ط§ظ„ط¬ظ„ط³ط© ظپط§ط±ط؛! طھط£ظƒط¯ ظ…ظ† ط¥ط¹ط¯ط§ط¯ط§طھ Repository Secrets.")
    exit(1)

# ================== ط¨ظٹط§ظ†ط§طھظƒ ط§ظ„ط³ط±ظٹط© ط§ظ„ظ…ط­ظ…ظٹط© ط§ظ„ظ…ط³طھط±ط¬ط¹ط© ==================
TOKEN = os.environ.get("MY_TELEGRAM_TOKEN")
GITHUB_TOKEN = os.environ.get("MY_GITHUB_TOKEN")
GITHUB_USER = "Mesbahikarim03-svg"
REPO_NAME = "krimo.-Iptv"
SESSION_STRING = s_str

MAX_FILE_SIZE_MB = 150
MIN_CHANNELS_REQUIRED = 1000
CHANNEL_ID = "@free_iptv_world"
CHANNEL_NAME_FOR_FILE = "FREE_IPTV_WORLD"

# ================== ط¥ط¹ط¯ط§ط¯ط§طھ ط§ظ„ط³ط±ط¹ط© ط§ظ„ظ‚طµظˆظ‰ (TURBO MODE) ==================
MAX_PARALLEL_DIALOGS = 5          # ط¹ط¯ط¯ ط§ظ„ظ‚ظ†ظˆط§طھ ط§ظ„طھظٹ ظٹطھظ… ظپط­طµظ‡ط§ ط¨ظ†ظپط³ ط§ظ„ظˆظ‚طھ
MAX_PARALLEL_FETCHES = 25         # ط¹ط¯ط¯ ط§ظ„ط±ظˆط§ط¨ط· ط§ظ„طھظٹ ظٹطھظ… طھط­ظ„ظٹظ„ظ‡ط§ ط¨ظ†ظپط³ ط§ظ„ظˆظ‚طھ
MAX_PARALLEL_UPLOADS = 6          # ط¹ط¯ط¯ ط§ظ„ط±ظپط¹ط§طھ ط§ظ„ط³ط­ط§ط¨ظٹط© ط§ظ„ظ…طھظˆط§ط²ظٹط©
HISTORY_LIMIT = 80                # ط±ط³ط§ط¦ظ„ ط£ظƒط«ط± ظ…ظ† ظƒظ„ ظ‚ظ†ط§ط© ظ„ظ„طµظٹط¯ ط§ظ„ط¹ظ…ظٹظ‚
FETCH_TIMEOUT = 15.0              # طھظ‚ظ„ظٹطµ ط§ظ„ظ€ timeout ظ„ظ„ط³ط±ط¹ط©
ALIVE_CHECK_SAMPLE = 5            # ط¹ط¯ط¯ ط§ظ„ط±ظˆط§ط¨ط· ظ„ظ„ظپط­طµ ط§ظ„ط­ظٹظˆظٹ

DIALOG_SEM = None  # طھظڈظ‡ظٹط£ ط¯ط§ط®ظ„ main ظ„ط£ظ†ظ‡ط§ async-bound
FETCH_SEM = None
UPLOAD_SEM = None

MY_CHANNELS = ["ط¹ط§ظ„ظ… iptv ظ…ط¬ط§ظ†ظٹ", "ط¯ط±ط¯ط´ط© ظ…ط¬ط§ظ†ظٹط© ط¹ط¨ط± ط§ظ„ط¥ظ†طھط±ظ†طھ", "طھط­ط¯ظٹط« ظ…ط¬ط§ظ†ظٹ ظ„ط¹ط§ظ„ظ… ط§ظ„ط¨ط« ط¹ط¨ط± ط§ظ„ط¥ظ†طھط±ظ†طھ"]
TARGET_KEYWORDS = ["iptv", "m3u", "xtream", "mac", "portal", "sat", "tv", "server", "stb", "cccam", "streaming", "restream", "codes", "vip", "app"]

ADULT_WORDS = ["xxx", "porn", "adult", "adults", "sex", "18+", "+18", "erotic", "playboy", "amateur", "onlyfans", "brazzers", "vivid", "hustler", "penthouse", "babes", "realitykings", "naughty", "bangbros", "milf", "lesbian", "gay", "cam", "nsfw", "x-art", "babe", "pussy", "dick", "matures", "hardcore", "xnxx", "xvideos", "pornhub", "redtube", "kamasutra", "peep"]
ADULT_REGEX = re.compile(r'(?i)(?:' + '|'.join(map(re.escape, ADULT_WORDS)) + r')')
GROUP_TITLE_REGEX = re.compile(r'group-title="([^"]*)"')

WARNING_TEXT = """<blockquote>âڑ ï¸ڈ <b>ATTENTION / ط§ظ†طھط¨ط§ظ‡:</b>
Links are valid for <b>10 HOURS</b> from publishing, then they will be deleted automatically. Download them NOW!
ظ…ط¯ط© ط§ظ„ط±ظˆط§ط¨ط· 10 ط³ط§ط¹ط§طھ ظپظ‚ط· ظ…ظ† ظˆظ‚طھ ط§ظ„ظ†ط´ط± ط«ظ… ط³ظٹطھظ… ط­ط°ظپظ‡ط§. ظٹط±ط¬ظ‰ ط§ظ„طھط­ظ…ظٹظ„ ط£ظˆ ط§ظ„ظ†ط³ط® ط§ظ„ط¢ظ†!</blockquote>\n\n"""

# ============== ط§ظ„ظ‚ط§ظ„ط¨ ط§ظ„ط£طµظ„ظٹ ظ„ظ„ط±ظˆط§ط¨ط· (ظ„ظ… ظٹظڈط؛ظٹظ‘ط± ط¥ط·ظ„ط§ظ‚ط§ظ‹) ==============
LINK_POST_CAPTION = """ًں”— ً‌——ً‌—œً‌—¥ً‌—کً‌—–ً‌—§ ً‌—œو”؟ً‌—§ً‌—© ً‌—ںً‌—œً‌—،ً‌—‍ً‌—¦ ًں”—
ًںŒچ ً‌—™ً‌—¥ً‌—کً‌—ک ً‌—œً‌—£ً‌—§ً‌—© ً‌—ھً‌—¢ً‌—¥ً‌—ںً‌—— ًںŒچ

<blockquote>âڑ ï¸ڈ <b>ط¥ط¨ط±ط§ط، ط°ظ…ط©:</b>
ظ†ط¨ط±ط£ ط¥ظ„ظ‰ ط§ظ„ظ„ظ‡ ظ…ظ† ط£ظٹ ط§ط³طھط®ط¯ط§ظ… ط³ظٹط، ط£ظˆ ط§ظ„ط¯ط®ظˆظ„ ظ„ظ‚ظ†ظˆط§طھ ط؛ظٹط± ظ„ط§ط¦ظ‚ط©. ًں¤²</blockquote>

ًںڑ€ ً‌—›ً‌—¶ً‌—´ً‌—µ-ً‌—¦ً‌—½ً‌—²ً‌—²dw ً‌—ںً‌—¶ً‌—»ً‌—¸ï½“:
{links}

<blockquote>ًں“ٹ ً‌—¦ً‌—²ً‌—؟ً‌کƒً‌—²ً‌—؟ ً‌——ً‌—²ً‌کپً‌—®ً‌—¶ً‌—¹ً‌ک€:
â”œ ًں“¦ ً‌—–ً‌—¼ً‌—»ً‌کپً‌—²ً‌—»ً‌کپ: Premium Channels & VODs
â”œ âڑ، ً‌—™ً‌—¼ً‌—؟ً‌—؛ً‌—®ً‌کپ: M3U & Xtream Codes
â”œ âڑ½ï¸ڈ ً‌—¦ً‌—½ً‌—¼ً‌—؟ً‌کپً‌ک€: beIN, SSC, Sky, TNT
â”œ ًںژ¬ ً‌— ً‌—¼ً‌کƒً‌—¶ً‌—²ً‌ک€: Netflix, OSN, Disney+
â”” ًں“± ً‌——ً‌—²ً‌کƒً‌—¶ً‌—°ً‌—²ً‌ک€: Smart TV, Android, iOS, PC

ًںŒچ ً‌—ھً‌—¼ً‌—؟ً‌—¹ً‌—±ً‌ک„ً‌—¶ً‌—±ً‌—² ً‌—–ً‌—µً‌—®ً‌—»ً‌—»ً‌—²ً‌—¹ً‌ک€ (ً‌—©ً‌—œً‌—£):
ًں‡©ًں‡؟ ط§ظ„ط¬ط²ط§ط¦ط± | ًں‡²ًں‡¦ ط§ظ„ظ…ط؛ط±ط¨ | ًں‡¹ًں‡³ طھظˆظ†ط³ | ًں‡ھًں‡¬ ظ…طµط± | ًں‡¸ًں‡¦ ط§ظ„ط³ط¹ظˆط¯ظٹط© | ًں‡¦ًں‡ھ ط§ظ„ط¥ظ…ط§ط±ط§طھ
ًں‡«ًں‡· France | ًں‡¬ًں‡§ UK | ًں‡؛ًں‡¸ USA | ًں‡©ًں‡ھ Germany | ًں‡®ًں‡¹ Italy | ًں‡ھًں‡¸ Spain
ًں‡¨ًں‡¦ Canada | ًں‡³ًں‡± Netherlands | ًں‡§ًں‡ھ Belgium | ًں‡¸ًں‡ھ Sweden | ًں‡¨ًں‡­ Swiss
ًں‡¹ًں‡· Tأ¼rkiye |
... <b>And Many More!</b> ًں”¥</blockquote>

âڑ™ï¸ڈ ً‌—›ً‌—¼ً‌ک„ ً‌کپً‌—¼ ً‌ک‚ً‌ک€ً‌—²?
1ï¸ڈâƒ£ Copy the link above.
2ï¸ڈâƒ£ Open your IPTV Player (Smarters, Tivimate, VLC).
3ï¸ڈâƒ£ Select "Add Playlist / M3U URL".
4ï¸ڈâƒ£ Paste & Enjoy! ًںچ؟

â™»ï¸ڈ ً‌ک—ً‌ک­ً‌ک¦ً‌ک¢ً‌ک´ً‌ک¦ ً‌کڑً‌ک©ً‌ک¢ً‌ک³ً‌ک¦ & ً‌کڑد…ً‌ک±ً‌ک±ً‌ک°ً‌ک³ً‌کµ ً‌کœً‌ک´!"""

# ============== ظ‚ط§ظ„ط¨ ط¨ط³ظٹط· ط§ط­طھط±ط§ظپظٹ ظ„ظ„طµظˆط±ط© (ط¨ط¯ظˆظ† ط±ظˆط§ط¨ط·) ==============
IMAGE_SIMPLE_CAPTION = """ًںŒچ <b>ً‌—™ً‌—¥ً‌—کً‌—ک ً‌—œً‌—£ً‌—§ً‌—© ً‌—ھً‌—¢ً‌—¥ً‌—ںً‌——</b> ًںŒچ
â”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پ

ًں”¥ <b>{title}</b>

ًں“¦ ط¹ط¯ط¯ ط§ظ„ط³ظٹط±ظپط±ط§طھ: <b>{count}</b>
âڑ، ط§ظ„ط¬ظˆط¯ط©: <b>4K / FHD / HD</b>
ًں›°ï¸ڈ ط§ظ„طھط­ط¯ظٹط«: <b>{date}</b>

ًںژ¬ Movies â€¢ âڑ½ Sports â€¢ ًں“؛ Live TV
ًںŒگ Worldwide Channels (VIP)

â”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پâ”پ
ًں‘‡ <i>ط§ظ„ط±ظˆط§ط¨ط· ظپظٹ ط§ظ„ظ…ظ†ط´ظˆط± ط§ظ„طھط§ظ„ظٹ</i> ًں‘‡"""


def build_post_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("ًں“£ ً‌—¢ً‌ک‚ً‌—؟ ً‌—–ً‌—µً‌—®ً‌—»ً‌—»ً‌—²ً‌—¹", url="https://t.me/free_iptv_world"), InlineKeyboardButton("ًں’¬ ً‌—¢ً‌ک‚ً‌—؟ ً‌—ڑً‌—؟ً‌—¼ً‌ک‚ً‌—½", url="https://t.me/FREE_IPTV_WORLD_CHAT")],
        [InlineKeyboardButton("ًں”پ ً‌—¦ً‌—µً‌—®ً‌—؟ً‌—² ً‌—£ً‌—¼ً‌ک€ً‌کپ", url="https://t.me/share/url?url=https://t.me/free_iptv_world&text=ًں”¥%20ط£ظ‚ظˆظ‰%20ط³ظٹط±ظپط±ط§طھ%20IPTV%20ظ…ط¬ط§ظ†ط§ظ‹%20ًں”¥")]
    ])

def stop_button():
    return InlineKeyboardMarkup([[InlineKeyboardButton("ًں›‘ ط¥ظٹظ‚ط§ظپ ط§ظ„ط¹ظ…ظ„ظٹط©", callback_data="cancel_process")]])

def safe_delete(filepath):
    try:
        if os.path.exists(filepath): os.remove(filepath)
    except: pass

async def is_link_working(url):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
                return response.status == 200
    except: return False

# ================== طھظˆظ„ظٹط¯ ط¨ظˆط³طھط± ط§ط­طھط±ط§ظپظٹ ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ ==================
async def generate_ai_poster(title_text, server_count, keyword=""):
    """
    ظٹظˆظ„ظ‘ط¯ طµظˆط±ط© ط¨ظˆط³طھط± ط§ط­طھط±ط§ظپظٹط© ط¹ط¨ط± Pollinations.ai (ظ…ط¬ط§ظ†ظٹطŒ ط¨ط¯ظˆظ† API key).
    ظٹط¹ظ…ظ„ ط¶ظ…ظ† GitHub Actions ط¨ط¯ظˆظ† ط£ظٹ ظ…ظپط§طھظٹط­ ط¥ط¶ط§ظپظٹط©.
    ظٹظڈط±ط¬ط¹ ظ…ط³ط§ط± ط§ظ„ظ…ظ„ظپ ط§ظ„ظ…ط­ظ„ظٹ ظ„ظ„طµظˆط±ط© ط§ظ„ظ…ظˆظ„ظ‘ط¯ط©طŒ ط£ظˆ None ط¥ط°ط§ ظپط´ظ„.
    """
    try:
        kw_part = f", {keyword.upper()} edition" if keyword else ""
        prompt = (
            f"Ultra professional cinematic IPTV streaming poster, dark navy and gold luxury theme, "
            f"glowing neon 'FREE IPTV WORLD' logo at top center, premium 4K TV channels mosaic background, "
            f"world map with glowing connection lines, sports football movies netflix style icons, "
            f"high-end modern minimalist design, bold elegant typography, "
            f"text '{title_text}' embossed in metallic gold{kw_part}, "
            f"premium VIP badge, satellite dish silhouette, "
            f"highly detailed, 8k, sharp focus, dramatic lighting, no people, no faces"
        )
        # Pollinations endpoint â€” ظ…ط¬ط§ظ†ظٹ طھظ…ط§ظ…ط§ظ‹
        encoded = urllib.parse.quote(prompt)
        seed = random.randint(1, 9999999)
        url = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?width=1280&height=720&nologo=true&enhance=true&seed={seed}&model=flux"
        )

        out_path = f"poster_{uuid.uuid4().hex[:8]}.jpg"
        timeout = aiohttp.ClientTimeout(total=90)
        # ظ…ط­ط§ظˆظ„طھط§ظ† ظ„ظ„ظ…ظˆط«ظˆظ‚ظٹط©
        for attempt in range(2):
            try:
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                        if resp.status == 200:
                            data = await resp.read()
                            if data and len(data) > 5000:  # طھط­ظ‚ظ‚ ظ…ظ† ط£ظ† ط§ظ„طµظˆط±ط© ظ„ظٹط³طھ ظپط§ط±ط؛ط©
                                with open(out_path, "wb") as f:
                                    f.write(data)
                                return out_path
            except Exception:
                await asyncio.sleep(2)
        return None
    except Exception as e:
        print(f"âڑ ï¸ڈ AI poster generation failed: {e}")
        return None


async def send_post_with_ai_image(bot, channel_id, title_text, server_count, keyword, full_caption_with_links):
    """
    ظٹظ†ط´ط± ظ…ظ†ط´ظˆط±ظٹظ† ظ…طھطھط§ظ„ظٹظٹظ† ظپظٹ ظ‚ظ†ط§ط© Telegram:
    1) طµظˆط±ط© AI ط§ط­طھط±ط§ظپظٹط© ظ…ط¹ ظ‚ط§ظ„ط¨ ظƒط§ط¨ط´ظ† ط¨ط³ظٹط· (ط¨ط¯ظˆظ† ط±ظˆط§ط¨ط·)
    2) ط§ظ„ظ…ظ†ط´ظˆط± ط§ظ„ط£طµظ„ظٹ ط¨ط§ظ„ط±ظˆط§ط¨ط· ط¨ط§ظ„ظ‚ط§ظ„ط¨ ط§ظ„ظƒط§ظ…ظ„ ط¨ط¯ظˆظ† طھط؛ظٹظٹط±
    """
    # 1) طµظˆط±ط© ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ
    poster_path = await generate_ai_poster(title_text, server_count, keyword)
    img_caption = IMAGE_SIMPLE_CAPTION.format(
        title=title_text,
        count=server_count,
        date=datetime.now().strftime("%Y-%m-%d")
    )

    if poster_path and os.path.exists(poster_path):
        try:
            with open(poster_path, "rb") as ph:
                await bot.send_photo(
                    chat_id=channel_id,
                    photo=ph,
                    caption=img_caption,
                    parse_mode="HTML"
                )
        except Exception as e:
            print(f"âڑ ï¸ڈ send_photo failed, fallback to text header: {e}")
            try:
                await bot.send_message(
                    chat_id=channel_id, text=img_caption,
                    parse_mode="HTML", disable_web_page_preview=True
                )
            except: pass
        finally:
            safe_delete(poster_path)
    else:
        # ظپظٹ ط­ط§ظ„ ظپط´ظ„ طھظˆظ„ظٹط¯ ط§ظ„طµظˆط±ط©طŒ ط£ط±ط³ظ„ ط§ظ„ظƒط§ط¨ط´ظ† ط§ظ„ط¨ط³ظٹط· ظƒظ†طµ (ظ„ظƒظٹ ظ„ط§ ظٹطھط¹ط·ظ„ ط§ظ„ظ†ط´ط±)
        try:
            await bot.send_message(
                chat_id=channel_id, text=img_caption,
                parse_mode="HTML", disable_web_page_preview=True
            )
        except: pass

    # طھط£ط®ظٹط± طµط؛ظٹط± ظ„ط¶ظ…ط§ظ† طھط±طھظٹط¨ ط§ظ„ظ…ظ†ط´ظˆط±ط§طھ
    await asyncio.sleep(1.2)

    # 2) ط§ظ„ظ…ظ†ط´ظˆط± ط§ظ„ط£طµظ„ظٹ ط¨ط§ظ„ط±ظˆط§ط¨ط· â€” ط¨ط¯ظˆظ† ط£ظٹ طھط؛ظٹظٹط± ظپظٹ ط§ظ„ظ‚ط§ظ„ط¨
    await bot.send_message(
        chat_id=channel_id,
        text=full_caption_with_links,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=build_post_keyboard()
    )


# ================== ط§ظ„طھظ†ط¸ظٹظپ ظ…ظ† GitHub ==================
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
                            resp = requests.post("https://catbox.moe/user/api.php", data={'reqtype': 'fileupload', 'userhash': '4743fd4cd7b648c176c6e5800'}, files={'fileToUpload': (base_name, f, 'application/vnd.apple.mpegurl')})
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
                    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
                        with open(filename, 'rb') as f:
                            data = aiohttp.FormData()
                            data.add_field('files[]', f, filename=base_name)
                            async with session.post("https://uguu.se/upload.php", data=data) as response:
                                if response.status == 200:
                                    res = await response.json()
                                    if res.get("success"): link = res["files"][0]["url"]
                elif api == "litterbox":
                    async with aiohttp.ClientSession(timeout=custom_timeout) as session:
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


# ظ†ط³ط®ط© ظ…ط­ظ…ظٹط© ط¨ظ€ semaphore ظ„ط¶ظ…ط§ظ† ط¹ط¯ظ… طھط¬ط§ظˆط² ط§ظ„ط­ط¯ ط§ظ„ط£ط¹ظ„ظ‰ ظ„ظ„ط±ظپط¹ ط§ظ„ظ…طھظˆط§ط²ظٹ
async def upload_to_cloud_sem(filename, selected_api="all"):
    global UPLOAD_SEM
    if UPLOAD_SEM is None:
        return await upload_to_cloud(filename, selected_api)
    async with UPLOAD_SEM:
        return await upload_to_cloud(filename, selected_api)


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
    promo = '#EXTINF:-1 tvg-id="Free.IPTV" tvg-name="FREE IPTV WORLD PROMO" tvg-logo="https://files.catbox.moe/goe4nn.jpg" group-title="ًںŒں FREE IPTV WORLD ًںŒں",ًں“؛ Welcome to FREE IPTV WORLD\r\nhttps://files.catbox.moe/npglfu.mp4\r\n'
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write("#EXTM3U\r\n" + promo)
        count += 1
        for g in groups.keys():
            for extinf, url, _ in groups[g]:
                extinf_fixed = extinf.replace('\n', '\r\n')
                if ',' in extinf_fixed:
                    parts = extinf_fixed.rsplit(',', 1)
                    if "FREE IPTV WORLD" not in parts[1]: extinf_branded = f"{parts[0]},{parts[1]} | ًںŒں FREE IPTV WORLD ًںŒں"
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
    test_urls = random.sample(all_valid_urls, min(ALIVE_CHECK_SAMPLE, len(all_valid_urls)))
    headers = {"User-Agent": "TiviMate/4.7.0 (Linux; Android 11)"}
    # طھظ‚ظ„ظٹطµ ط´ط¯ظٹط¯ ظ„ظ„ظ€ timeouts ظ„ط±ظپط¹ ط§ظ„ط³ط±ط¹ط©
    async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(sock_connect=2, sock_read=3)) as session:
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
    """
    ظ†ط³ط®ط© ظپط§ط¦ظ‚ط© ط§ظ„ط³ط±ط¹ط© â€” طھط³طھط®ط¯ظ… semaphore ط¹ط§ظ… ظ„طھط¬ظ†ط¨ ط§ظ„ط¥ط؛ط±ط§ظ‚طŒ
    ظˆchunk ط£ظƒط¨ط± (4MB)طŒ ظˆtimeout ط£ظ‚طµط± ظ„ط±ظپط¹ ط§ظ„ط¥ظ†طھط§ط¬ظٹط©.
    """
    global FETCH_SEM
    async def _fetch():
        try:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True) as response:
                if response.status in [200, 206]:
                    temp = f"temp_{uuid.uuid4().hex}.m3u"
                    with open(temp, 'wb') as f:
                        async for chunk in response.content.iter_chunked(4 * 1024 * 1024):
                            f.write(chunk)
                    groups, total, adult = await analyze_async(temp)
                    safe_delete(temp)
                    if total < MIN_CHANNELS_REQUIRED or not await is_playlist_alive(groups): return {"id": idx, "success": False}
                    return {"id": idx, "groups": groups, "total": total, "size_mb": get_clean_size_mb(groups), "success": True}
        except: pass
        return {"id": idx, "success": False}

    try:
        if FETCH_SEM is not None:
            async with FETCH_SEM:
                return await asyncio.wait_for(_fetch(), timeout=FETCH_TIMEOUT)
        return await asyncio.wait_for(_fetch(), timeout=FETCH_TIMEOUT)
    except: return {"id": idx, "success": False}

async def safe_edit(bot, chat_id, message_id, text, edit_state, markup=None, force=False):
    if force or (time.time() - edit_state["time"] > 3.0):
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, parse_mode="Markdown", reply_markup=markup)
            edit_state["time"] = time.time()
        except: pass


# ================== ظ…ظڈط³ط§ط¹ط¯ ط¬ط¯ظٹط¯: ط§ط³طھط®ط±ط§ط¬ ط±ظˆط§ط¨ط· ط±ط³ط§ط¦ظ„ ظ‚ظ†ط§ط© ط¨ط§ظ„طھظˆط§ط²ظٹ ==================
async def extract_urls_from_chat(app, chat_id_pyro, limit=HISTORY_LIMIT):
    """ظٹط¬ظ…ط¹ ظƒظ„ ط±ظˆط§ط¨ط· m3u/get.php ظ…ظ† ط¢ط®ط± `limit` ط±ط³ط§ظ„ط© ظپظٹ ظ‚ظ†ط§ط©."""
    urls = set()
    try:
        async for msg in app.get_chat_history(chat_id_pyro, limit=limit):
            text = str(msg.text or msg.caption or "")
            if not text:
                continue
            found = re.findall(r'(https?://[^\s]+)', text)
            for u in found:
                lu = u.lower()
                if 'm3u' in lu or 'get.php' in lu:
                    urls.add(u)
    except:
        pass
    return urls


# ================== 1. ط¯ط§ظ„ط© ط§ظ„طµظٹط¯ ط§ظ„طھظ„ظ‚ط§ط¦ظٹ ظˆط§ظ„ظ…ظˆط§ط²ظٹ (TURBO) ==================
async def run_hunter_action(bot, chat_id, message_id, args):
    global DIALOG_SEM, FETCH_SEM
    try:
        edit_state = {"time": 0}
        target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
        keyword = " ".join(args[:-1]).lower() if len(args) > 1 and args[-1].isdigit() else (" ".join(args[1:]).lower() if len(args) > 1 else "")

        await safe_edit(bot, chat_id, message_id, "ًںڑ€ **ط¨ط¯ط£ ط§ظ„طµظٹط¯ ط§ظ„ظ…ط¨ط§ط´ط± ط¨ط§ظ„طھظˆط±ط¨ظˆ ط§ظ„ظپط§ط¦ظ‚...**", edit_state, stop_button(), force=True)

        app = Client("wassim_fast_scraper", api_id=24974564, api_hash="b87511de89b42178862e13e84147952b", session_string=SESSION_STRING)
        await app.start()

        found_count, scanned, collected_links, tested_urls = 0, 0, [], set()
        found_lock = asyncio.Lock()

        # ط¬ظ„ط³ط© aiohttp ظˆط§ط­ط¯ط© ظ…ط¹ connector ظ…ط­ط³ظ‘ظ† ظ„ظ„ط³ط±ط¹ط© ط§ظ„ظ‚طµظˆظ‰
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=20, ttl_dns_cache=300, use_dns_cache=True)
        async with aiohttp.ClientSession(connector=connector) as session_req:

            # ظ†ط¬ظ…ط¹ ظƒظ„ ط§ظ„ظ‚ظ†ظˆط§طھ ط§ظ„ظ…ط³طھظ‡ط¯ظپط© ط£ظˆظ„ط§ظ‹
            target_chats = []
            async for dialog in app.get_dialogs():
                chat = dialog.chat
                if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
                    continue
                chat_name = chat.title or str(chat.id)
                if any(kw in chat_name.lower() for kw in TARGET_KEYWORDS):
                    target_chats.append((chat.id, chat_name))

            await safe_edit(bot, chat_id, message_id, f"ًںژ¯ **طھظ… ط§ظƒطھط´ط§ظپ {len(target_chats)} ظ‚ظ†ط§ط© ظ‡ط¯ظپ. ط¨ط¯ط، ط§ظ„ظ…ط¹ط§ظ„ط¬ط© ط§ظ„ظ…طھظˆط§ط²ظٹط©...**", edit_state, stop_button(), force=True)

            async def process_one_chat(chat_id_pyro, chat_name):
                nonlocal found_count, scanned, collected_links, tested_urls
                async with DIALOG_SEM:
                    if found_count >= target_count:
                        return
                    scanned += 1
                    await safe_edit(bot, chat_id, message_id, f"ًں”چ **ظپط­طµ:** {chat_name}\nâœ… ط§ظ„ظ…ط¬ظ‡ط²: {found_count}/{target_count}", edit_state, stop_button())

                    urls_to_test = await extract_urls_from_chat(app, chat_id_pyro, limit=HISTORY_LIMIT)

                    async with found_lock:
                        valid_urls = [u for u in urls_to_test if u not in tested_urls]
                        tested_urls.update(valid_urls)

                    if not valid_urls:
                        return

                    tasks = [fetch_and_analyze(session_req, u, i) for i, u in enumerate(valid_urls)]
                    results = await asyncio.gather(*tasks)

                    # ط±ظپط¹ ظ…طھظˆط§ط²ظٹ ظ„ظ„ظ†طھط§ط¦ط¬ ط§ظ„ظ†ط§ط¬ط­ط©
                    async def handle_result(res):
                        nonlocal found_count, collected_links
                        if found_count >= target_count:
                            return
                        if not (res and res.get("success")):
                            return
                        groups = res["groups"]
                        if keyword:
                            filtered = defaultdict(list)
                            for g_name, entries in groups.items():
                                for extinf, curl, _ in entries:
                                    if keyword in g_name.lower() or keyword in extinf.lower():
                                        filtered[g_name].append((extinf, curl, False))
                            groups = filtered
                        if not groups:
                            return

                        fname = f"Hunter_{uuid.uuid4().hex[:4].upper()}.m3u"
                        write_m3u_and_get_count(groups, fname)
                        link = await upload_to_cloud_sem(compress_if_large(fname), "all")
                        safe_delete(fname)
                        if link:
                            async with found_lock:
                                if found_count < target_count:
                                    found_count += 1
                                    collected_links.append(f"ًں”¹ <b>ط§ظ„ط¨ط§ظ‚ط© {found_count}:</b> <code>{link}</code>")
                                    await safe_edit(bot, chat_id, message_id, f"ًںژ‰ **طµظٹط¯ ظ‚ظˆظٹ!**\nâœ… ط§ظ„ظ…ط¬ظ‡ط²: {found_count}/{target_count}", edit_state, stop_button(), force=True)

                    await asyncio.gather(*[handle_result(r) for r in results])

            # طھط´ط؛ظٹظ„ ط§ظ„ظ‚ظ†ظˆط§طھ ط¨ط§ظ„طھظˆط§ط²ظٹ
            await asyncio.gather(*[process_one_chat(cid, cname) for cid, cname in target_chats])

        await app.stop()

        if collected_links:
            # ط¹ظ†ظˆط§ظ† ظ…ط®طµطµ ظ„ظ„ط¨ط§ظ‚ط©
            if keyword:
                cap_title = f"ًں”¥ ً‌—کً‌—«ً‌—–ً‌—ںً‌—¨ً‌—¦ً‌—œً‌—©ً‌—ک ً‌—¦ً‌—کً‌—¥ً‌—©ً‌—کً‌—¥: {keyword.upper()} ًں”¥"
                ai_title = f"EXCLUSIVE {keyword.upper()} SERVER"
            else:
                cap_title = "ًں”— ً‌——ً‌—œً‌—¥ً‌—کً‌—–ً‌—§ ً‌—œً‌—£ً‌—§ً‌—© ً‌—ںً‌—œً‌—،ً‌—‍ً‌—¦ ًں”—"
                ai_title = "DIRECT IPTV LINKS"

            # ط§ظ„ظ‚ط§ظ„ط¨ ط§ظ„ط£طµظ„ظٹ ط¨ط§ظ„ظƒط§ظ…ظ„ ط¨ط¯ظˆظ† ط£ظٹ طھط؛ظٹظٹط± ظپظٹ ط¨ظ†ظٹطھظ‡ â€” ظپظ‚ط· ظ†ط³طھط¨ط¯ظ„ ط¹ظ†ظˆط§ظ†ظ‡ ظˆط§ظ„ط±ظˆط§ط¨ط·
            caption = WARNING_TEXT + LINK_POST_CAPTION.replace("ًں”— ً‌——ً‌—œً‌—¥ً‌—کً‌—–ً‌—§ ً‌—œو”؟ً‌—§ً‌—© ً‌—ںً‌—œً‌—،ً‌—‍ً‌—¦ ًں”—", cap_title).replace("{links}", "\n\n".join(collected_links))

            # âœ¨ ط§ظ„ظ†ط´ط± ط§ظ„ط¬ط¯ظٹط¯: طµظˆط±ط© AI ط£ظˆظ„ط§ظ‹ ط«ظ… ط§ظ„ط±ظˆط§ط¨ط· (ط§ظ„ظ‚ط§ظ„ط¨ ط§ظ„ط£طµظ„ظٹ)
            await send_post_with_ai_image(
                bot=bot,
                channel_id=CHANNEL_ID,
                title_text=ai_title,
                server_count=found_count,
                keyword=keyword,
                full_caption_with_links=caption
            )

            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"ًںڈپ **ط§ظƒطھظ…ظ„طھ ط§ظ„ط¹ظ…ظ„ظٹط© ط¨ظ†ط¬ط§ط­!** طھظ… ظ†ط´ط± {found_count} ط³ظٹط±ظپط± ط¨طµظˆط±ط© ط§ط­طھط±ط§ظپظٹط© ط¨ط§ظ„ط°ظƒط§ط، ط§ظ„ط§طµط·ظ†ط§ط¹ظٹ.")
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="â‌Œ ظ„ظ… ط£ط¬ط¯ ظ†طھط§ط¦ط¬ ظ…ط·ط§ط¨ظ‚ط©.")
    except Exception as e:
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"â‌Œ ط®ط·ط£: {e}")
        except: pass


# ================== 2. ط¯ط§ظ„ط© ط§ظ„طµظٹط¯ ظƒظ…ظ„ظپ ظ†طµظٹ (hunttxt) â€” TURBO ==================
async def run_hunttxt_action(bot, chat_id, message_id, args):
    global DIALOG_SEM
    try:
        edit_state = {"time": 0}
        target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
        keyword = " ".join(args[:-1]).lower() if len(args) > 1 and args[-1].isdigit() else (" ".join(args[1:]).lower() if len(args) > 1 else "")

        await safe_edit(bot, chat_id, message_id, "ًںڑ€ **ط¨ط¯ط£ ط§ظ„طµظٹط¯ ط§ظ„ظ†طµظٹ ط¨ط§ظ„طھظˆط±ط¨ظˆ ط§ظ„ظ…ظˆط§ط²ظٹ...**", edit_state, stop_button(), force=True)

        app = Client("wassim_fast_scraper", api_id=24974564, api_hash="b87511de89b42178862e13e84147952b", session_string=SESSION_STRING)
        await app.start()

        found_count, scanned, collected_links_raw, tested_urls = 0, 0, [], set()
        found_lock = asyncio.Lock()

        connector = aiohttp.TCPConnector(limit=100, limit_per_host=20, ttl_dns_cache=300, use_dns_cache=True)
        async with aiohttp.ClientSession(connector=connector) as session_req:
            target_chats = []
            async for dialog in app.get_dialogs():
                chat = dialog.chat
                if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
                    continue
                chat_name = chat.title or str(chat.id)
                if any(kw in chat_name.lower() for kw in TARGET_KEYWORDS):
                    target_chats.append((chat.id, chat_name))

            await safe_edit(bot, chat_id, message_id, f"ًںژ¯ **طھظ… ط§ظƒطھط´ط§ظپ {len(target_chats)} ظ‚ظ†ط§ط©. ط¨ط¯ط، ط§ظ„ظپط­طµ ط§ظ„ظ…طھظˆط§ط²ظٹ...**", edit_state, stop_button(), force=True)

            async def process_one_chat(chat_id_pyro, chat_name):
                nonlocal found_count, scanned, collected_links_raw, tested_urls
                async with DIALOG_SEM:
                    if found_count >= target_count:
                        return
                    scanned += 1
                    await safe_edit(bot, chat_id, message_id, f"ًں”چ **ظپط­طµ:** {chat_name}\nâœ… ط§ظ„ظ…ط³طھط®ط±ط¬: {found_count}/{target_count}", edit_state, stop_button())

                    urls_to_test = await extract_urls_from_chat(app, chat_id_pyro, limit=HISTORY_LIMIT)

                    async with found_lock:
                        valid_urls = [u for u in urls_to_test if u not in tested_urls]
                        tested_urls.update(valid_urls)

                    if not valid_urls:
                        return

                    tasks = [fetch_and_analyze(session_req, u, i) for i, u in enumerate(valid_urls)]
                    results = await asyncio.gather(*tasks)

                    async def handle_result(res):
                        nonlocal found_count, collected_links_raw
                        if found_count >= target_count:
                            return
                        if not (res and res.get("success")):
                            return
                        groups = res["groups"]
                        if keyword:
                            filtered = defaultdict(list)
                            for g_name, entries in groups.items():
                                for extinf, curl, _ in entries:
                                    if keyword in g_name.lower() or keyword in extinf.lower():
                                        filtered[g_name].append((extinf, curl, False))
                            groups = filtered
                        if not groups:
                            return

                        fname = f"Hunter_{uuid.uuid4().hex[:4].upper()}.m3u"
                        write_m3u_and_get_count(groups, fname)
                        link = await upload_to_cloud_sem(compress_if_large(fname), "all")
                        safe_delete(fname)
                        if link:
                            async with found_lock:
                                if found_count < target_count:
                                    found_count += 1
                                    collected_links_raw.append(link)
                                    await safe_edit(bot, chat_id, message_id, f"ًںژ‰ **طھظ… ط§ظ„طھط¬ظ‡ظٹط²!**\nâœ… ط§ظ„ظ…ط³طھط®ط±ط¬: {found_count}/{target_count}", edit_state, stop_button(), force=True)

                    await asyncio.gather(*[handle_result(r) for r in results])

            await asyncio.gather(*[process_one_chat(cid, cname) for cid, cname in target_chats])

        await app.stop()

        if collected_links_raw:
            txt_filename = f"Cloud_Links_{target_count}_{uuid.uuid4().hex[:4]}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f: f.write("\n".join(collected_links_raw))
            with open(txt_filename, "rb") as f_send:
                await bot.send_document(chat_id=chat_id, document=f_send, caption=f"âœ… **ط§ظƒطھظ…ظ„ طµظٹط¯ ط§ظ„ظ…ظ„ظپ ط§ظ„ظ†طµظٹ!**\nط¥ظ„ظٹظƒ {len(collected_links_raw)} ط±ظˆط§ط¨ط· ط³ط­ط§ط¨ظٹط©.")
            safe_delete(txt_filename)
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="â‌Œ ظ„ظ… ط£ط¬ط¯ ظ†طھط§ط¦ط¬.")
    except Exception as e:
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"â‌Œ ط®ط·ط£: {e}")
        except: pass


# ================== 3. ط¯ط§ظ„ط© ط§ظ„ط³ط­ط¨ ط§ظ„ط³ط±ظٹط¹ (scrape) â€” TURBO ==================
async def run_scrape_action(bot, chat_id, message_id, args):
    global DIALOG_SEM
    try:
        edit_state = {"time": 0}
        target_count = int(args[0])
        await safe_edit(bot, chat_id, message_id, "âڑ، **ط¨ط¯ط£ ط§ظ„ط³ط­ط¨ ط§ظ„ظپط§ط¦ظ‚ ط§ظ„ط®ط§ظ… ظ„ظ„ظ…طµظ†ط¹...**", edit_state, stop_button(), force=True)

        app = Client("wassim_fast_scraper", api_id=24974564, api_hash="b87511de89b42178862e13e84147952b", session_string=SESSION_STRING)
        await app.start()

        all_links = []
        links_lock = asyncio.Lock()

        target_chats = []
        async for dialog in app.get_dialogs():
            chat = dialog.chat
            if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]:
                continue
            target_chats.append(chat.id)

        async def scrape_one(chat_id_pyro):
            async with DIALOG_SEM:
                if len(all_links) >= target_count * 2:
                    return
                urls = await extract_urls_from_chat(app, chat_id_pyro, limit=HISTORY_LIMIT)
                async with links_lock:
                    all_links.extend(urls)

        await asyncio.gather(*[scrape_one(cid) for cid in target_chats])

        await app.stop()
        final_links = list(set(all_links))[:target_count]
        if final_links:
            txt_filename = f"Scraped_{len(final_links)}.txt"
            with open(txt_filename, "w", encoding="utf-8") as f: f.write("\n".join(final_links))
            with open(txt_filename, "rb") as f_send:
                await bot.send_document(chat_id=chat_id, document=f_send, caption=f"âڑ، **ط§ظƒطھظ…ظ„ ط§ظ„ط³ط­ط¨ ط§ظ„ط³ط±ظٹط¹ ط¨ظ†ط¬ط§ط­!**\nطھظ… ط¬ظ„ط¨ {len(final_links)} ط±ظˆط§ط¨ط·.")
            safe_delete(txt_filename)
            await bot.delete_message(chat_id=chat_id, message_id=message_id)
        else:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="â‌Œ ظ„ظ… ظٹطھظ… ط§ظ„ط¹ط«ظˆط± ط¹ظ„ظ‰ ط±ظˆط§ط¨ط· ط¬ط¯ظٹط¯ط©.")
    except Exception as e:
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"â‌Œ ط®ط·ط£: {e}")
        except: pass


# ================== ط§ظ„ظ…ط­ط±ظƒ ط§ظ„ط³ط­ط§ط¨ظٹ ط§ظ„ط£ط³ط§ط³ظٹ ط§ظ„ظ…طھط­ظƒظ… ==================
async def main():
    global DIALOG_SEM, FETCH_SEM, UPLOAD_SEM
    if not SESSION_STRING: exit(1)

    # طھظ‡ظٹط¦ط© ط§ظ„ظ€ semaphores ط¶ظ…ظ† ط§ظ„ظ€ event loop
    DIALOG_SEM = asyncio.Semaphore(MAX_PARALLEL_DIALOGS)
    FETCH_SEM = asyncio.Semaphore(MAX_PARALLEL_FETCHES)
    UPLOAD_SEM = asyncio.Semaphore(MAX_PARALLEL_UPLOADS)

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
            await safe_edit(bot, chat_id, message_id, "âڑ™ï¸ڈ **ط§ظ„ظ…طµظ†ط¹ ظٹظ‚ظˆظ… ط¨طھظ†ط¸ظٹظپ ظˆطھظپط±ظٹط؛ ط§ظ„ظ…ظ„ظپ ط¨ط§ظ„ظپظˆط±ظ…ط§طھ ط§ظ„ط£طµظ„ظٹ ط§ظ„ط´ط±ط¹ظٹ...** âڈ³", {"time": 0}, stop_button(), force=True)
            tg_file = await bot.get_file(payload.get("file_id"))
            filepath = "temp_dl.m3u"
            await tg_file.download_to_drive(filepath)

            groups, total, adult = await analyze_async(filepath)
            os.remove(filepath)

            out_file = "clean_original.m3u"
            write_m3u_and_get_count(groups, out_file)
            final_file = compress_if_large(out_file)

            # ط±ظپط¹ ظ…طھظˆط§ط²ظچ ط¹ظ„ظ‰ GitHub ظˆ Catbox ظپظٹ ظ†ظپط³ ط§ظ„ظˆظ‚طھ ظ„ط±ظپط¹ ط§ظ„ط³ط±ط¹ط©
            git_link, catbox_link = await asyncio.gather(
                upload_to_cloud_sem(final_file, "github"),
                upload_to_cloud_sem(final_file, "catbox_m3u8"),
            )

            safe_delete(out_file)
            if final_file != out_file: safe_delete(final_file)

            msg = f"âœ… **ط§ظƒطھظ…ظ„ ط§ظ„طھظ†ط¸ظٹظپ ظˆط§ظ„ظپظˆط±ظ…ط§طھ ط§ظ„ط£طµظ„ظٹ!**\n\nًں“، ط¥ط¬ظ…ط§ظ„ظٹ ط§ظ„ظ‚ظ†ظˆط§طھ: {total:,}\nًں”‍ ظ…ط­ط°ظˆظپ ظˆظپظ„طھط±ط© ط¥ط¨ط§ط­ظٹ: {adult:,}\n\nًں”— **ط±ط§ط¨ط· ط§ظ„ظ…ط³طھظˆط¯ط¹ (GitHub):**\n`{git_link}`\n\nًں”— **ط±ط§ط¨ط· ط§ظ„ط¨ط« (Catbox):**\n`{catbox_link}`"
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=msg, parse_mode="Markdown")

    except Exception as e:
        try:
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"â‌Œ ط®ط·ط£ ط¯ط§ط®ظ„ظٹ ظپظٹ ط¹ظ…ظ„ ط§ظ„ظ…طµظ†ط¹: {str(e)}")
        except: pass

if __name__ == "__main__":
    asyncio.run(main())
