# vegamovies_bot.py
import os
import json
import requests
import re
from base64 import b64encode
from telethon import TelegramClient, events

# ========== Config ==========
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")
GITHUB_FILE_PATH = os.environ.get("GITHUB_FILE_PATH", "movie_list.json")
GITHUB_BRANCH = os.environ.get("GITHUB_BRANCH", "main")

# ========== Start Client ==========
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# ========== Helper Functions ==========
def search_vegamovies(query):
    url = f"https://vegamovies.frl/?s={query.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    matches = re.findall(r'<a href="(https://vegamovies[^"]+)" rel="bookmark">\s*(.*?)\s*</a>', res.text)
    return matches[:5]  # top 5 matches

def save_to_github(data):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    # Check existing SHA
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

def load_local_movies():
    path = "movie_list.json"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_local_movies(data):
    with open("movie_list.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ========== Bot Handlers ==========
@bot.on(events.NewMessage(pattern="/find (.+)"))
async def handler(event):
    query = event.pattern_match.group(1)
    user_id = event.sender_id

    results = search_vegamovies(query)
    if not results:
        await event.reply("😞 Sorry, no movie found on Vegamovies.")
        return

    msg_lines = ["🎬 *Search Results:*\n"]
    local_data = load_local_movies()

    for i, (link, title) in enumerate(results, start=1):
        msg_lines.append(f"{i}. [{title}]({link})")
        local_data.append({"title": title.strip(), "msg_id": user_id, "url": link})

    save_local_movies(local_data)
    save_to_github(local_data)

    await event.reply("\n".join(msg_lines), link_preview=False, parse_mode='md')

@bot.on(events.NewMessage(pattern="/help"))
async def help_handler(event):
    help_text = """
🤖 *Vegamovies Bot Help*

Use `/find <movie name>` to search movies on vegamovies.frl
Example: `/find Animal` or `/find War`
    """
    await event.reply(help_text, parse_mode='md')

# ========== Start ==========
print("✅ Bot is running...")
bot.run_until_disconnected()
