import spacy
from sentence_transformers import SentenceTransformer, util
import numpy as np
from extract.normal_3 import *
import re

# This is a comprehensive list of keywords to identify relevant sentences for context extraction.
# It helps find related sentences even if they don't contain the primary keyword.
KEYWORD_TARGETS = [
    # Technology usage
    "use", "using", "used", "adopted", "deployed", "implemented",
    "powered by", "enabled by", "built with", "runs on", "based on",
    "utilized", "developed with", "hosted on", "migrated to",
    "relied on", "incorporated", "embedded", "integrated", "engineered with",
    "constructed with", "configured with", "operates on", "compiled with",
    "compiled for", "written in", "coded in", "developed using", "products", "product",

    # Partnerships and integrations
    "partner", "partnership", "strategic partner", "collaborated with", "solution",
    "integrated with", "alliance", "reseller", "technology partner", "solutions",
    "solution partner", "OEM", "channel partner", "vendor", "offering", "applications",
    "works with", "cooperate with", "joint venture", "consortium", "application",
    "affiliate", "associated with", "in collaboration with", "case-studies", "studies",
    "teamed up with", "engaged with", "connected with", "case studies",

    # Hiring indicators
    "hiring", "job posting", "career opportunity", "recruiting",
    "skills required", "experience with", "desired skills", "looking for",
    "join our team", "open roles", "vacancy", "apply", "certified in",
    "seeking", "in search of", "requirement", "mandatory skills",
    "preferred skills", "competency in", "proficiency in", "expertise in",
    "qualified in", "trained in", "hands-on experience",

    # Spending and investment
    "investment", "budget", "procurement", "IT spend", "contract with",
    "financial commitment", "spending", "cost", "deal", "payment to", "funding",
    "allocated", "invested", "purchased", "acquired", "licensed", "subscription",
    "retained", "engaged service", "outsourced to", "sponsored",
    "capital expenditure", "CAPEX", "operational expenditure", "OPEX",

    # Additional technical indicators
    "migration", "upgrade", "refactor", "replatform", "containerized",
    "orchestrated", "automated", "scaled", "optimized", "monitored",
    "maintained", "supported", "configured", "customized", "extended",
    "enhanced", "augmented", "modernized", "transformed", "digitalized"
]

nlp = spacy.load("en_core_web_sm")
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')


