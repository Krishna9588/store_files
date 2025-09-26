import spacy
from sentence_transformers import SentenceTransformer, util
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Data class to hold analysis results"""
    category: str
    confidence: float
    evidence: str
    context_chunk: str
    all_scores: Dict[str, float]

class RelationshipAnalyzer:
    """Analyzes relationships between companies and technologies using semantic similarity"""

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', spacy_model: str = "en_core_web_sm"):
        """Initialize the analyzer with specified models"""
        try:
            self.nlp = spacy.load(spacy_model)
            self.semantic_model = SentenceTransformer(model_name)
            logger.info(f"Loaded models: {spacy_model}, {model_name}")
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise

    def isolate_context(self, text: str, keyword: str, sentences_before: int = 2,
                        sentences_after: int = 2, additional_keywords: List[str] = None) -> Optional[str]:
        """
        Finds sentences with the keyword and extracts a surrounding paragraph for context.

        Args:
            text: Input text to analyze
            keyword: Primary keyword to search for
            sentences_before: Number of sentences before keyword to include
            sentences_after: Number of sentences after keyword to include
            additional_keywords: Additional keywords to search for

        Returns:
            Context text containing relevant sentences or None if not found
        """
        if not text or not keyword:
            return None

        doc = self.nlp(str(text))
        sentences = list(doc.sents)
        relevant_indices = set()

        # Build search terms
        search_terms = [keyword.lower()]
        if additional_keywords:
            search_terms.extend([term.lower() for term in additional_keywords])

        # Find sentences containing any search term
        for i, sentence in enumerate(sentences):
            sentence_text = sentence.text.lower()
            if any(term in sentence_text for term in search_terms):
                start_index = max(0, i - sentences_before)
                end_index = min(len(sentences), i + sentences_after + 1)
                relevant_indices.update(range(start_index, end_index))

        if not relevant_indices:
            logger.warning(f"No sentences found containing keywords: {search_terms}")
            return None

        # Combine relevant sentences
        sorted_indices = sorted(list(relevant_indices))
        context_text = " ".join([sentences[i].text.strip() for i in sorted_indices])

        logger.info(f"Extracted context from {len(sorted_indices)} sentences")
        return context_text

    def get_relationship_profiles(self, company_name: str, keyword: str) -> Dict[str, str]:
        """
        Define relationship profiles for classification

        Args:
            company_name: Name of the company
            keyword: Technology/service keyword

        Returns:
            Dictionary mapping category names to profile descriptions
        """
        return {
            "Service Provider/Partner": (
                f"{company_name} offers professional services, solutions, consulting, and expertise for {keyword}. "
                f"They help their clients migrate to, build on, or manage the {keyword} platform. "
                f"They have a partnership, certification, or competency with {keyword}. "
                f"They provide implementation, support, or managed services."
            ),
            "Service User": (
                f"{company_name} uses {keyword} to power its own internal infrastructure, products, or applications. "
                f"Their technology stack is built on {keyword}. They are a customer or consumer of the service. "
                f"They leverage {keyword} for their own business operations or product development."
            ),
            "Informative": (
                f"This is an informational article, blog post, or guide explaining what {keyword} is. "
                f"It describes the technology, its benefits, or how to use it in a general sense. "
                f"The content is educational or promotional but not tied to {company_name}'s specific offerings or usage."
            ),
            "Competitive": (
                f"{company_name} competes with or offers alternatives to {keyword}. "
                f"They provide similar services or products that compete in the same market space. "
                f"The content discusses differences, comparisons, or competitive advantages."
            )
        }

    def analyze_relationship_semantically(self, context_text: str, company_name: str,
                                          keyword: str) -> AnalysisResult:
        """
        Analyzes the context chunk to classify the relationship using semantic similarity.

        Args:
            context_text: Text context to analyze
            company_name: Name of the company
            keyword: Technology/service keyword

        Returns:
            AnalysisResult object with classification details
        """
        if not context_text:
            return AnalysisResult(
                category="Uncertain",
                confidence=0.0,
                evidence="Keyword not found in text.",
                context_chunk="",
                all_scores={}
            )

        # Get relationship profiles
        relationship_profiles = self.get_relationship_profiles(company_name, keyword)

        try:
            # Encode profiles and context
            profile_embeddings = self.semantic_model.encode(list(relationship_profiles.values()))
            context_embedding = self.semantic_model.encode(context_text)

            # Calculate similarity scores
            similarities = util.cos_sim(context_embedding, profile_embeddings)[0]

            # Create scores dictionary
            all_scores = {
                category: float(score)
                for category, score in zip(relationship_profiles.keys(), similarities)
            }

            # Find best match
            top_score_index = np.argmax(similarities)
            confidence_score = float(similarities[top_score_index])
            winner_category = list(relationship_profiles.keys())[top_score_index]

            # Extract best supporting sentence
            evidence_sentence = self._extract_best_evidence(
                context_text, profile_embeddings[top_score_index]
            )

            logger.info(f"Classification: {winner_category} (confidence: {confidence_score:.3f})")

            return AnalysisResult(
                category=winner_category,
                confidence=round(confidence_score, 4),
                evidence=evidence_sentence,
                context_chunk=context_text,
                all_scores={k: round(v, 4) for k, v in all_scores.items()}
            )

        except Exception as e:
            logger.error(f"Error in semantic analysis: {e}")
            return AnalysisResult(
                category="Error",
                confidence=0.0,
                evidence=f"Analysis failed: {str(e)}",
                context_chunk=context_text,
                all_scores={}
            )

    def _extract_best_evidence(self, context_text: str, winning_profile_embedding) -> str:
        """Extract the sentence that best supports the classification"""
        try:
            context_sentences = [sent.text.strip() for sent in self.nlp(context_text).sents]
            if not context_sentences:
                return context_text[:200] + "..." if len(context_text) > 200 else context_text

            sentence_embeddings = self.semantic_model.encode(context_sentences)
            evidence_similarities = util.cos_sim(winning_profile_embedding, sentence_embeddings)[0]
            best_sentence_index = np.argmax(evidence_similarities)

            return context_sentences[best_sentence_index]
        except Exception as e:
            logger.warning(f"Error extracting evidence: {e}")
            return context_text[:200] + "..." if len(context_text) > 200 else context_text

    def analyze_company_relationship(self, text_content: str, company_name: str,
                                     keyword: str, **kwargs) -> AnalysisResult:
        """
        Complete analysis pipeline for a company-technology relationship

        Args:
            text_content: Raw text content to analyze
            company_name: Name of the company
            keyword: Technology/service keyword
            **kwargs: Additional parameters for context isolation

        Returns:
            AnalysisResult object with complete analysis
        """
        logger.info(f"Analyzing relationship between {company_name} and {keyword}")

        # Step 1: Isolate relevant context
        additional_keywords = kwargs.get('additional_keywords', [])
        if keyword.upper() == 'AWS':
            additional_keywords.append('Amazon Web Services')

        isolated_chunk = self.isolate_context(
            text_content,
            keyword,
            sentences_before=kwargs.get('sentences_before', 2),
            sentences_after=kwargs.get('sentences_after', 2),
            additional_keywords=additional_keywords
        )

        if not isolated_chunk:
            return AnalysisResult(
                category="Not Found",
                confidence=0.0,
                evidence=f"Keyword '{keyword}' not found in text.",
                context_chunk="",
                all_scores={}
            )

        # Step 2: Perform semantic analysis
        return self.analyze_relationship_semantically(isolated_chunk, company_name, keyword)

    def print_analysis_report(self, result: AnalysisResult, include_context: bool = True):
        """Print a formatted analysis report"""
        print("=" * 60)
        print("COMPANY-TECHNOLOGY RELATIONSHIP ANALYSIS")
        print("=" * 60)

        if include_context and result.context_chunk:
            print("\n--- EXTRACTED CONTEXT ---")
            print(result.context_chunk)
            print("\n" + "-" * 40)

        print(f"\nPREDICTED CATEGORY: {result.category}")
        print(f"CONFIDENCE SCORE:   {result.confidence:.2%}")
        print(f"SUPPORTING EVIDENCE: \"{result.evidence}\"")

        if result.all_scores:
            print(f"\nALL CATEGORY SCORES:")
            for category, score in sorted(result.all_scores.items(), key=lambda x: x[1], reverse=True):
                print(f"  {category:<25} {score:.3f} ({score:.1%})")

        print("=" * 60)


if __name__ == "__main__":
    analyzer = RelationshipAnalyzer()

    company_name = "Birlasoft"
    keyword = "AWS"
    url = "https://www.birlasoft.com/services/enterprise-products/aws"

    import csv
    path = "All_yes.csv"
    with open(path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row
        for row in reader:
            company_name = row[0]
            keyword = row[1]
            url = row[2]
            logger.info(f"Processing {company_name} for {keyword} from {url}")

    output_data = []


    from prime_normal import *

    sample_content = html(url, keyword)

        # Perform analysis
    result = analyzer.analyze_company_relationship(sample_content, company_name, keyword)

    # Print report
    analyzer.print_analysis_report(result)

    #
    try:
        # Assuming html() function is defined elsewhere to fetch content
        # For demonstration, let's use a placeholder or a mock if actual fetching is not desired
        # from your_web_scraper_module import html
        # For now, let's assume html returns some text or is mocked
        from prime_normal import html # Ensure this import is correct for your setup
        sample_content = html(url, keyword)

        if not sample_content:
            logger.warning(f"Could not retrieve content for {url}. Skipping analysis for this row.")
            result = AnalysisResult(
                category="Content Not Found",
                confidence=0.0,
                evidence="Failed to retrieve web page content.",
                context_chunk="",
                all_scores={}
            )
        else:
            # Perform analysis
            result = analyzer.analyze_company_relationship(sample_content, company_name, keyword)

        # Store results
        output_data.append({
            "company_name": company_name,
            "keyword": keyword,
            "url": url,
            "predicted_category": result.category,
            "confidence": result.confidence,
            "evidence": result.evidence,
            "context_chunk": result.context_chunk,
            "all_scores": str(result.all_scores) # Convert dict to string for CSV
        })

        # Optionally print report for each analysis
        analyzer.print_analysis_report(result)

    except Exception as e:
        logger.error(f"Error processing row for {company_name}, {keyword}, {url}: {e}")
        output_data.append({
            "company_name": company_name,
            "keyword": keyword,
            "url": url,
            "predicted_category": "Error",
            "confidence": 0.0,
            "evidence": f"Error during analysis: {e}",
            "context_chunk": "",
        })