from transformers import pipeline
from prime_normal import *
import time
import torch

# Note: The first time you run this, it will download the model (approx. 500MB).
print("--- Loading Hugging Face QA Pipeline ---")
start_time = time.time()

# Check if a CUDA-enabled GPU is available
device = 0 if torch.cuda.is_available() else -1
if device == 0:
    print("GPU found! Running on GPU.")
else:
    print("No GPU found, running on CPU.")

# Pass device=0 to use the first GPU, or device=-1 for CPU
# qa_pipeline = pipeline(
#     "question-answering",
#     model="deepset/roberta-base-squad2",
#     device=device
# )
# qa_pipeline = pipeline(
#     "question-answering",
#     model="google/mobilebert-uncased-squad2",
#     device=device
# )
# qa_pipeline = pipeline("question-answering", model="timpal0l/mdeberta-v3-base-squad2",device=device)
qa_pipeline = pipeline("question-answering", model="distilbert/distilbert-base-cased-distilled-squad",device=device)

print("--- Pipeline Loaded ---")

# --- 1. Define the Context and Question ---
url1 = "https://www.protiviti.com/au-en/client-story/national-vision-financial-reporting-sap-business-planning"
keyword = "SAP"
company = "protiviti"
raw_text = html_extract(url1)
clean_content = html_clean(raw_text)
context1 = extract_content_with_spacy(clean_content, keyword)
context2 = extract_content(clean_content, keyword)
context = context1
print(context)
# context = extract_content(clean_content, keyword)

# - context  -----------------
# question = f"How is {company} and {keyword} connected with each other"
question = f"""
            Analyze the following text about {company} (company name might not be well structured) to determine if it indicates that {company} uses, supports, develops, deploys, partners with, or is actively involved with the technology or concept of '{keyword}'.
            Note: If the technology is mentioned in Job description by that company means they use that technology.
            Note: The company name might not always be explicitly mentioned, could be misspelled, have irregular spacing, or be mixed with unrelated tokens or unknown words. Focus on contextual clues to assess technology usage.
            **Important Guidance:**
            To help you assess company involvement accurately, compare the text against the following key phrases. These are indicators of meaningful involvement with "{keyword}":
            * Integration & Compatibility: If a product from {company} is described as being 'integrated with' or 'compatible with' {keyword}, this is a strong indicator of usage.
            """
# question = f"""
#             Determine if {company} uses {keyword} based only on the text below. followed by a one-sentence explanation.
#             Rules for your answer:
#             Answer 'Yes' if the text provides direct evidence of operational use by the company (e.g., a company statement, a job posting, or a technical case study).
#             Answer 'No' if the text describes third-party use, educational programs, individual certifications, speculation, or a context mismatch.
#             """
# question = ""

# --- 2. Invoke the Pipeline ---
result = qa_pipeline(question=question, context=str(context))
duration = time.time() - start_time

# --- 3. Print the Result ---
print("\n--- Extracted Answer ---")
# This model returns a dictionary containing the answer, score, start, and end positions
print(f"Answer: {result['answer']}")
print(f"Confidence Score: {result['score']:.4f}")
print(f"Confidence Score: {result}")
print(f"time: {duration:.2f} sec.")