def isolate_context(text, keyword, sentences_before=2, sentences_after=2):
    """
    Finds sentences with the keyword or related terms and extracts a surrounding paragraph for context.
    """
    doc = nlp(str(text))
    sentences = list(doc.sents)
    relevant_indices = set()

    # Create a lowercase set for faster lookup
    keyword_targets_lower = {target.lower() for target in KEYWORD_TARGETS}

    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.text.lower()
        # Check if the primary keyword or any of the secondary keywords are in the sentence
        if keyword.lower() in sentence_lower or any(target in sentence_lower for target in keyword_targets_lower):
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
    Analyzes the context chunk to classify the relationship using semantic similarity.
    """
    if not context_text:
        return {"category": "Uncertain", "confidence": 0.0, "evidence": "Keyword not found in text."}

    relationship_profiles = {
        "Service Provider/Partner": (
            f"{company_name} offers professional services, solutions, consulting, and expertise for {keyword}. "
            f"They help their clients migrate to, build on, or manage the {keyword} platform. "
            f"They have a partnership, certification, or competency with {keyword}."
        ),
        "Service User": (
            f"{company_name} uses {keyword} to power its own internal infrastructure, products, or applications. "
            f"Their technology stack is built on {keyword}. They are a customer or consumer of the service."
        ),
        "Developer/Contributor": (
            f"{company_name} is actively involved in the creation, development, or maintenance of the core {keyword} technology. "
            f"They contribute to open-source projects related to {keyword} or have released their own tools that extend it."
        ),
        "Hiring/Talent": (
            f"{company_name} is hiring for roles that require skills in {keyword}. "
            f"They are seeking new employees or talent with experience using or managing the technology."
        ),
        "Speculative/Promotional": (
            f"{company_name} mentions {keyword} in a forward-looking, general, or promotional context. "
            f"The company speculates on its future use, highlights it as a general industry trend, or uses it as a marketing buzzword without specific details of implementation."
        ),
        "Product/Feature Announcement": (
            f"{company_name} announces a new product, feature, or integration that uses or is built on {keyword}. "
            f"The text details a specific application of the technology within one of their products."
        ),
        "Press Release/Official Statement": (
            f"This is an official news release or statement from {company_name} regarding a collaboration, partnership, or new milestone related to {keyword}."
        ),
        "Event/Webinar Promotion": (
            f"{company_name} is promoting an event, webinar, or speaking engagement where they will discuss, present, or showcase a topic related to {keyword}."
        ),
        "Educational/How-To Guide": (
            f"The text is a tutorial, how-to guide, or educational resource explaining how to use {keyword}. "
            f"It provides general, non-specific instructions without detailing {company_name}'s products."
        )
    }

    # This dictionary maps the category names to the final, human-readable phrase.
    output_phrases = {
        "Service Provider/Partner": "is a Service Provider or Partner for",
        "Service User": "is a Service User of",
        "Developer/Contributor": "is a Developer/Contributor for",
        "Hiring/Talent": "is Hiring for roles that require",
        "Speculative/Promotional": "mentions",
        "Product/Feature Announcement": "has a Product/Feature Announcement related to",
        "Press Release/Official Statement": "has an Official Statement or Press Release about",
        "Event/Webinar Promotion": "is Promoting an Event or Webinar about",
        "Educational/How-To Guide": "has an Educational Guide about",
        "Uncertain": "has an uncertain relationship with"
    }

    # --- Step 2: Encode Profiles and Context ---
    profile_embeddings = semantic_model.encode(list(relationship_profiles.values()))
    context_embedding = semantic_model.encode(context_text)

    # --- Step 3: Calculate Similarity Scores ---
    similarities = util.cos_sim(context_embedding, profile_embeddings)[0]  # Get a 1D tensor of scores

    # --- Step 4: Classify and Get Confidence ---
    top_score_index = np.argmax(similarities)
    confidence_score = float(similarities[top_score_index])
    winner_category = list(relationship_profiles.keys())[top_score_index]

    # --- Step 5: Extract Best Sentence as Evidence ---
    # Find the single sentence in the context that is most similar to the winning profile.
    context_sentences = [sent.text.strip() for sent in nlp(context_text).sents]
    sentence_embeddings = semantic_model.encode(context_sentences)
    winning_profile_embedding = profile_embeddings[top_score_index]

    evidence_similarities = util.cos_sim(winning_profile_embedding, sentence_embeddings)[0]
    best_sentence_index = np.argmax(evidence_similarities)
    evidence_sentence = context_sentences[best_sentence_index]

    # Extract a smaller, more focused snippet from the best sentence
    # This directly addresses the "smaller and accurate" request.
    match = re.search(r'(.{0,50}\b' + re.escape(keyword) + r'\b.{0,50})', evidence_sentence, re.IGNORECASE)
    if match:
        evidence_snippet = match.group(1).strip()
    else:
        evidence_snippet = evidence_sentence  # Fallback to the whole sentence if regex fails

    # --- Step 6: Format the output sentence ---
    output_phrase = output_phrases.get(winner_category, "has an uncertain relationship with")
    formatted_sentence = f"{company_name} {output_phrase} {keyword}."

    return {
        "category": winner_category,
        "confidence": round(confidence_score, 4),
        "evidence": evidence_snippet,
        "formatted_output": formatted_sentence
    }


# --- Main Execution ---

# Our example text chunk from the Birlasoft website

# company_name = "AVer Information"
# keyword = "Gemini"
# url = "https://www.aver.com/AVerExpert/International-School-AI-Skillshttps://www.aver.com/AVerExpert/International-School-AI-Skills

# "
# ext_content = normal(url, keyword)


company_name = "Himaz"
keyword = "Azure"
url = "https://www.himax.com.tw/products/wiseeye-ai-sensing/wiseeye-online-store/"
ext_content = normal(url, keyword)

# 1. Isolate the most relevant context
isolated_chunk = isolate_context(ext_content, keyword)

# 2. Analyze the chunk to get the classification and evidence
if isolated_chunk:
    print("--- Isolated Context Chunk ---")
    print(isolated_chunk)
    print("\n" + "=" * 30 + "\n")

    analysis_result = analyze_relationship_semantically(isolated_chunk, company_name, keyword)

    print("--- Analysis Result ---")
    print(f"Predicted Category: {analysis_result['category']}")
    print(f"Confidence Score:   {analysis_result['confidence']:.2%}")
    print(f"Supporting Evidence:  \"{analysis_result['evidence']}\"")
else:
    print(f"Keyword '{keyword}' not found in the text.")
