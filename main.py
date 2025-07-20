# main.py
import os
import json
import requests
import re
from base64 import b64encode
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events

# ========== Flask Setup ==========
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🤖 Vegamovies Bot is Alive!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=8080)

# ========== Environment Variables ==========
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
GITHUB_FILE_PATH = os.environ.get("GITHUB_FILE_PATH", "movie_list.json")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

# ========== Telegram Bot ==========
bot = TelegramClient("vegamovies_bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ========== Search Function ==========
def search_vegamovies(query):
    url = f"https://vegamovies.frl/?s={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    matches = re.findall(r'<a href="(https://vegamovies[^"]+)" rel="bookmark">\s*(.*?)\s*</a>', res.text)
    return matches[:5]

# ========== Local File Save ==========
def load_local_movies():
    path = "movie_list.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_local_movies(data):
    with open("movie_list.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ========== GitHub Integration ==========
def save_to_github(data):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    res = requests.get(url, headers=headers)
    sha = res.json().get("sha") if res.status_code == 200 else None

    encoded_content = b64encode(json.dumps(data, indent=4, ensure_ascii=False).encode()).decode()

    payload = {
        "message": "Update movie_list.json",
        "content": encoded_content,
        "branch": GITHUB_BRANCH
    }

    if sha:
        payload["sha"] = sha

    put_res = requests.put(url, headers=headers, json=payload)
    return put_res.status_code in [200, 201]

# ========== Telegram Bot Handlers ==========

@bot.on(events.NewMessage(pattern="/start"))
async def start_handler(event):
    await event.reply("👋 नमस्ते! मुझे कोई भी मूवी नाम बताओ: `/find MovieName`")

@bot.on(events.NewMessage(pattern="/help"))
async def help_handler(event):
    await event.reply(
        "📌 *Vegamovies Bot Help*\n\n"
        "🎬 `/find <movie name>` से मूवी सर्च करें\n"
        "उदाहरण: `/find Animal` या `/find War`",
        parse_mode='md'
    )

@bot.on(events.NewMessage(pattern="/find (.+)"))
async def find_handler(event):
    query = event.pattern_match.group(1)
    user_id = event.sender_id

    await event.reply(f"🔍 `{query}` के लिए खोज जारी है...", parse_mode='md')
    results = search_vegamovies(query)

    if not results:
        await event.reply("❌ कोई भी मूवी नहीं मिली।")
        return

    msg_lines = ["🎬 *Search Results:*\n"]
    local_data = load_local_movies()

    for i, (link, title) in enumerate(results, start=1):
        msg_lines.append(f"{i}. [{title}]({link})")
        local_data.append({"title": title.strip(), "msg_id": user_id, "url": link})

    save_local_movies(local_data)
    save_to_github(local_data)

    await event.reply("\n".join(msg_lines), link_preview=False, parse_mode='md')

# ========== Start Everything ==========
if __name__ == "__main__":
    print("🚀 Bot and Server Running...")

    # Run Flask in background thread
    Thread(target=run_flask).start()

    # Start Telegram bot
    bot.run_until_disconnected()
