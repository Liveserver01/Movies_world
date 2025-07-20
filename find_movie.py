from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def search_movie(query):
    base_url = "https://vegamovies.frl"
    search_url = f"{base_url}/?s={query.replace(' ', '+')}"

    options = Options()
    options.add_argument("--headless")  # Headless mode: background में browser
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(search_url)

        time.sleep(5)  # wait for JS content to load

        titles = driver.find_elements(By.CLASS_NAME, "title")

        if not titles:
            driver.quit()
            return ["❗ कोई मूवी नहीं मिली, साइट का HTML नहीं लोड हुआ।"]

        movie_links = []
        for title in titles[:5]:
            try:
                a_tag = title.find_element(By.TAG_NAME, "a")
                text = a_tag.text
                link = a_tag.get_attribute("href")
                movie_links.append(f"[{text}]({link})")
            except:
                continue

        driver.quit()

        return movie_links if movie_links else ["❗ मूवी लिंक नहीं मिले।"]

    except Exception as e:
        return [f"❌ Error: {str(e)}"]
