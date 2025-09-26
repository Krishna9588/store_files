from extract.normal_3 import *
from extract.pdf_3_adv import *
from explain_new_json import *
from extract.date_me_3 import *
from info import *
import pandas as pd
from datetime import datetime
import csv
import os
import time
import json
from pathlib import Path # clickable Links

# --- Configuration & Setup -----------------

load = "Temp"
csv_name = "All_New_Siemens_149" #result file name

# ----------- Setup for Input and Output dir. -----
print("| Make sure input file have columns: | company_id | company_name | domain | keyword | company_url | context(opt) |")
print(f"| Input File: {load} | Output File: {csv_name} |")
INPUT_FILE_PATH = f"input/{load}"
CHECKPOINT_FILE = f"result_new/{csv_name}_new_result.csv"
JSON_CHECKPOINT_FILE = f"json/result_new_json/{csv_name}_new_result.json"
# -------------------------------------------------


# ------- Checkpoint Function ---------------------
# ----------- File Header -------------------------
# ALL_DATA_HEADERS = ["Company Name", "Domain", "Page URL", "Keyword", "Date", "Context", "Usage Indicated",
#                     "Explanation", "Processing Time (s)"]
# CSV_CHECKPOINT_HEADERS = ["Company Name", "Domain", "Page URL", "Keyword", "Date", "Usage Indicated", "Explanation"]
ALL_DATA_HEADERS = ["Company ID","Company Name", "Domain", "Page URL", "Keyword", "Date", "Context", "Usage Indicated",
                    "Explanation", "Processing Time (s)"]  # ---- company_id remove comment and update above part.
CSV_CHECKPOINT_HEADERS = ["Company ID","Company Name", "Domain", "Page URL", "Keyword", "Date", "Usage Indicated", "Explanation"]


