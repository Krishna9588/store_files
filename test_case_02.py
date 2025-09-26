import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import csv

# Example keywords dictionary
keywords_dict = {
    "SAP": ["SAP", "S/4HANA", "SAP Business One", "SAP HANA"],
    "VMware": ["VMware", "vSphere", "vCenter", "ESXi"],
    "Cloud": ["AWS", "Azure", "Google Cloud", "Oracle Cloud"]
}

# Crawl a domain and search keywords
def crawl_and_search(domain, keywords_dict, max_pages=30):
    visited = set()
    results = []
    to_visit = [f"https://{domain}"]

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
                continue

            soup = BeautifulSoup(resp.text, "html.parser")
            text = soup.get_text(" ", strip=True).lower()

            # Search keywords
            for category, keywords in keywords_dict.items():
                for kw in keywords:
                    if kw.lower() in text:
                        results.append((domain, kw, url))

            # Extract sub-links (same domain only)
            for a in soup.find_all("a", href=True):
                link = urljoin(url, a["href"])
                if urlparse(link).netloc == urlparse(url).netloc:
                    if link not in visited:
                        to_visit.append(link)

        except Exception as e:
            print(f"Error crawling {url}: {e}")

    return results


# ---- MAIN SCRIPT ----
all_results = []

# Read company list from CSV
with open("companies.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        domain = row["domain"].strip()
        print(f"Crawling {domain}...")
        matches = crawl_and_search(domain, keywords_dict)
        all_results.extend([(row["company"], kw, page) for (_, kw, page) in matches])

# Save results to CSV
with open("company_keywords_001.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Company", "Keyword", "Page_URL"])
    writer.writerows(all_results)

print("✅ Done! Results saved in company_keywords.csv")
