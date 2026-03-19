import os
import requests
import schedule
import time
from datetime import datetime

# ===== YOUR CONFIG =====
TELEGRAM_TOKEN = "8631314434:AAG93N1EJmE0IlO1xS27wsEiJQm39B_zLh8"   # from @BotFather
CHANNEL_ID = "@mauryacircle96"                  # ✅ already set!
NEWS_API_KEY = "c89afbecbb214ec89cd95fa1a9fa4518"    # from newsapi.org
# =======================

CATEGORIES = ["general", "technology", "business", "sports"]
POSTED_URLS = set()

def fetch_news():
    articles = []
    for category in CATEGORIES:
        url = (
            f"https://newsapi.org/v2/top-headlines"
            f"?category={category}&language=en&pageSize=2&apiKey={NEWS_API_KEY}"
        )
        res = requests.get(url).json()
        if res.get("articles"):
            articles.extend(res["articles"])
    return articles

def translate_to_hindi(text):
    try:
        url = f"https://api.mymemory.translated.net/get?q={requests.utils.quote(text)}&langpair=en|hi"
        res = requests.get(url, timeout=5).json()
        return res["responseData"]["translatedText"]
    except:
        return ""

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    requests.post(url, json=payload)

def post_news():
    articles = fetch_news()
    count = 0
    for article in articles:
        if article["url"] in POSTED_URLS:
            continue
        if not article.get("title") or not article.get("url"):
            continue

        title_en = article["title"]
        desc_en = article.get("description") or ""
        source = article.get("source", {}).get("name", "Unknown")
        link = article["url"]

        title_hi = translate_to_hindi(title_en)
        desc_hi = translate_to_hindi(desc_en) if desc_en else ""

        message = (
            f"🌍 <b>{title_en}</b>\n"
            f"{'📝 ' + desc_en if desc_en else ''}\n\n"
            f"🇮🇳 <i>{title_hi}</i>\n"
            f"{'   ' + desc_hi if desc_hi else ''}\n\n"
            f"📰 Source: {source}\n"
            f"🔗 {link}"
        )

        send_to_telegram(message)
        POSTED_URLS.add(article["url"])
        count += 1
        time.sleep(3)

    print(f"[{datetime.now()}] Posted {count} articles.")

# Run every hour
schedule.every(1).hours.do(post_news)

print("✅ Bot started! Posting to @mauryacircle96 every hour...")
post_news()  # post immediately on start

while True:
    schedule.run_pending()
    time.sleep(30)