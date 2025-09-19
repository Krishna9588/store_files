import spacy
from sentence_transformers import SentenceTransformer, util
import numpy as np
# from extract.normal_3 import *
from prime_normal import *
nlp = spacy.load("en_core_web_sm")
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

def isolate_context(text, keyword, sentences_before=2, sentences_after=2):
    """
    Finds sentences with the keyword and extracts a surrounding paragraph for context.
    """
    doc = nlp(str(text))
    sentences = list(doc.sents)
    relevant_indices = set()

    for i, sentence in enumerate(sentences):
        if keyword.lower() in sentence.text.lower() or "amazon web services" in sentence.text.lower():
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
        "Informative": (
            f"This is an informational article, blog post, or guide explaining what {keyword} is. "
            f"It describes the technology, its benefits, or how to use it in a general sense, not tied to {company_name}'s specific offerings."
        )
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

    return {
        "category": winner_category,
        "confidence": round(confidence_score, 4),
        "evidence": evidence_sentence
    }


# --- Main Execution ---

# Our example text chunk from the Birlasoft website

company_name = "Birlasoft"
keyword = "AWS"
url = "https://www.birlasoft.com/services/enterprise-products/aws"
ext_content = html(url, keyword)
# print(ext_content)

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