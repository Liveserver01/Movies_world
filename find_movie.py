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

    try:
        with requests.Session() as session:
            response = session.get(search_url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            results = soup.find_all("h2", class_="title")

            if not results:
                return ["❗ कोई मूवी नहीं मिली, शायद साइट का लेआउट बदल गया है।"]

            movie_links = []
            for item in results:
                a_tag = item.find("a")
                if a_tag and a_tag.get("href"):
                    title = a_tag.get_text(strip=True)
                    link = a_tag["href"]
                    movie_links.append(f"[{title}]({link})")

            if not movie_links:
                return ["❗ मूवी लिंक नहीं मिल पाए।"]

            return movie_links[:5]

    except requests.exceptions.Timeout:
        return ["⏳ टाइमआउट हो गया। इंटरनेट या साइट स्लो हो सकती है।"]
    except requests.exceptions.RequestException as e:
        return [f"❌ रिक्वेस्ट एरर: {str(e)}"]
    except Exception as e:
        return [f"❌ Unknown Error: {str(e)}"]
