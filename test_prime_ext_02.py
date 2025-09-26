# --- IMPORTS ---
# Your existing functions for extracting text
from extract.normal_3 import normal
from explain_io import explain
# Our new, powerful semantic analysis library
from prime_extract_02 import isolate_focused_context, analyze_relationship_semantically, get_summary_category

# --- INPUTS ---
# company_name = "Birlasoft"
# keyword = "AWS"
# url = "https://www.birlasoft.com/services/enterprise-products/aws"

company_name = "vasscompany"
keyword = "sap"
# url = "https://www.nutanix.com/vmware-alternative/vmware-cloud-aws-promotion?utm_source=google_adwords&utm_medium=paid_search&utm_campaign=Nutanix_Search_APAC_T1_Cohort-Awareness_Google_Awareness_English&utm_term=aws%20cloud%20technology&utm_experience=&cq_plac=&cq_net=g&cq_plt=gp&cq_cmp=22870534290&_bt=768344371864&_bk=aws%20cloud%20technology&_bm=p&_bn=g&_bg=183640285677&gad_source=1&gad_campaignid=22870534290&gbraid=0AAAAADN2VjZgrOfHkBPPVQtJlBpjSOCbR&gclid=CjwKCAjwxfjGBhAUEiwAKWPwDhrSEmyGsIEOoBdHl3f4KH2-7Kyush8PJ9AZ_FCvnTUaI4MziPZGjBoCuvAQAvD_BwE"
url = "https://vasscompany.com/apac/en/insights/blogs-articles/sap-erp/"

# --- DATA EXTRACTION ---
print(f"INFO: Extracting content from {url}...")
ext_content = str(normal(url, keyword))
print("INFO: Content extracted.")

# --- SEMANTIC ANALYSIS (Using our new library) ---
print("INFO: Starting semantic analysis...")
# 1. Isolate the most relevant context using the new, smarter function
isolated_chunk = isolate_focused_context(ext_content, company_name, keyword)

# 2. Analyze the chunk to get detailed predictions and evidence
if isolated_chunk:
    analysis_result = analyze_relationship_semantically(isolated_chunk, company_name, keyword)

    # 3. Get the high-level summary category from the top prediction
    top_prediction = analysis_result['top_predictions'][0]
    summary = get_summary_category(top_prediction['category'])

    # --- OUTPUT RESULTS ---
    print("\n" + "=" * 30)
    print("--- Semantic Analysis Result ---")
    print(f"High-Level Summary: {summary}")
    print("-" * 20)

    # Print the top 3 detailed predictions
    for pred in analysis_result['top_predictions']:
        print(f"Predicted Category: {pred['category']:<35} | Confidence: {pred['confidence']:.2%}")

    print("-" * 20)
    print(f"Supporting Evidence:  \"{analysis_result['evidence']}\"")
    print("=" * 30 + "\n")

else:
    print("ANALYSIS FAILED: Keyword not found or no relevant context could be isolated.")

# --- GEMINI ANALYSIS (Your existing logic) ---
print("INFO: Starting Gemini analysis...")
gemini_analysis = explain(ext_content, keyword, company_name, url)

if gemini_analysis:
    print("--- Gemini Result ---")
    usage_indicated = "Yes" if gemini_analysis.get("uses_tech") else "No"
    explanation = gemini_analysis.get("explanation", "No explanation provided.")
    print(f"Usage Indicated: {usage_indicated}")
    print(f"Explanation: {explanation}")
    print("=" * 30 + "\n")
