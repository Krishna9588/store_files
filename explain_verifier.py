import google.generativeai as genai
import json
from itertools import cycle

# It's good practice to share keys, but for simplicity, we'll keep them here.
# Consider moving to a central config file in the future.
API_KEYS = [
    "AIzaSyAeStmlXLi_u2kA_pQiInQBiZVBAM3HRqA",  # Vedisha - NEW_temp
    "AIzaSyDDYP4NIL28a19fupyUtL_oOvG9_d0zaA4",  # Krishna_P New
    "AIzaSyB2CMRJNrUBYn_Ow_fy461hKr5xhX6U6po",  # Vedisha_P - NEW
    "AIzaSyARqV2CdLY6RxX5BMAhtpvWXokEl3Jj0Vo",  # Swapnil
    "AIzaSyD1tz5JH2855URNIYgh4Y8EhIS9JNqQl1g",
    "AIzaSyAlfQ0UeUHFVfpehf-2CcuXdwwscgtXMOU",
]
key_cycler = cycle(API_KEYS)


# def verify_analysis(context: str, keyword: str, company_name: str, analysis_1: dict, analysis_2: dict) -> dict:
#     """
#     Acts as a final judge on two separate analyses using a chain-of-thought prompt.
#     """
#     prompt = f"""
#     You are a Senior Technology Analyst and an expert fact-checker. Your task is to act as a final arbiter between two junior analyst reports. You must critically evaluate their findings against the provided source text and make a definitive, final judgment.
#
#     **Source Evidence:**
#     - **Company:** {company_name}
#     - **Technology Keyword:** {keyword}
#     - **Source Text:** "{context}"
#
#     ---
#     **Junior Analyst Reports:**
#
#     **Analysis #1 (Standard Prompt):**
#     - **Decision:** `{analysis_1.get('uses_tech')}`
#     - **Justification:** "{analysis_1.get('explanation')}"
#
#     **Analysis #2 (Advanced Prompt):**
#     - **Decision:** `{analysis_2.get('uses_tech')}`
#     - **Justification:** "{analysis_2.get('explanation')}"
#      json.loads(cleaned_text)
#
#         return {
#             "uses_tech": parsed_response.get("final_decision", False),
#             "explanation": parsed_response.get("final_explanation", "Verification failed."),
#             "reasoning": parsed_response.get("reasoning", "No reasoning provided.")
#         }
#     except Exception as e:
#         print(f"|!▶ Error during verification step: {e}")
#         # Fallback: If verification fails, trust the more advanced model (analysis_2)
#         return {
#             "uses_tech": analysis_2.get('uses_tech', False),
#             "explanation": f"VERIFICATION FAILED. Falling back to Analysis #2: {analysis_2.get('explanation')}",
#             "reasoning": f"Error in verifier: {e}"
#         }