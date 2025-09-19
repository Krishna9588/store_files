# C:/Users/propl/PycharmProjects/rook_dont/extract/normal_new.py

import re
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# --- Define a constant path for the single log file ---
LOG_FILE_PATH = "normal_results/context_extraction_log.json"


def _save_result_to_json(url: str, keyword: str, contexts: list):
    """Appends the extracted contexts to a single, consolidated JSON log file."""
    output_dir = os.path.dirname(LOG_FILE_PATH)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    new_entry = {
        "url": url,
        "keyword": keyword,
        "retrieval_timestamp_utc": datetime.utcnow().isoformat(),
        "results": contexts
    }

    all_data = []
    try:
        if os.path.exists(LOG_FILE_PATH):
            with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                all_data = json.load(f)
                if not isinstance(all_data, list):
                    all_data = []
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    all_data.append(new_entry)

    try:
        with open(LOG_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"  [WARNING] Could not save result to JSON log file: {e}")


def fetch_html(url: str) -> str:
    """Fetches HTML content from a URL with a timeout and error handling."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    }
    # Added verify=False to handle sites with SSL certificate issues, a common problem.
    response = requests.get(url, headers=headers, timeout=20, verify=False)
    response.raise_for_status()
    return response.text


def extract_semantic_contexts(html: str, keyword: str, max_matches: int = 6) -> list:
    """
    UPGRADED LOGIC: An intelligent context extractor that finds all keyword matches
    within distinct blocks and then selects a diverse, spaced-out sample.
    """
    soup = BeautifulSoup(html, "lxml")

    # 1. Aggressive cleaning of irrelevant sections
    for selector in [
        "nav", "footer", "aside", "header", "script", "style",
        "[role='navigation']", "[role='banner']", "[role='contentinfo']",
        "#sidebar", ".sidebar", "#footer", ".footer", "#header", ".header"
    ]:
        for tag in soup.select(selector):
            tag.decompose()

    # The \b ensures we only match whole words, preventing partial matches.
    keyword_pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)

    # --- Step 1: Find all potential contexts first ---
    all_potential_contexts = []
    seen_contexts_text = set()

    # --- Fallback Search Logic (Request 1) ---
    # Prioritize major semantic tags, but fall back to the whole body if they don't exist.
    content_area = soup.select_one("main, article")
    if not content_area:
        print("  [INFO] No <main> or <article> tag found. Falling back to full <body> search.")
        content_area = soup.body

    if not content_area:
        return []  # Should be rare, but a good safeguard

    # Iterate through all relevant blocks to find every possible match
    for block in content_area.find_all(['p', 'div', 'li', 'section'], recursive=True):
        # Ignore small, likely irrelevant blocks
        if not block.get_text(strip=True) or len(block.get_text(strip=True)) < 50:
            continue

        block_text = block.get_text(separator=' ', strip=True)
        if keyword_pattern.search(block_text):
            cleaned_context = re.sub(r'\s+', ' ', block_text).strip()
            # De-duplicate to ensure we only have unique context snippets
            if cleaned_context not in seen_contexts_text:
                all_potential_contexts.append({"keyword": keyword, "context": cleaned_context})
                seen_contexts_text.add(cleaned_context)

    # --- Step 2: Apply Diverse Selection Logic (Request 3) ---
    num_found = len(all_potential_contexts)

    if num_found == 0:
        return []

    # If we found 6 or fewer, just return all of them
    if num_found <= max_matches:
        return all_potential_contexts
    else:
        # If we found more than 6, select a diverse, spaced-out sample
        print(f"  [INFO] Found {num_found} contexts. Selecting a diverse sample of {max_matches}.")
        selected_contexts = []
        # This formula ensures the first and last items are always included
        for i in range(max_matches):
            index = int(round(i * (num_found - 1) / (max_matches - 1)))
            # Ensure we don't add the same context if rounding causes duplicates
            if all_potential_contexts[index] not in selected_contexts:
                selected_contexts.append(all_potential_contexts[index])
        return selected_contexts


def normal(url: str, keyword: str) -> list:
    """
    Main function to fetch, clean, and extract keyword contexts from a URL.
    Now uses the much-improved semantic extraction logic.
    """
    html = fetch_html(url)
    contexts = extract_semantic_contexts(html, keyword)

    _save_result_to_json(url, keyword, contexts)

    return contexts
