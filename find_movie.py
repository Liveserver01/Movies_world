from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def search_movie(query):
    options = Options()
    options.add_argument("--headless")  # ब्राउज़र दिखेगा नहीं
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    base_url = "https://vegamovies.frl"
    search_url = f"{base_url}/?s={query.replace(' ', '+')}"
    driver.get(search_url)
    time.sleep(3)  # पेज लोड होने दो

    results = []
    items = driver.find_elements(By.CSS_SELECTOR, "h2.title a")
    for item in items[:5]:
        title = item.text.strip()
        link = item.get_attribute("href")
        results.append(f"[{title}]({link})")

    driver.quit()

    if not results:
        return ["❗ कोई मूवी नहीं मिली, शायद साइट बदल गई है।"]
    return results
