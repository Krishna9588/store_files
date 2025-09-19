import re
import requests
from bs4 import BeautifulSoup
import time


def fetch_html(url: str) -> str:
    """
    Fetches HTML content from a URL with a timeout and a single retry attempt after a delay.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    try:
        # First attempt with a standard timeout
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        # If the first attempt fails, wait and try one more time with a longer timeout
        print(f"|   [!] Initial request failed for {url}: {e}. Retrying in 40 seconds...")
        time.sleep(40)
        print(f"|   [!] Retrying request for {url}...")
        response = requests.get(url, headers=headers, timeout=25) # Longer timeout for the retry
        response.raise_for_status()  # If this fails, the exception will be caught by the main loop
        return response.text

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
        # --- LIMIT ADDED HERE ---
        # If we have already found the maximum number of matches, stop searching.
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

    # --- BUG FIX ---
    # Now returns the list of matches directly, not as a tuple `(matches,)`.
    # This makes it work correctly with `if not contexts:` in your main script.
    return matches


def normal(url: str, keyword: str) -> list:
    """
    Main function to fetch, clean, and extract keyword contexts from a URL.
    Returns a list of context dictionaries.
    """
    # Let exceptions from fetch_html be caught by the main script
    html = fetch_html(url)
    text = clean_html(html)
    contexts = context_around_keyword(text, keyword)

    return contexts