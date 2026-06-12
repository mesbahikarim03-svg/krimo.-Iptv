import os
import json
import asyncio
import re
import requests
import base64
import time
import uuid
from collections import defaultdict
import aiohttp
from telegram import Bot
from pyrogram import Client, enums

# ================== الإعدادات والبيانات ==================
TOKEN = "7070246714:AAEW0yicB7oT5sVsnyBNbVIavRxt3iyH-kU"
GITHUB_TOKEN = os.environ.get("MY_GITHUB_TOKEN")
GITHUB_USER = "Mesbahikarim03-svg"
REPO_NAME = "krimo.-Iptv"  # المستودع الجديد نتاعك

API_ID = 24974564
API_HASH = "b87511de89b42178862e13e84147952b"
SESSION_STRING = "BAF9FOQAbltMnvF2hdrEFT2Qk9ZjqWrcvHmmTWPZclpftaZ2CtORF8imvvaJxCfU5jeCS0lCVqFPbEt50i2PUpObRAAiZNG8e6y0M5sA8jKK-wr26fz4fzjLkALcOxyZg9MB9jdKGCr5PbwgboEn8WeIItU0RltnsRSauKfDCmm7dgteqneUatn2QbpGHHw6_QldEPqRiRbKJXi_kMQQ4tDd004CDuuT0SF1XkCn5wHKd43v7iGBQWhJtu2R07NSqVjvaVQWKWMZjrSUDF7NeAdCCbxVkYDSrp9UzlMRhuuF9f1mEY4TsMSg-y7SB3kaKJiOeP2SaJpGPn0ffrAwwm8-MrQ1iAAAAABEOrkgAA"

CHANNEL_ID = "@free_iptv_world"
CHANNEL_NAME_FOR_FILE = "FREE_IPTV_WORLD"
MIN_CHANNELS_REQUIRED = 100

ADULT_WORDS = ["xxx", "porn", "adult", "adults", "sex", "18+", "+18", "erotic", "playboy", "amateur", "onlyfans", "brazzers", "vivid", "hustler", "penthouse", "babes", "realitykings", "naughty", "bangbros", "milf", "lesbian", "gay", "cam", "nsfw", "x-art", "babe", "pussy", "dick", "matures", "hardcore", "xnxx", "xvideos", "pornhub", "redtube", "kamasutra", "peep"]
ADULT_REGEX = re.compile(r'(?i)(?:' + '|'.join(map(re.escape, ADULT_WORDS)) + r')')
GROUP_TITLE_REGEX = re.compile(r'group-title="([^"]*)"')

WARNING_TEXT = "<blockquote>⚠️ <b>ATTENTION:</b> Links are valid for <b>10 DAYS</b> from publishing.</blockquote>\n\n"
LINK_POST_CAPTION = "🔗 𝗗𝗜𝗥𝗘𝗖𝗧 𝗜𝗣𝗧𝗩 𝗟𝗜𝗡𝗞𝗦 🔗\n🚀 High-Speed Links:\n{links}\n♻️ Please Share & Support Us!"

# ================== الدوال المساعدة ==================
def cleanup_old_github_files():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            for f in resp.json():
                name = f.get("name", "")
                if name.startswith("FIW_") and name.endswith(".m3u"):
                    if int(time.time()) - int(name.split("_")[1]) > 864000:
                        requests.delete(f.get("url"), json={"message": "Clean", "sha": f.get("sha")}, headers=headers)
    except: pass

async def upload_to_github(filename):
    cleanup_old_github_files()
    unique_id = str(uuid.uuid4().hex)[:6]
    safe_name = f"FIW_{int(time.time())}_{unique_id}.m3u"
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents/{safe_name}"
    with open(filename, "rb") as f:
        encoded = base64.b64encode(f.read()).decode('utf-8')
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    resp = requests.put(url, json={"message": "Upload", "content": encoded}, headers=headers)
    if resp.status_code in [200, 201]:
        return f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/main/{safe_name}"
    return None

def analyze_file(filepath):
    groups = defaultdict(list)
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
                    if bool(ADULT_REGEX.search(current_extinf)) or bool(ADULT_REGEX.search(url)) or bool(ADULT_REGEX.search(group)):
                        adult += 1
                    else:
                        groups[group].append((current_extinf, url))
                    current_extinf = ""
    clean_groups = {g: e for g, e in groups.items() if not bool(ADULT_REGEX.search(g))}
    return clean_groups, total, adult