# -------------------------------------------------
def save_checkpoint(result: dict):
    """Appends a single result row to both CSV and JSON checkpoint files for redundancy."""
    # Ensure the checkpoint directory exists
    os.makedirs(os.path.dirname(CHECKPOINT_FILE), exist_ok=True)
    os.makedirs(os.path.dirname(JSON_CHECKPOINT_FILE), exist_ok=True)

    # --- 1. Save to CSV Checkpoint (Primary) ---
    csv_file_exists = os.path.exists(CHECKPOINT_FILE)
    try:
        with open(CHECKPOINT_FILE, "a", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_CHECKPOINT_HEADERS, extrasaction='ignore')
            if not csv_file_exists:
                writer.writeheader()
            writer.writerow(result)
            f.flush()  # Force Python's internal buffer to write to the OS
            os.fsync(f.fileno())  # Force the OS to write the data to the disk
    except IOError as e:
        print(f"  [ERROR] Could not write to CSV checkpoint file {CHECKPOINT_FILE}. {e}")

    # --- 2. Save to JSON Checkpoint (Backup) ---
    try:
        all_json_data = []
        # Read existing JSON data if the file exists and is valid
        if os.path.exists(JSON_CHECKPOINT_FILE):
            with open(JSON_CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                try:
                    all_json_data = json.load(f)
                    if not isinstance(all_json_data, list):
                        all_json_data = []  # Reset if file content is not a list
                except json.JSONDecodeError:
                    print(
                        f"  [WARNING] JSON checkpoint {JSON_CHECKPOINT_FILE} is corrupted. A new one will be created.")
                    all_json_data = []

        # Append the new result and write the entire list back
        all_json_data.append(result)
        with open(JSON_CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_json_data, f, ensure_ascii=False, indent=4)
            f.flush()  # Force Python's internal buffer to write to the OS
            os.fsync(f.fileno())  # Force the OS to write the data to the disk

    except IOError as e:
        print(f"  [ERROR] Could not write to JSON checkpoint file {JSON_CHECKPOINT_FILE}. {e}")


def load_processed_items():
    # --- 1. Attempt to load from the primary CSV checkpoint ---
    try:
        if os.path.exists(CHECKPOINT_FILE):
            df_checkpoint = pd.read_csv(CHECKPOINT_FILE)
            if "Page URL" in df_checkpoint.columns and (""
                                                        "Keyword") in df_checkpoint.columns:
                # Drop rows with missing values to prevent errors
                df_checkpoint.dropna(subset=["Page URL", "Keyword"], inplace=True)
                processed_set = set(zip(df_checkpoint["Page URL"], df_checkpoint["Keyword"]))
                if processed_set:
                    print(f"Loaded {len(processed_set)} items from CSV checkpoint.")
                    return processed_set
    except (pd.errors.EmptyDataError, KeyError) as e:
        print(f"Warning: CSV checkpoint is empty or invalid ({e}). Trying JSON backup.")
    except Exception as e:
        print(f"Warning: Could not load from CSV checkpoint ({e}). Trying JSON backup.")

    # --- 2. If CSV fails, attempt to load from the JSON backup ---
    try:
        if os.path.exists(JSON_CHECKPOINT_FILE):
            with open(JSON_CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                if isinstance(json_data, list):
                    processed_set = {
                        (item['Page URL'], item['Keyword'])
                        for item in json_data
                        if isinstance(item, dict) and 'Page URL' in item and 'Keyword' in item
                    }
                    if processed_set:
                        print(f"Loaded {len(processed_set)} items from JSON checkpoint backup.")
                        return processed_set
    except (json.JSONDecodeError, FileNotFoundError, TypeError) as e:
        print(f"Warning: Could not load from JSON checkpoint backup either ({e}).")

    # If both loading methods fail, start fresh
    return set()


# -------------------------------------------------

# --------------- Main Execution ------------------
def main():
    """Main function to run the processing script."""
    already_processed = load_processed_items()
    if already_processed:
        print(f"| Found {len(already_processed)} items in the checkpoint file to skip.")

    try:
        # Check if input file is CSV or JSON
        input_csv_path = f"{INPUT_FILE_PATH}.csv"
        input_json_path = f"{INPUT_FILE_PATH}.json"

        if os.path.exists(input_csv_path):
            df_input = pd.read_csv(input_csv_path)
            input_format = "CSV"
        elif os.path.exists(input_json_path):
            df_input = pd.read_json(input_json_path)
            input_format = "JSON"
        else:
            print(f"|▶ Error: Input file not found. Expected either '{input_csv_path}' or '{input_json_path}'")
            return

        # --- CHANGE 1: Added 'domain' to the required columns check ---
        # required_columns = ['company_name', 'company_url', 'keyword', 'domain_name']
        required_columns = ['company_name', 'domain', 'company_url', 'keyword']  # ,'context'
        if not all(col in df_input.columns for col in required_columns):
            print(f"|▶ Error: Input {input_format} '{INPUT_FILE_PATH}' must contain columns: {required_columns}")
            return
    except FileNotFoundError:
        print(f"| Error: Input file not found at '{INPUT_FILE_PATH}'")
        return
    except Exception as e:
        print(f"| An unexpected error occurred while reading the input file: {e}")
        return

    new_items_processed = 0

    for index, row in df_input.iterrows():
        # --- CHANGE 2: Read all required columns from the row, including the new domain ---
        # comp_name = row['company_name']
        current_url = row['company_url']
        keyword = row['keyword']
        domain_from_csv = row['domain']  # This is the new Domain Name
        # -------------------------------------------------------- http Problem
        if not current_url.startswith(("http://", "https://")):
            current_url = "https://" + current_url
        # ----------------------------------------------------------------------
        if (current_url, keyword) in already_processed:
            continue

        new_items_processed += 1
        # ----------------------------------------------------------------------
        # Company Name - Updated part
        company_name_from_csv = row.get('company_name')
        # comp_id = row.get('company_id') # comp_id
        comp_name = info(current_url, company_name_from_csv=company_name_from_csv)

        # ------ Company Index ------
        company_id = row.get('company_id') if 'company_id' in df_input.columns else None

        if company_id is not None:
            comp_id = int(company_id)
            ind = f"{index+1}. ID: {comp_id}"
        else:
            comp_id = new_items_processed
            ind = index+1
        # ---------------------------


        start_time = time.time()
        print(f"| {ind}. Processing URL: {current_url}, Keyword: {keyword}, Company: {comp_name}")


        # Check if context is provided in the input data
        provided_context = row.get('context') if 'context' in df_input.columns else None

        try:
            if provided_context is not None:
                # Use the provided context from input_file
                contexts = provided_context
                # For PDF files, we still need to call pdf() to get the date
                if current_url.lower().endswith(".pdf"):
                    _, date = pdf(current_url, keyword)  # Only get date, discard the context
                    print("|▶ Using provided context from input file, but getting date from PDF")
                else:
                    date = date_me(current_url)  # Get date using the existing function
                    print("|▶ Using provided context from input file")
            elif current_url.lower().endswith(".pdf"):
                contexts, date = pdf(current_url, keyword)
                print("|▶ Using PDF function")

            else:
                contexts = normal(current_url, keyword)
                date = date_me(current_url)
                #                 print(contexts[0:10])
                print("|▶ Using HTML function")

            gemini_analysis = explain(
                chunk_text=contexts,
                keyword_tech=keyword,
                company_name=comp_name,
                page_url=current_url  # Page url to LLM
            )
            usage_indicated = "Yes" if gemini_analysis.get("uses_tech") else "No"
            explanation = gemini_analysis.get("explanation", "No explanation provided.")
            push_context = gemini_analysis.get("push_context", "No context found.")

            print(f"|====▶ Usage Indicated: {usage_indicated}")
            result = {
                "Company ID": comp_id, #comp_id
                "Company Name": comp_name,
                "Domain": domain_from_csv,
                "Page URL": current_url,
                "Keyword": keyword,
                "Date": date or "Not found",
                "Context": push_context if push_context else "No context found",
                "Usage Indicated": usage_indicated,
                "Explanation": explanation
            }


        except Exception as e:
            print(f"|▶ [ERROR] Failed to process: | Continuing to next URL.")
            contexts_no = "No Context found"

            gemini_analysis = explain(
                chunk_text=contexts_no,
                keyword_tech=keyword,
                company_name=comp_name,
                page_url=current_url  # Page url to LLM
            )
            usage_indicated = "Yes" if gemini_analysis.get("uses_tech") else "No"
            explanation = gemini_analysis.get("explanation", "No explanation provided.")
            push_context = gemini_analysis.get("push_context", "No context found.")
            print(f"|====▶ Usage Indicated: {usage_indicated}")

            result = {
                "Company ID": comp_id, #comp_id
                "Company Name": comp_name,
                "Domain": domain_from_csv,
                "Page URL": current_url,
                "Keyword": keyword,
                "Date": "Not Found",  # add date here
                "Context": push_context if push_context else "No context found",
                "Usage Indicated": usage_indicated,
                "Explanation": explanation
            }

        duration = time.time() - start_time
        result["Processing Time (s)"] = round(duration, 2)

        print(f"|=====▶ Completed in {duration:.2f} seconds.")
        print("‾‾" * 40)

        save_checkpoint(result)

        # Check if the input was not empty and if no new items were processed
        if not df_input.empty and new_items_processed == 0:
            print("No new URLs were processed. All items in the input file were already in the checkpoint.")

        # Create clickable file links for modern terminals by converting paths to URIs.
    csv_uri = Path(CHECKPOINT_FILE).resolve().as_uri()
    json_uri = Path(JSON_CHECKPOINT_FILE).resolve().as_uri()

    print("\n\n--------------- Processing Complete ---------------")
    print(f"\nResults saved to:")
    print(f"»» CSV: {csv_uri}")
    print(f"»» JSON: {json_uri}")

# -------------------------------------------------
if __name__ == "__main__":
    main()
# -------------------------------------------------
