import spacy
from sentence_transformers import SentenceTransformer, util
import numpy as np

# --- SETUP: Models are loaded once when the module is imported for efficiency ---
nlp = spacy.load("en_core_web_sm")
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')


# --- CORE FUNCTIONS ---

def isolate_focused_context(text, company_name, keyword, sentences_before=2, sentences_after=2):
    """
    Smarter Context Isolation: Finds sentences with BOTH the company and keyword for high-priority context.
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

    # The Universal, Non-Redundant Relationship Profiles Dictionary
    relationship_profiles = {
        # ... [The full, universal dictionary is placed here] ...
        # CONTENT & PUBLISHING SIGNALS
        "Content_Informational_Guide": (
            f"This is an educational blog post, article, or guide about {keyword}. The company {company_name} is positioned as the publisher or thought leader."),
        "Content_Marketing_And_Promotion": (
            f"This content is a promotion, advertisement, or marketing material from {company_name} related to {keyword} to generate leads or sales."),
        "Content_News_And_Announcements": (
            f"This is a news article or press release about {keyword}, where {company_name} is mentioned."),
        "Content_Comparison_Review": (
            f"This content compares or reviews {keyword} against other technologies, with {company_name} as the author of the analysis."),
        # TECHNOLOGY USAGE & IMPLEMENTATION SIGNALS
        "Usage_Core_Infrastructure": (
            f"The company {company_name}'s core infrastructure is powered by, built with, or runs on {keyword}. Our platform is based on {keyword}."),
        "Usage_Active_Deployment": (
            f"The company {company_name} has actively adopted, deployed, or implemented {keyword} within its environment for production use."),
        "Usage_Development_Stack": (
            f"The company {company_name}'s software is developed or engineered using {keyword}. We build our applications with {keyword}."),
        "Usage_Product_Integration": (
            f"The company {company_name}'s own products have incorporated, embedded, or are integrated with {keyword}."),
        # PARTNERSHIP & COMMERCIAL SIGNALS
        "Partnership_Formal_Alliance": (
            f"{company_name} has a formal partnership, strategic alliance, or is a recognized vendor for {keyword}. We are a certified partner."),
        "Partnership_Collaborative_Project": (
            f"{company_name} collaborates with or teams up with a company related to {keyword} on a specific project."),
        "Commercial_Solutions_Provider": (
            f"{company_name} develops and sells solutions, applications, or consulting services based on {keyword}."),
        "Commercial_Sales_Channel": (
            f"As a reseller or channel partner, {company_name} is authorized to sell {keyword}."),
        "Commercial_Case_Study_Proof": (
            f"{company_name} presents case studies or success stories demonstrating their expertise with {keyword}."),
        # HIRING & PERSONNEL SIGNALS
        "Hiring_Active_Recruitment": (
            f"{company_name} is actively hiring or recruiting for roles that require expertise in {keyword}."),
        "Hiring_Skill_Requirement": (
            f"Job descriptions at {company_name} list experience with {keyword} as a required or mandatory skill."),
        "Hiring_Proficiency_And_Certification": (
            f"Candidates for a job at {company_name} are expected to have proficiency or certification in {keyword}."),
        # FINANCIAL & PROCUREMENT SIGNALS
        "Financial_Budget_And_Investment": (
            f"{company_name} has made a financial investment or allocated a budget for {keyword}."),
        "Financial_Direct_Procurement": (f"{company_name} has purchased, licensed, or subscribed to {keyword}."),
        "Financial_Service_Engagement": (
            f"{company_name} has engaged, retained, or outsourced services related to {keyword}."),
        # TECHNICAL ACTION & MANAGEMENT SIGNALS
        "Technical_Strategic_Modernization": (
            f"{company_name} is undergoing a migration, system upgrade, or replatforming involving {keyword}."),
        "Technical_DevOps_And_Automation": (
            f"{company_name} utilizes {keyword} for DevOps, automation, or container orchestration."),
        "Technical_Performance_Optimization": (
            f"{company_name} is focused on using {keyword} to scale, optimize, or enhance their systems."),
        "Technical_Ongoing_Operations": (
            f"{company_name} is responsible for supporting, monitoring, and maintaining systems using {keyword}.")
    }

    # --- Analysis Steps ---
    profile_embeddings = semantic_model.encode(list(relationship_profiles.values()))
    context_embedding = semantic_model.encode(context_text)
    similarities = util.cos_sim(context_embedding, profile_embeddings)[0]

    # Return top 3 predictions for a richer analysis
    top_k = min(3, len(relationship_profiles))
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    predictions = []
    for index in top_indices:
        category = list(relationship_profiles.keys())[index]
        confidence = float(similarities[index])
        predictions.append({"category": category, "confidence": round(confidence, 4)})

    # Extract best evidence sentence based on the #1 prediction
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
    """Maps a detailed category to a high-level summary category for easy reporting."""
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

