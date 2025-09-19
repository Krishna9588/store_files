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
qa_pipeline = pipeline("question-answering", model="timpal0l/mdeberta-v3-base-squad2",device=device)

print("--- Pipeline Loaded ---")

# --- 1. Define the Context and Question ---
url1 = "https://atos.net/en/alliances-partnerships/atos-and-sap"
raw_text = html_extract(url1)
clean_content = html_clean(raw_text)
keyword = "SAP"
context = extract_context_with_spacy(clean_content, keyword)
# context = extract_content(clean_content, keyword)


# - context  -----------------
company = {"atos"}
question = f"How is {company} associated with {keyword}, Is {company} they patners, working togenter or used services of other"
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
qa_pipeline = pipeline("question-answering", model="timpal0l/mdeberta-v3-base-squad2",device=device)

print("--- Pipeline Loaded ---")

# --- 1. Define the Context and Question ---
url1 = "https://www.ocbc.com.hk/webpages/en-us/html/cor_overview/career/support_control.html?id=CareerOpportunities"
keyword = "SAP"
company = "OCBC"
raw_text = html_extract(url1)
clean_content = html_clean(raw_text)
context = extract_content(clean_content, keyword)
# context = extract_content(clean_content, keyword)

# - context  -----------------


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

