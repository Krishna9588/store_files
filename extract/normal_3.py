import re
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def create_driver() -> webdriver.Chrome:
    """Creates and returns a new Chrome WebDriver instance."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver


def fetch_html(url: str) -> str:
    """
    Fetches HTML content from a URL using a pre-initialized headless browser.
    Includes a simplified retry mechanism.
    """
    try:
        # First attempt
        driver = create_driver()
        driver.set_page_load_timeout(20)
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(2)
        return driver.page_source
    except Exception as e:
        print(f"|   [!] Initial request failed for {url}. Retrying...")
        time.sleep(5)
        # Second attempt
        driver.set_page_load_timeout(30) # Longer timeout for retry
        driver.get(url)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        time.sleep(3)
        return driver.page_source


# --------------

def clean_html(html: str) -> str:
    """Removes unwanted tags and extra whitespace from HTML."""
    soup = BeautifulSoup(html, "lxml")
    # Added <header> to the list of common non-content tags to remove
    for tag in soup(["script", "style", "nav", "footer", "aside", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    return re.sub(r"\s+", " ", text).strip()


def context_around_keyword(text: str, keyword: str, context_words: int = 250, max_matches: int = 5) -> list:
    """
    Finds up to `max_matches` occurrences of a keyword and returns the surrounding context.
    """
    words = re.findall(r'\b\w+\b', text)
    pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)

    matches = []
    for match in pattern.finditer(text):
        if len(matches) >= max_matches:
            break

        idx = match.start()
        word_idx = len(re.findall(r'\b\w+\b', text[:idx]))
        start = max(0, word_idx - context_words)
        end = min(len(words), word_idx + context_words)
        context = " ".join(words[start:end])
        matches.append({
            "keyword": keyword,
            "context": context
        })

    return matches


def normal(url: str, keyword: str) -> list:
    """
    Main function to fetch, clean, and extract keyword contexts from a URL using a provided driver.
    """
    html = fetch_html(url)
    if not html:
        return []
    text = clean_html(html)
    contexts = context_around_keyword(text, keyword)

    return contexts


# company_name = "Birlasoft"
# keyword = "AWS"
# url = "https://www.birlasoft.com/services/enterprise-products/aws"
# print(normal(url, keyword))