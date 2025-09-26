#
# import spacy
# from sentence_transformers import SentenceTransformer, util
# import numpy as np
# # from extract.normal_3 import *
# nlp = spacy.load("en_core_web_sm")
# semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
#
# def isolate_context(text, keyword, sentences_before=2, sentences_after=2):
#     """
#     Finds sentences with the keyword and extracts a surrounding paragraph for context.
#     """
#     doc = nlp(str(text))
#     sentences = list(doc.sents)
#     relevant_indices = set()
#
#     for i, sentence in enumerate(sentences):
#         if keyword.lower() in sentence.text.lower() or "amazon web services" in sentence.text.lower():
#             start_index = max(0, i - sentences_before)
#             end_index = min(len(sentences), i + sentences_after + 1)
#             relevant_indices.update(range(start_index, end_index))
#
#     if not relevant_indices:
#         return None
#
#     sorted_indices = sorted(list(relevant_indices))
#     context_text = " ".join([sentences[i].text.strip() for i in sorted_indices])
#     return context_text
#
#
# def analyze_relationship_semantically(context_text, company_name, keyword):
#     """
#     Analyzes the context chunk to classify the relationship using semantic similarity.
#     """
#     if not context_text:
#         return {"category": "Uncertain", "confidence": 0.0, "evidence": "Keyword not found in text."}
#
#     relationship_profiles = {
#         "Service Provider/Partner": (
#             f"{company_name} offers professional services, solutions, consulting, and expertise for {keyword}. "
#             f"They help their clients migrate to, build on, or manage the {keyword} platform. "
#             f"They have a partnership, certification, or competency with {keyword}."
#         ),
#         "Service User": (
#             f"{company_name} uses {keyword} to power its own internal infrastructure, products, or applications. "
#             f"Their technology stack is built on {keyword}. They are a customer or consumer of the service."
#         ),
#         "Informative": (
#             f"This is an informational article, blog post, or guide explaining what {keyword} is. "
#             f"It describes the technology, its benefits, or how to use it in a general sense, not tied to {company_name}'s specific offerings."
#         ),
#         # ===============================================
#         # === CONTENT & PUBLISHING SIGNALS ===
#         # ===============================================
#         "Content_Informational_Guide": (
#             f"This text is a blog post, article, tutorial, or guide that explains what {keyword} is. "
#             f"It describes the technology, its benefits, features, or best practices in a general, educational sense. "
#             f"The content aims to inform or teach the reader, rather than sell a specific product from {company_name}."
#         ),
#         "Content_Marketing_And_Promotion": (
#             f"The content is a promotion, advertisement, or marketing material from {company_name} related to {keyword}. "
#             f"It is likely promoting a webinar, a special offer, an event, or a downloadable asset like a whitepaper. "
#             f"The primary goal is marketing, lead generation, or driving attendance."
#         ),
#         "Content_News_And_Announcements": (
#             f"This is a news article, press release, or formal announcement. It might be {company_name} announcing a new "
#             f"achievement or partnership involving {keyword}, or it could be a general news report that mentions the technology, "
#             f"where {company_name} is cited or featured."
#         ),
#         "Content_Comparison_Review": (
#             f"This content is an article or blog post that compares, reviews, or analyzes {keyword} against other technologies. "
#             f"It might list pros and cons, benchmarks, or present {keyword} as an alternative to another solution. "
#             f"The tone is evaluative and intended to help readers make a choice."
#         ),
#         # =================================================
#         # === TECHNOLOGY USAGE & IMPLEMENTATION SIGNALS ===
#         # =================================================
#         "Usage_Core_Infrastructure": (
#             f"The company's core infrastructure is powered by, built with, or runs on {keyword}. "
#             f"Their primary applications and services are hosted on this technology, making it foundational to their operations."
#         ),
#         "Usage_Active_Deployment": (
#             f"The company has actively adopted, deployed, or implemented {keyword} within its technology stack. "
#             f"This indicates a completed or ongoing rollout of the technology for production use."
#         ),
#         "Usage_Development_Stack": (
#             f"The company's software is developed, written, coded, or engineered using {keyword}. "
#             f"It is a key tool or platform for their software development lifecycle."
#         ),
#         "Usage_Product_Integration": (
#             f"The company's own products have incorporated, embedded, or are integrated with {keyword}. "
#             f"The technology functions as a component or feature within their commercial offerings."
#         ),
#         # ===============================================
#         # === PARTNERSHIP & COMMERCIAL SIGNALS ===
#         # ===============================================
#         "Partnership_Formal_Alliance": (
#             f"{company_name} has a formal partnership, strategic alliance, or is a recognized vendor for {keyword}. "
#             f"This signifies a high-level, official business relationship for mutual benefit."
#         ),
#         "Partnership_Collaborative_Project": (
#             f"{company_name} has collaborated with, teamed up with, or is in a joint venture involving {keyword}. "
#             f"This points to a specific, project-based cooperation rather than a formal partner status."
#         ),
#         "Commercial_Solutions_Provider": (
#             f"{company_name} develops and sells solutions, applications, or offerings that are based on {keyword}. "
#             f"They position themselves as experts who deliver value on top of the technology."
#         ),
#         "Commercial_Sales_Channel": (
#             f"As a reseller or channel partner, {company_name} is authorized to sell {keyword}. "
#             f"They function as a sales or distribution channel for the technology."
#         ),
#         "Commercial_Case_Study_Proof": (
#             f"The company presents case studies or success stories demonstrating their expertise with {keyword}. "
#             f"This is used as proof of their capabilities to attract new clients."
#         ),
#         # ===============================================
#         # === HIRING & PERSONNEL SIGNALS ===
#         # ===============================================
#         "Hiring_Active_Recruitment": (
#             f"{company_name} is actively hiring, recruiting, or seeking candidates for open roles and job postings. "
#             f"Their career pages list vacancies that explicitly mention {keyword}."
#         ),
#         "Hiring_Skill_Requirement": (
#             f"Job descriptions at {company_name} list experience with {keyword} as a required, mandatory, or desired skill. "
#             f"This indicates a practical need for this skill within their teams."
#         ),
#         "Hiring_Proficiency_And_Certification": (
#             f"Candidates are expected to have a high level of proficiency, expertise, or certification in {keyword}. "
#             f"The company values formal training, qualifications, and deep competency in the technology."
#         ),
#         # ===============================================
#         # === FINANCIAL & PROCUREMENT SIGNALS ===
#         # ===============================================
#         "Financial_Budget_And_Investment": (
#             f"{company_name} has made a financial investment, allocated a budget, or has significant IT spend related to {keyword}. "
#             f"This shows a strategic financial commitment to the technology."
#         ),
#         "Financial_Direct_Procurement": (
#             f"The company has a direct procurement relationship, having purchased, licensed, or subscribed to {keyword}. "
#             f"They hold a direct contract or have made a payment for the service."
#         ),
#         "Financial_Service_Engagement": (
#             f"{company_name} has engaged, retained, or outsourced services related to {keyword}. "
#             f"They are paying a third party for consulting, management, or implementation of the technology."
#         ),
#         # ===============================================
#         # === TECHNICAL ACTION & MANAGEMENT SIGNALS ===
#         # ===============================================
#         "Technical_Strategic_Modernization": (
#             f"The company is undergoing a strategic initiative involving {keyword}, such as a digital transformation, "
#             f"migration, system upgrade, or replatforming of their legacy applications."
#         ),
#         "Technical_DevOps_And_Automation": (
#             f"The company utilizes {keyword} for modern DevOps practices. This includes automating processes, "
#             f"orchestrating workflows, or managing containerized environments."
#         ),
#         "Technical_Performance_Optimization": (
#             f"The company is focused on performance, using {keyword} to scale, optimize, enhance, or augment their systems. "
#             f"The goal is to improve the efficiency and capability of their existing infrastructure."
#         ),
#         "Technical_Ongoing_Operations": (
#             f"The company is responsible for the day-to-day operational management of {keyword}. This involves "
#             f"supporting, monitoring, maintaining, configuring, and customizing the technology."
#         )
#     }
#
#     # --- Step 2: Encode Profiles and Context ---
#     profile_embeddings = semantic_model.encode(list(relationship_profiles.values()))
#     context_embedding = semantic_model.encode(context_text)
#
#     # --- Step 3: Calculate Similarity Scores ---
#     similarities = util.cos_sim(context_embedding, profile_embeddings)[0]  # Get a 1D tensor of scores
#
#     # --- Step 4: Classify and Get Confidence ---
#     top_score_index = np.argmax(similarities)
#     confidence_score = float(similarities[top_score_index])
#     winner_category = list(relationship_profiles.keys())[top_score_index]
#
#     # --- Step 5: Extract Best Sentence as Evidence ---
#     # Find the single sentence in the context that is most similar to the winning profile.
#     context_sentences = [sent.text.strip() for sent in nlp(context_text).sents]
#     sentence_embeddings = semantic_model.encode(context_sentences)
#     winning_profile_embedding = profile_embeddings[top_score_index]
#
#     evidence_similarities = util.cos_sim(winning_profile_embedding, sentence_embeddings)[0]
#     best_sentence_index = np.argmax(evidence_similarities)
#     evidence_sentence = context_sentences[best_sentence_index]
#
#     return {
#         "category": winner_category,
#         "confidence": round(confidence_score, 4),
#         "evidence": evidence_sentence
#     }
#
#
# # # --- Main Execution ---
# #
# # # from prime_normal import *
# # from extract.normal_3 import *
# # company_name = "nutanix"
# # keyword = "AWS"
# # # url = "https://www.birlasoft.com/services/enterprise-products/aws"
# # url = "https://www.nutanix.com/vmware-alternative/vmware-cloud-aws-promotion?utm_source=google_adwords&utm_medium=paid_search&utm_campaign=Nutanix_Search_APAC_T1_Cohort-Awareness_Google_Awareness_English&utm_term=aws%20cloud%20technology&utm_experience=&cq_plac=&cq_net=g&cq_plt=gp&cq_cmp=22870534290&_bt=768344371864&_bk=aws%20cloud%20technology&_bm=p&_bn=g&_bg=183640285677&gad_source=1&gad_campaignid=22870534290&gbraid=0AAAAADN2VjZgrOfHkBPPVQtJlBpjSOCbR&gclid=CjwKCAjwxfjGBhAUEiwAKWPwDhrSEmyGsIEOoBdHl3f4KH2-7Kyush8PJ9AZ_FCvnTUaI4MziPZGjBoCuvAQAvD_BwE"
# # ext_content = normal(url, keyword)
# #
# #
# # from explain_new_json import *
# # gemini_analysis = explain(
# #                 chunk_text= str(ext_content),
# #                 keyword_tech=str(keyword),
# #                 company_name=str(company_name),
# #                 page_url=str(url)
# #             )
# # # print(ext_content)
# # # print(date,social)
# # # 1. Isolate the most relevant context
# # isolated_chunk = isolate_context(ext_content, keyword)
# #
# # # 2. Analyze the chunk to get the classification and evidence
# # if isolated_chunk:
# #     print("--- Isolated Context Chunk ---")
# #     print(f"length of Isolated chunk: {len(isolated_chunk)}")
# #     print("\n" + "=" * 30 + "\n")
# #
# #     analysis_result = analyze_relationship_semantically(isolated_chunk, company_name, keyword)
# #
# #     print("--- Analysis Result ---")
# #     print(f"Predicted Category: {analysis_result['category']}")
# #     print(f"Confidence Score:   {analysis_result['confidence']:.2%}")
# #     print(f"Supporting Evidence:  \"{analysis_result['evidence']}\"")
# #
# # else:
# #     print(f"Keyword '{keyword}' not found in the text.")
# #
# # if gemini_analysis:
# #     print("--- Extracted Content ---")
# #     usage_indicated = "Yes" if gemini_analysis.get("uses_tech") else "No"
# #     explanation = gemini_analysis.get("explanation", "No explanation provided.")
# #     push_context = gemini_analysis.get("push_context", "No context found.")
# #     print(f"usage_indicated: {usage_indicated}")
# #     print(f"explanation: {explanation}")
# #     # print(f"{ext_content}")
# # else:
# #     print("No content was extracted.")
#

