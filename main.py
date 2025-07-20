import os
import requests
from bs4 import BeautifulSoup
from telethon import TelegramClient, events

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHANNEL = os.environ.get("CHANNEL")

def search_movie(query):
    url = f"https://vegamovies.frl/?s={query.replace(' ', '+')}"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.text, 'html.parser')
    post = soup.find("h2", class_="entry-title")
    if not post:
        return None

    title = post.text.strip()
    link = post.find("a")["href"]
    return f"🎬 **{title}**\n🔗 {link}"

client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@client.on(events.NewMessage(pattern="/find (.+)"))
async def handler(event):
    query = event.pattern_match.group(1)
    await event.respond("🔍 Searching...")
    result = search_movie(query)

    if result:
        await client.send_message(CHANNEL, result)
        await event.respond("✅ Sent to channel.")
    else:
        await event.respond("❌ Not found.")

print("🤖 Bot is running...")
client.run_until_disconnected()
