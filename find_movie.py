import requests
from bs4 import BeautifulSoup

def search_movie(query):
    base_url = "https://vegamovies.frl"
    search_url = f"{base_url}/?s={query.replace(' ', '+')}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = soup.find_all("h2", class_="title")

        movie_links = []
        for item in results:
            title = item.get_text(strip=True)
            link = item.find("a")["href"]
            movie_links.append(f"{title}\n{link}")

        if not movie_links:
            return ["कोई भी रिजल्ट नहीं मिला।"]

        return movie_links[:5]  # Top 5 results
    except Exception as e:
        return [f"Error: {str(e)}"]