import spacy
from sentence_transformers import SentenceTransformer, util
import numpy as np

# --- SETUP ---
nlp = spacy.load("en_core_web_sm")
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# --- FUNCTIONS ---
def isolate_focused_context(text, company_name, keyword, sentences_before=2, sentences_after=2):
    """
    IMPROVEMENT 1: Smarter Context Isolation
    Finds sentences with BOTH the company and keyword for high-priority context.
    If none are found, it falls back to finding just the keyword to handle broader texts.
    """
    doc = nlp(str(text))
    sentences = list(doc.sents)
    relevant_indices = set()

    # Priority 1: Find sentences with BOTH company and keyword for precision.
    for i, sentence in enumerate(sentences):
        sent_text_lower = sentence.text.lower()
        company_names = [company_name.lower(), company_name.lower().replace(" ", "")]
        if any(name in sent_text_lower for name in company_names) and keyword.lower() in sent_text_lower:
            start_index = max(0, i - sentences_before)
            end_index = min(len(sentences), i + sentences_after + 1)
            relevant_indices.update(range(start_index, end_index))

    # Priority 2: If no specific link is found, analyze the general context around the keyword.
    if not relevant_indices:
        for i, sentence in enumerate(sentences):
            if keyword.lower() in sentence.text.lower():
                start_index = max(0, i - sentences_before)
                end_index = min(len(sentences), i + sentences_after + 1)
                relevant_indices.update(range(start_index, end_index))

    if not relevant_indices:
        return None

    sorted_indices = sorted(list(relevant_indices))
    context_text = " ".join([sentences[i].text.strip() for i in sorted_indices])
    return context_text

