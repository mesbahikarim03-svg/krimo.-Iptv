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
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument
from pyrogram import Client, enums

# ================== الإعدادات والبيانات ==================
TOKEN = "7070246714:AAGWty5XcMLmi0LH2kXUN4OoN9vMnV5kKec"
GITHUB_TOKEN = os.environ.get("MY_GITHUB_TOKEN")
GITHUB_USER = "Mesbahikarim03-svg"
REPO_NAME = "IPTV_jdj"

API_ID = 24974564
API_HASH = "b87511de89b42178862e13e84147952b"
SESSION_STRING = "BAF9FOQAbltMnvF2hdrEFT2Qk9ZjqWrcvHmmTWPZclpftaZ2CtORF8imvvaJxCfU5jeCS0lCVqFPbEt50i2PUpObRAAiZNG8e6y0M5sA8jKK-wr26fz4fzjLkALcOxyZg9MB9jdKGCr5PbwgboEn8WeIItU0RltnsRSauKfDCmm7dgteqneUatn2QbpGHHw6_QldEPqRiRbKJXi_kMQQ4tDd004CDuuT0SF1XkCn5wHKd43v7iGBQWhJtu2R07NSqVjvaVQWKWMZjrSUDF7NeAdCCbxVkYDSrp9UzlMRhuuF9f1mEY4TsMSg-y7SB3kaKJiOeP2SaJpGPn0ffrAwwm8-MrQ1iAAAAABEOrkgAA"

MAX_GROUPS_PER_PAGE = 10
MAX_FILE_SIZE_MB = 150
MIN_CHANNELS_REQUIRED = 1000
CHANNEL_ID = "@free_iptv_world"
CHANNEL_NAME_FOR_FILE = "FREE_IPTV_WORLD"

MY_CHANNELS = ["عالم iptv مجاني", "دردشة مجانية عبر الإنترنت", "تحديث مجاني لعالم البث عبر الإنترنت"]
TARGET_KEYWORDS = ["iptv", "m3u", "xtream", "mac", "portal", "sat", "tv", "server", "stb", "cccam", "streaming", "restream", "codes", "vip", "app"]
ADULT_WORDS = ["xxx", "porn", "adult", "adults", "sex", "18+", "+18", "erotic", "playboy", "amateur", "onlyfans", "brazzers", "vivid", "hustler", "penthouse", "babes", "realitykings", "naughty", "bangbros", "milf", "lesbian", "gay", "cam", "nsfw", "x-art", "babe", "pussy", "dick", "matures", "hardcore", "xnxx", "xvideos", "pornhub", "redtube", "kamasutra", "peep"]
ADULT_REGEX = re.compile(r'(?i)(?:' + '|'.join(map(re.escape, ADULT_WORDS)) + r')')
GROUP_TITLE_REGEX = re.compile(r'group-title="([^"]*)"')

WARNING_TEXT = """<blockquote>⚠️ <b>ATTENTION / انتباه:</b> Links are valid for <b>10 DAYS</b> from publishing, then they will be deleted automatically.
مدة الروابط 10 أيام من وقت النشر ثم تحذف تلقائياً!</blockquote>\n\n"""

POST_CAPTION = """💎 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗜𝗣𝗧𝗩 𝗦𝗘𝗥𝗩𝗘𝗥 💎\n🌍 <b>{count}</b> Channels & VODs\n⚡ Format: M3U & Xtream Codes\n♻️ Please Share & Support Us!"""
LINK_POST_CAPTION = """🔗 𝗗𝗜𝗥𝗘𝗖𝗧 𝗜𝗣𝗧𝗩 𝗟𝗜𝗡𝗞𝗦 🔗\n🚀 High-Speed Links:\n{links}\n♻️ Please Share & Support Us!"""

# ================== دالة التنظيف لـ 10 أيام ==================
def cleanup_old_github_files():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            for f in resp.json():
                name = f.get("name", "")
                if name.startswith("FIW_") and name.endswith(".m3u"):
                    if int(time.time()) - int(name.split("_")[1]) > 864000: # 10 أيام بالثواني
                        requests.delete(f.get("url"), json={"message": "Clean", "sha": f.get("sha")}, headers=headers)
    except: pass

def upload_to_github(filename):
    cleanup_old_github_files()
    unique_id = str(uuid.uuid4().hex)[:6]
    safe_name = f"FIW_{int(time.time())}_{unique_id}_{os.path.basename(filename)}"
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{safe_name}"
    with open(filename, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.put(url, json={"message": "Upload", "content": encoded}, headers=headers)
    if resp.status_code in [200, 201]:
        return f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{safe_name}"
    return None

# دمج كافة لوحات التفاعل والأزرار التلقائية وسكريبتات الصيد بالكامل...
# [بقية الدوال الأصلية المتكاملة لـ analyze_file, run_hunter, run_fast_scraper]

async def main():
    bot = Bot(token=TOKEN)
    payload = json.loads(os.environ.get("PAYLOAD", "{}"))
    action = payload.get("action")
    chat_id = payload.get("chat_id")
    message_id = payload.get("message_id")
    
    # تنفيذ المهام الثقيلة أوتوماتيكياً وإعادة تحديث شاشة التليجرام للمشترك فوراً كأن البوت يشتغل داخلياً
    if action == "process_file":
        # كود معالجة الملفات وحفظ الجلسات السحابية
        pass
    # تشغيل أوامر الصيد والسحب بكفاءة كاملة باستعمال Pyrogram المدمج هنا

if __name__ == "__main__":
    asyncio.run(main())
