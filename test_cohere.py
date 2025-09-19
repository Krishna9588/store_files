import requests
import fitz  # PyMuPDF
from io import BytesIO

def extract_context_from_online_pdf(pdf_url, keyword, context_chars=700):
    # fetch pdf file
    response = requests.get(pdf_url)
    response.raise_for_status()

    # open in memory
    doc = fitz.open(stream=BytesIO(response.content), filetype="pdf")
    results = []

    for page_num, page in enumerate(doc, start=1):
        text = page.get_text("text")
        lower_text = text.lower()
        lower_keyword = keyword.lower()

        idx = lower_text.find(lower_keyword)
        while idx != -1:
            start = max(0, idx - context_chars)
            end = min(len(text), idx + len(keyword) + context_chars) 
            snippet = text[start:end].replace("\n", " ").strip()

            results.append({
                "page": page_num,
                "snippet": snippet
            })

            idx = lower_text.find(lower_keyword, idx + 1)

    # If too many results, downsample to exactly 6 evenly spaced
    if len(results) > 10:
        step = len(results) // 6
        sampled = [results[i] for i in range(0, len(results), step)][:6]
        return sampled

    return results



# Example
pdf_url = "https://www.nab.com.au/content/dam/nab/documents/guides/services/nab-india-supplier-onboarding-guide-step-1.pdf"   # Attention is All You Need
keyword = "sap"

# matches = extract_context_from_online_pdf(pdf_url, keyword)
# # print(matches[0:5])
# index = 1
# for match in matches[:20]:  # preview top 3 matches
#     print(f"Page {index}. {match['page']} -> {match['snippet']}\n")
#     index += 1

def get_pdf_date(pdf_url):
    import requests, fitz
    from io import BytesIO

    response = requests.get(pdf_url)
    response.raise_for_status()

    doc = fitz.open(stream=BytesIO(response.content), filetype="pdf")
    meta = doc.metadata

    # Try creationDate or modDate
    date = meta.get("creationDate") or meta.get("modDate")

    if date:
        # PDF dates look like: "D:20170612130500Z"
        # Let's clean it up
        date = date.replace("D:", "")
        year, month, day = date[0:4], date[4:6], date[6:8]
        return f"{year}-{month}-{day}"
    return None
import re

print("Get_PDF_Date",get_pdf_date(pdf_url))

def extract_date_from_text(doc):
    first_page_text = doc[0].get_text("text")
    # Match patterns like "June 2017" or "2017-06-12"
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",       # 2017-06-12
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b"
    ]
    for pat in patterns:
        match = re.search(pat, first_page_text, re.IGNORECASE)
        if match:
            return match.group(0)
    return None


# print("extract_date_from_text",extract_date_from_text(pdf_url))