def analyze_relationship_semantically(context_text, company_name, keyword):
    """
    Analyzes the context to classify the relationship using a detailed set of profiles.
    Returns the top 3 predictions and the best evidence sentence.
    """
    if not context_text:
        return {"top_predictions": [{"category": "Uncertain", "confidence": 0.0}],
                "evidence": "Keyword not found in text."}

    # IMPROVEMENT 2: Cleaner, More Precise Profiles
    # The redundant, broad profiles ("Service Provider/Partner", "Service User", "Informative") have been removed
    # to force the model to choose a more specific and useful category.
    relationship_profiles = {
        # ===============================================
        # === CONTENT & PUBLISHING SIGNALS ===
        # ===============================================
        "Content_Informational_Guide": (
            f"This text is a blog post, article, tutorial, or guide that explains what {keyword} is. "
            f"It describes the technology, its benefits, features, or best practices in a general, educational sense. "
            f"The content aims to inform or teach the reader, rather than sell a specific product from {company_name}."
        ),
        "Content_Marketing_And_Promotion": (
            f"The content is a promotion, advertisement, or marketing material from {company_name} related to {keyword}. "
            f"It is likely promoting a webinar, a special offer, an event, or a downloadable asset like a whitepaper. "
            f"The primary goal is marketing, lead generation, or driving attendance."
        ),
        "Content_News_And_Announcements": (
            f"This is a news article, press release, or formal announcement. It might be {company_name} announcing a new "
            f"achievement or partnership involving {keyword}, or it could be a general news report that mentions the technology, "
            f"where {company_name} is cited or featured."
        ),
        "Content_Comparison_Review": (
            f"This content is an article or blog post that compares, reviews, or analyzes {keyword} against other technologies. "
            f"It might list pros and cons, benchmarks, or present {keyword} as an alternative to another solution. "
            f"The tone is evaluative and intended to help readers make a choice."
        ),
        # =================================================
        # === TECHNOLOGY USAGE & IMPLEMENTATION SIGNALS ===
        # =================================================
        "Usage_Core_Infrastructure": (
            f"The company's core infrastructure is powered by, built with, or runs on {keyword}. "
            f"Their primary applications and services are hosted on this technology, making it foundational to their operations."
        ),
        "Usage_Active_Deployment": (
            f"The company has actively adopted, deployed, or implemented {keyword} within its technology stack. "
            f"This indicates a completed or ongoing rollout of the technology for production use."
        ),
        "Usage_Development_Stack": (
            f"The company's software is developed, written, coded, or engineered using {keyword}. "
            f"It is a key tool or platform for their software development lifecycle."
        ),
        "Usage_Product_Integration": (
            f"The company's own products have incorporated, embedded, or are integrated with {keyword}. "
            f"The technology functions as a component or feature within their commercial offerings."
        ),
        # ... [and so on for all other granular profiles] ...
        "Partnership_Formal_Alliance": (
            f"{company_name} has a formal partnership, strategic alliance, or is a recognized vendor for {keyword}. "
            f"This signifies a high-level, official business relationship for mutual benefit."
        ),
        "Partnership_Collaborative_Project": (
            f"{company_name} has collaborated with, teamed up with, or is in a joint venture involving {keyword}. "
            f"This points to a specific, project-based cooperation rather than a formal partner status."
        ),
        "Commercial_Solutions_Provider": (
            f"{company_name} develops and sells solutions, applications, or offerings that are based on {keyword}. "
            f"They position themselves as experts who deliver value on top of the technology."
        ),
        "Commercial_Sales_Channel": (
            f"As a reseller or channel partner, {company_name} is authorized to sell {keyword}. "
            f"They function as a sales or distribution channel for the technology."
        ),
        "Commercial_Case_Study_Proof": (
            f"The company presents case studies or success stories demonstrating their expertise with {keyword}. "
            f"This is used as proof of their capabilities to attract new clients."
        ),
        "Hiring_Active_Recruitment": (
            f"{company_name} is actively hiring, recruiting, or seeking candidates for open roles and job postings. "
            f"Their career pages list vacancies that explicitly mention {keyword}."
        ),
        "Hiring_Skill_Requirement": (
            f"Job descriptions at {company_name} list experience with {keyword} as a required, mandatory, or desired skill. "
            f"This indicates a practical need for this skill within their teams."
        ),
        "Hiring_Proficiency_And_Certification": (
            f"Candidates are expected to have a high level of proficiency, expertise, or certification in {keyword}. "
            f"The company values formal training, qualifications, and deep competency in the technology."
        ),
        "Financial_Budget_And_Investment": (
            f"{company_name} has made a financial investment, allocated a budget, or has significant IT spend related to {keyword}. "
            f"This shows a strategic financial commitment to the technology."
        ),
        "Financial_Direct_Procurement": (
            f"The company has a direct procurement relationship, having purchased, licensed, or subscribed to {keyword}. "
            f"They hold a direct contract or have made a payment for the service."
        ),
        "Financial_Service_Engagement": (
            f"{company_name} has engaged, retained, or outsourced services related to {keyword}. "
            f"They are paying a third party for consulting, management, or implementation of the technology."
        ),
        "Technical_Strategic_Modernization": (
            f"The company is undergoing a strategic initiative involving {keyword}, such as a digital transformation, "
            f"migration, system upgrade, or replatforming of their legacy applications."
        ),
        "Technical_DevOps_And_Automation": (
            f"The company utilizes {keyword} for modern DevOps practices. This includes automating processes, "
            f"orchestrating workflows, or managing containerized environments."
        ),
        "Technical_Performance_Optimization": (
            f"The company is focused on performance, using {keyword} to scale, optimize, enhance, or augment their systems. "
            f"The goal is to improve the efficiency and capability of their existing infrastructure."
        ),
        "Technical_Ongoing_Operations": (
            f"The company is responsible for the day-to-day operational management of {keyword}. This involves "
            f"supporting, monitoring, maintaining, configuring, and customizing the technology."
        )
    }

    # --- Step 1: Encode Profiles and Context ---
    profile_embeddings = semantic_model.encode(list(relationship_profiles.values()))
    context_embedding = semantic_model.encode(context_text)

    # --- Step 2: Calculate Similarity Scores ---
    similarities = util.cos_sim(context_embedding, profile_embeddings)[0]

    # --- Step 3: Get Top 3 Predictions ---
    # IMPROVEMENT 3: Richer Output with Top 3 Predictions
    top_k = min(3, len(relationship_profiles))
    top_indices = np.argsort(similarities)[-top_k:][::-1]  # Get indices of top k scores, sorted descending

    predictions = []
    for index in top_indices:
        category = list(relationship_profiles.keys())[index]
        confidence = float(similarities[index])
        predictions.append({"category": category, "confidence": round(confidence, 4)})

    # --- Step 4: Extract Best Evidence Sentence (based on the #1 prediction) ---
    best_prediction_index = top_indices[0]
    winning_profile_embedding = profile_embeddings[best_prediction_index]

    context_sentences = [sent.text.strip() for sent in nlp(context_text).sents if len(sent.text.strip()) > 10]
    if not context_sentences:
        return {"top_predictions": predictions, "evidence": "No suitable sentences found for evidence."}

    sentence_embeddings = semantic_model.encode(context_sentences)
    evidence_similarities = util.cos_sim(winning_profile_embedding, sentence_embeddings)[0]
    best_sentence_index = np.argmax(evidence_similarities)
    evidence_sentence = context_sentences[best_sentence_index]
    return {
        "top_predictions": predictions,
        "evidence": evidence_sentence
    }

