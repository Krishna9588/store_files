import httpx
import html2text
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import re
try:
    from langchain_community.document_transformers import Html2TextTransformer
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
from datetime import datetime
from dateutil.parser import parse

""" Possible outcomes of this file
1. 5 distinct, clean chunks of text
2. date of the article
3. social media links
"""

# Html
def html_extract(url):
    raw_text = ""

    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        raw_text = response.text
        print("Extracted HTML using direct httpx request")
    except Exception as e:
        print(f"Direct extraction failed: {e}")

        if LANGCHAIN_AVAILABLE:
            try:
                from langchain_community.document_loaders import AsyncHtmlLoader
                loader = AsyncHtmlLoader([url])
                docs = loader.load()
                transformer = Html2TextTransformer()
                docs_transformed = transformer.transform_documents(docs)
                raw_text = docs_transformed[0].page_content
                print("Extracted HTML using Html2TextTransformer")
            except Exception as e:
                print(f"Html2TextTransformer extraction failed: {e}")

                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                    response = httpx.get(url, headers=headers, follow_redirects=True, timeout=30)
                    response.raise_for_status()
                    raw_text = response.text
                    print("Extracted HTML using advanced httpx request")
                except Exception as e:
                    print(f"All extraction methods failed: {e}")
                    raw_text = ""
        else:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = httpx.get(url, headers=headers, follow_redirects=True, timeout=30)
                response.raise_for_status()
                raw_text = response.text
                print("Extracted HTML using advanced httpx request")
            except Exception as e:
                print(f"All extraction methods failed: {e}")
                raw_text = ""

    return raw_text

# Html Clean
def html_clean(raw_html):

    if not raw_html:
        return "Input HTML is empty."

    # Method 1: Using BeautifulSoup to clean HTML
    try:
        soup = BeautifulSoup(raw_html, 'html.parser')

        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()

        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        print("Cleaned HTML using BeautifulSoup")
        return text
    except Exception as e:
        print(f"BeautifulSoup cleaning failed: {e}")

        try:
            md_text = md(raw_html)
            print("Cleaned HTML using markdownify")
            return md_text
        except Exception as e:
            print(f"Markdownify cleaning failed: {e}")

            try:
                h = html2text.HTML2Text()
                h.ignore_links = True
                h.ignore_images = True
                h.ignore_emphasis = True
                text = h.handle(raw_html)
                print("Cleaned HTML using html2text")
                return text
            except Exception as e:
                print(f"All cleaning methods failed: {e}")
                return raw_html

# Context
def extract_content(clean_cont, keyword, limit=5, before=250, after=250):
    chunks = []
    searchable_text = clean_cont

    for i in range(limit):
        match = re.search(keyword, searchable_text, re.IGNORECASE)

        if not match:
            print(f"No more occurrences of '{keyword}' found. Found {len(chunks)} chunk(s).")
            break

        keyword_start, keyword_end = match.span()

        chunk_start = max(0, keyword_start - before)
        chunk_end = min(len(searchable_text), keyword_end + after)

        extracted_chunk = searchable_text[chunk_start:chunk_end]
        chunks.append(extracted_chunk.strip())

        searchable_text = searchable_text[:chunk_start] + searchable_text[chunk_end:]

    return chunks

