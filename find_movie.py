from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def search_movie(query):
    url = f"https://vegamovies.frl/?s={query.replace(' ', '+')}"

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/115.0")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    driver.get(url)

    time.sleep(5)  # wait for page to load

    movie_elements = driver.find_elements(By.CLASS_NAME, "title")
    results = []

    for element in movie_elements[:5]:
        try:
            a_tag = element.find_element(By.TAG_NAME, "a")
            title = a_tag.text.strip()
            link = a_tag.get_attribute("href")
            results.append(f"[{title}]({link})")
        except:
            continue

    driver.quit()

    if not results:
        return ["❗ कोई मूवी नहीं मिली, शायद साइट का लेआउट बदल गया है।"]

    return results

# Example call
print(search_movie("Superman"))