def write_m3u(groups, filename):
    count = 0
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write("#EXTM3U\n")
        for g, entries in groups.items():
            for extinf, url in entries:
                f.write(extinf + "\n" + url + "\n")
                count += 1
    return count

async def fetch_and_analyze(url):
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=45)) as session:
            async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
                if resp.status in [200, 206]:
                    temp_path = f"temp_{uuid.uuid4().hex}.m3u"
                    with open(temp_path, 'wb') as f:
                        async for chunk in resp.content.iter_chunked(1024 * 1024): f.write(chunk)
                    groups, total, adult = analyze_file(temp_path)
                    os.remove(temp_path)
                    if total >= MIN_CHANNELS_REQUIRED: return groups
    except: pass
    return None

# ================== المعالجة الأساسية ==================
async def process_hunt(bot, chat_id, message_id, args):
    await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="🚀 المصنع (GitHub) بدأ الآن عملية الصيد... ⏳\nجاري الدخول للحساب...")
    
    target_count = int(args[-1]) if args[-1].isdigit() else int(args[0])
    keyword = " ".join(args[:-1]).lower() if len(args) > 1 and args[-1].isdigit() else (" ".join(args[1:]).lower() if len(args) > 1 else "")
    
    app = Client("wassim_fast_scraper", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
    await app.start()
    
    found_count = 0
    collected_links = []
    tested_urls = set()

    async for dialog in app.get_dialogs():
        if found_count >= target_count: break
        chat = dialog.chat
        if chat.type not in [enums.ChatType.CHANNEL, enums.ChatType.SUPERGROUP, enums.ChatType.GROUP]: continue
        
        async for msg in app.get_chat_history(chat.id, limit=60):
            if found_count >= target_count: break
            text = str(msg.text or msg.caption)
            urls = [u for u in re.findall(r'(https?://[^\s]+)', text) if 'm3u' in u.lower() or 'get.php' in u.lower()]
            
            for u in set(urls):
                if found_count >= target_count: break
                if u in tested_urls: continue
                tested_urls.add(u)
                
                try: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🔍 فحص سيرفر محتمل...\n✅ المجهز: {found_count}/{target_count}")
                except: pass

                groups = await fetch_and_analyze(u)
                if groups:
                    if keyword:
                        filtered = {g: e for g, e in groups.items() if keyword in g.lower()}
                        if not filtered: continue
                        groups = filtered

                    fname = f"hunter_{uuid.uuid4().hex[:4]}.m3u"
                    write_m3u(groups, fname)
                    git_link = await upload_to_github(fname)
                    if os.path.exists(fname): os.remove(fname)

                    if git_link:
                        collected_links.append(f"🔹 `{git_link}`")
                        found_count += 1
                        try: await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🎉 تم صيد سيرفر قوي! ✅ {found_count}/{target_count}")
                        except: pass
    await app.stop()

    if collected_links:
        links_text = "\n\n".join(collected_links)
        caption = WARNING_TEXT + LINK_POST_CAPTION.replace("{links}", links_text)
        await bot.send_message(chat_id=CHANNEL_ID, text=caption, parse_mode="HTML")
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"🏁 اكتمل الصيد الأسطوري!\nتم تجهيز ونشر {found_count} سيرفر في القناة بنجاح.")
    else:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="❌ انتهى البحث، لم أجد سيرفرات شغالة تلبي طلبك.")

async def main():
    bot = Bot(token=TOKEN)
    payload = json.loads(os.environ.get("PAYLOAD", "{}"))
    action = payload.get("action")
    chat_id = payload.get("chat_id")
    message_id = payload.get("message_id")
    
    if not chat_id or not action: return

    try:
        if action == "hunt":
            args = payload.get("args", [])
            await process_hunt(bot, chat_id, message_id, args)
            
        elif action == "process_file":
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="⚙️ المصنع (GitHub) يقوم بتنظيف الملف الآن... ⏳")
            tg_file = await bot.get_file(payload.get("file_id"))
            filepath = "temp_dl.m3u"
            await tg_file.download_to_drive(filepath)
            
            groups, total, adult = analyze_file(filepath)
            os.remove(filepath)
            
            out_file = "clean.m3u"
            write_m3u(groups, out_file)
            git_link = await upload_to_github(out_file)
            os.remove(out_file)
            
            msg = f"✅ اكتمل التنظيف!\n📡 القنوات: {total:,}\n🔞 المحذوف: {adult:,}\n\n🔗 الرابط המباشر:\n`{git_link}`"
            await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=msg, parse_mode="Markdown")
            
    except Exception as e:
        await bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=f"❌ خطأ في المصنع: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