def get_summary_category(granular_category):
    """
    IMPROVEMENT 4: Hierarchical Reporting for Easy Summaries
    Maps a detailed category to a high-level summary category.
    """
    HIERARCHICAL_MAP = {
        "PARTNER": ["Partnership_Formal_Alliance", "Partnership_Collaborative_Project", "Commercial_Solutions_Provider",
                    "Commercial_Sales_Channel", "Commercial_Case_Study_Proof"],
        "USER": ["Usage_Core_Infrastructure", "Usage_Active_Deployment", "Usage_Development_Stack",
                 "Usage_Product_Integration", "Technical_Strategic_Modernization", "Technical_DevOps_And_Automation",
                 "Technical_Performance_Optimization", "Technical_Ongoing_Operations"],
        "RECRUITING": ["Hiring_Active_Recruitment", "Hiring_Skill_Requirement", "Hiring_Proficiency_And_Certification"],
        "FINANCIAL": ["Financial_Budget_And_Investment", "Financial_Direct_Procurement",
                      "Financial_Service_Engagement"],
        "CONTENT": ["Content_Informational_Guide", "Content_Marketing_And_Promotion", "Content_News_And_Announcements",
                    "Content_Comparison_Review"]
    }
    for summary, granular_list in HIERARCHICAL_MAP.items():
        if granular_category in granular_list:
            return summary
    return "UNCATEGORIZED"


