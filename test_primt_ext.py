from prime_extract import *
from explain_io import *
from extract.normal_3 import *

# --- Main Execution ---

# company_info
# company_name = "vasscompany"
company_name = "Birlasoft"
keyword = "AWS"
# url = "https://www.nutanix.com/vmware-alternative/vmware-cloud-aws-promotion?utm_source=google_adwords&utm_medium=paid_search&utm_campaign=Nutanix_Search_APAC_T1_Cohort-Awareness_Google_Awareness_English&utm_term=aws%20cloud%20technology&utm_experience=&cq_plac=&cq_net=g&cq_plt=gp&cq_cmp=22870534290&_bt=768344371864&_bk=aws%20cloud%20technology&_bm=p&_bn=g&_bg=183640285677&gad_source=1&gad_campaignid=22870534290&gbraid=0AAAAADN2VjZgrOfHkBPPVQtJlBpjSOCbR&gclid=CjwKCAjwxfjGBhAUEiwAKWPwDhrSEmyGsIEOoBdHl3f4KH2-7Kyush8PJ9AZ_FCvnTUaI4MziPZGjBoCuvAQAvD_BwE"
url = "https://www.birlasoft.com/services/enterprise-products/aws"
# url = "https://vasscompany.com/apac/en/insights/blogs-articles/sap-erp/"
# normal_content extraction
ext_content = str(normal(url, keyword))

# Gemini Exp
# gemini_analysis = explain(str(ext_content),str(keyword),str(company_name),str(url))
gemini_analysis = explain(ext_content, keyword, company_name, url)
# explain_gemi = explain(ext_content, keyword, company_name, url)

print("--- Gemini Result ---")
print("\n" + "=" * 30 + "\n")
usage_indicated = "Yes" if gemini_analysis.get("uses_tech") else "No"
explanation = gemini_analysis.get("explanation", "No explanation provided.")
push_context = gemini_analysis.get("push_context", "No context found.")
print(f"usage_indicated: {usage_indicated}")
print(f"explanation: {explanation}")
# print(gemini_analysis)

# prime_extract

# 1. Isolate the most relevant context
isolated_chunk = isolate_context(ext_content, keyword)

# 2. Analyze the chunk to get the classification and evidence
if isolated_chunk:
    print("--- Isolated Context Chunk ---")
    print(f"length of Isolated chunk: {len(isolated_chunk)}")
    print("\n" + "=" * 30 + "\n")
    analysis_result = analyze_relationship_semantically(isolated_chunk, company_name, keyword)
    print("--- Analysis Result ---")
    print(f"Predicted Category: {analysis_result['category']}")
    print(f"Confidence Score:   {analysis_result['confidence']:.2%}")
    # print(f"Supporting Evidence:  \"{analysis_result['evidence']}\"")
else:
    print(f"Keyword '{keyword}' not found in the text.")