# Date
def find_date(raw_html: str) -> str | None:
  
    def _parse_and_format_date(date_str: str) -> str | None:
        """Tries to parse a date string and returns it in MM/YYYY format."""
        if not date_str:
            return None
        try:
            dt_object = parse(date_str, fuzzy=True)
            return dt_object.strftime("%m/%Y")
        except (ValueError, TypeError, OverflowError):
            return None

    if not raw_html:
        return None

    soup = BeautifulSoup(raw_html, 'html.parser')

    main_content_selectors = ['article', 'main', '.post-body', '.entry-content', '.td-post-content']
    main_content = None
    for selector in main_content_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break

    if main_content:
        body_date_pattern = r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s\d{1,2},?\s\d{4}|\b\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s\d{4}'
        match = re.search(body_date_pattern, main_content.get_text(), re.IGNORECASE)
        if match:
            date = _parse_and_format_date(match.group(0))
            if date: return date


    patterns_metadata = [
        # 2. Common meta tags
        r'<meta[^>]+(?:property|name)="(?:article:published_time|published_date|date)"[^>]+content="([^"]+)"',
        r'<meta[^>]+(?:property|name)="(?:article:modified_time|modified_date)"[^>]+content="([^"]+)"',
        # 3. JSON-LD structured data
        r'"datePublished"\s*:\s*"([^"]+)"',
        r'"dateModified"\s*:\s*"([^"]+)"',
        # 4. The <time> HTML tag
        r'<time[^>]*datetime="([^"]+)"',
        # 5. Visible text with keywords (searching the raw HTML)
        r'(?:published|released|modified|updated|posted)[\s:onby-]*([\w\s,./-]+\d{4})'
    ]

    for pattern in patterns_metadata:
        match = re.search(pattern, raw_html, re.IGNORECASE)
        if match:
            date = _parse_and_format_date(match.group(1))
            if date: return date

    # 6: Any date visible on the page (keyword-less) ---
    visible_text = soup.get_text(separator=' ')
    any_date_pattern = r'\b(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s\d{1,2},?\s\d{4}|\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s\d{4}|\d{1,2}[./-]\d{1,2}[./-]\d{4})\b'
    match = re.search(any_date_pattern, visible_text, re.IGNORECASE)
    if match:
        date = _parse_and_format_date(match.group(0))
        if date: return date

    # 7: Copyright year as a last resort ---
    cc_match = re.search(r'(?:©|cc|copyright|(c)|&copy;)\s*(\d{4})', raw_html, re.IGNORECASE)
    if cc_match:
        try:
            year = int(cc_match.group(1))

            now = datetime.now()
            current_year = now.year
            current_month = now.month

            if year < current_year:
                return f"12/{year}"
            elif year == current_year:
                return f"{current_month:02d}/{year}"
        except (ValueError, TypeError):
            pass

    return None

# Social Media
def social_links(raw_html: str) -> dict:
    """
    Parses raw HTML to find and extract social media PROFILE links,
    prioritizing links found in the footer.

    Args:
        raw_html: A string containing the raw HTML content of a webpage.

    Returns:
        A dictionary where keys are the names of the social media platforms
        and values are their corresponding direct profile URLs.
    """
    social_links = {}
    soup = BeautifulSoup(raw_html, 'html.parser')

    # Keywords that indicate a "sharing" link, which we want to ignore.
    ignore_patterns = ['sharer.php', 'shareArticle', '/share?', 'intent/tweet']

    # A mapping of domain keywords to the desired output key.
    platform_map = {
        'linkedin.com': 'linkedin',
        'facebook.com': 'facebook',
        'x.com': 'twitter (x.com)',
        'twitter.com': 'twitter (x.com)',
        'youtube.com': 'youtube',
        'glassdoor.com': 'glassdoor',
        'instagram.com': 'instagram'
    }

    # Find all anchor tags in the document
    all_links = soup.find_all('a')

    # --- KEY CHANGE: Iterate through the links in REVERSE order ---
    # This starts the search from the bottom of the page (the footer).
    for link in reversed(all_links):
        url = link.get('href')
        if not url:
            continue

        # --- NEW: Skip URLs that are identified as sharing links ---
        if any(pattern in url for pattern in ignore_patterns):
            continue

        # Check the URL against our known platforms
        for domain, platform_name in platform_map.items():
            if domain in url:
                # --- KEY CHANGE: Only add the link if we haven't found it yet ---
                # Since we are searching from the bottom up, the first one we find
                # for each platform is the correct one from the footer.
                if platform_name not in social_links:
                    social_links[platform_name] = url

    # The dictionary may have been populated in reverse order, so we can
    # optionally return it in a consistent order if needed, though it's not required.
    return social_links

# primary function
def html(url,keyword):
    raw_text = html_extract(url)
    clean_content = html_clean(raw_text)
    context = extract_content(clean_content, keyword)
    date = find_date(raw_text)
    return context,date


# ---------- Test Code -----------------
# url1 = "https://www.birlasoft.com/services/enterprise-products/aws"

# raw_text = html_extract(url1)
# print()



# a = social_links(raw_text)
# for c,d in a.items():
#     print(f"{c}: {d}")