# --- Main Execution Example ---
if __name__ == "__main__":
    # This is a placeholder for your text extraction logic (e.g., using BeautifulSoup)
    def extract_text_from_url(url, keyword):
        print(f"INFO: Placeholder - scraping text from {url}...")
        # A simple example text
        return """
        Nutanix Announces Strategic Partnership with AWS. As an official AWS partner, Nutanix now offers solutions
        that are deeply integrated with Amazon Web Services. Our joint customers can now run applications on
        Nutanix cloud infrastructure and seamlessly connect to AWS for services like S3 and Glacier. We are hiring
        engineers with AWS experience to build on this collaboration. This is a big investment for Nutanix.
        """


    # --- INPUTS ---
    company_name = "Nutanix"
    keyword = "AWS"
    url = "https://www.nutanix.com/some-partner-page"  # Example URL

    # --- PROCESSING ---
    extracted_text = extract_text_from_url(url, keyword)

    # 1. Isolate the most relevant context using the new, smarter function
    isolated_chunk = isolate_focused_context(extracted_text, company_name, keyword)

    # 2. Analyze the chunk to get detailed predictions and evidence
    if isolated_chunk:
        analysis_result = analyze_relationship_semantically(isolated_chunk, company_name, keyword)

        # 3. Get the high-level summary category from the top prediction
        top_category = analysis_result['top_predictions'][0]['category']
        summary = get_summary_category(top_category)

        # --- OUTPUT ---
        print("\n" + "=" * 30)
        print("--- Analysis Result ---")
        print(f"High-Level Summary: {summary}")
        print("-" * 20)
        # Print the top 3 detailed predictions
        for pred in analysis_result['top_predictions']:
            print(f"Predicted Category: {pred['category']}")
            print(f"Confidence Score:   {pred['confidence']:.2%}")
        print("-" * 20)
        print(f"Supporting Evidence:  \"{analysis_result['evidence']}\"")
        print("=" * 30 + "\n")

    else:
        print(f"Keyword '{keyword}' not found in the text.")