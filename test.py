import requests
import time
from bs4 import BeautifulSoup
import httpx
from langchain_community.document_transformers import Html2TextTransformer

# using request to get content - need to clean up

def req_html(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }    # First attempt
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        # print(f"| Request Successfully extracted content from {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        # print(f"| Request failed to extract content from {url} - trying httx")
        return None

# using httpx to get content - need to clean up
def httpx_html(url):
    try:
        response = httpx.get(url, timeout=25)
        response.raise_for_status()
        print("--- Success! Got HTML using httpx ---")
        return response.text
        # process the HTML
    except Exception as e:
        print(f"--- httpx also failed ---")
        return None

# html2text - no need to clean