import requests
from bs4 import BeautifulSoup

def search_movie(query):
    base_url = "https://vegamovies.frl"
    search_url = f"{base_url}/?s={query.replace(' ', '+')}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    session = requests.Session()
    try:
        response = session.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("h2", class_="title")

        movie_links = []
        for item in results:
            a_tag = item.find("a")
            if a_tag:
                title = a_tag.get_text(strip=True)
                link = a_tag["href"]
                movie_links.append(f"[{title}]({link})")

        if not movie_links:
            return ["❗ कोई रिज़ल्ट नहीं मिला।"]

        return movie_links[:5]
    except Exception as e:
        return [f"❌ Error: {str(e)}"]
