"""
Confidence Calibration - Know When Uncertain
Assesses confidence in responses and adds appropriate caveats

This prevents overconfident wrong answers
"""

import logging
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ConfidenceAssessment:
    """Result of confidence assessment"""
    confidence_score: float  # 0.0-1.0
    confidence_level: str  # "high", "medium", "low"
    should_add_caveat: bool
    caveat_text: Optional[str]
    factors: Dict[str, float]  # What contributed to confidence
    reasoning: str


class ConfidenceCalibrator:
    """
    Assesses confidence in responses

    Factors that affect confidence:
    1. Data quality (Do we have good data?)
    2. Query clarity (Is the question clear?)
    3. Answer completeness (Did we answer fully?)
    4. Source reliability (Are sources trustworthy?)
    5. Response consistency (Does answer make sense?)
    """

    # Confidence thresholds
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.6
    LOW_CONFIDENCE = 0.4

    @classmethod
    def assess_confidence(
        cls,
        response: str,
        query: str,
        context: Dict[str, Any]
    ) -> ConfidenceAssessment:
        """
        Assess confidence in a response

        Args:
            response: The generated response
            query: Original user query
            context: Context including tools used, data sources, etc.

        Returns:
            Confidence assessment with score and caveat if needed
        """
        factors = {}

        # Factor 1: Data quality (40% weight)
        factors['data_quality'] = cls._assess_data_quality(context)

        # Factor 2: Query clarity (20% weight)
        factors['query_clarity'] = cls._assess_query_clarity(query)

        # Factor 3: Answer completeness (25% weight)
        factors['answer_completeness'] = cls._assess_completeness(response, query)

        # Factor 4: Source reliability (10% weight)
        factors['source_reliability'] = cls._assess_source_reliability(context)

        # Factor 5: Response consistency (5% weight)
        factors['response_consistency'] = cls._assess_consistency(response)

        # Calculate weighted confidence score
        weights = {
            'data_quality': 0.40,
            'query_clarity': 0.20,
            'answer_completeness': 0.25,
            'source_reliability': 0.10,
            'response_consistency': 0.05
        }

        confidence_score = sum(factors[k] * weights[k] for k in weights)

        # Determine confidence level
        if confidence_score >= cls.HIGH_CONFIDENCE:
            confidence_level = "high"
        elif confidence_score >= cls.MEDIUM_CONFIDENCE:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        # Determine if we should add a caveat
        should_add_caveat = confidence_score < cls.MEDIUM_CONFIDENCE

        # Generate caveat text if needed
        caveat_text = None
        if should_add_caveat:
            caveat_text = cls._generate_caveat(confidence_score, factors, context)

        # Generate reasoning
        reasoning = cls._explain_confidence(confidence_score, factors)

        return ConfidenceAssessment(
            confidence_score=confidence_score,
            confidence_level=confidence_level,
            should_add_caveat=should_add_caveat,
            caveat_text=caveat_text,
            factors=factors,
            reasoning=reasoning
        )

    @classmethod
    def _assess_data_quality(cls, context: Dict[str, Any]) -> float:
        """
        Assess quality of data used

        High quality: Multiple reliable sources, recent data
        Low quality: No sources, old data, incomplete data
        """
        score = 0.5  # Neutral start

        tools_used = context.get('tools_used', [])
        api_results = context.get('api_results', {})

        # Check if we have data sources
        has_data = bool(api_results) or bool(tools_used)

        if not has_data:
            return 0.3  # Low confidence if no data

        # Check quality of data sources
        reliable_sources = ['archive_api', 'finsight_api', 'shell_execution']
        unreliable_sources = ['web_search']

        reliable_count = sum(1 for tool in tools_used if tool in reliable_sources)
        unreliable_count = sum(1 for tool in tools_used if tool in unreliable_sources)

        if reliable_count > 0:
            score += 0.3

        if unreliable_count > 0 and reliable_count == 0:
            score -= 0.2

        # Check for empty results
        if api_results:
            # Check if results are empty
            for key, value in api_results.items():
                if isinstance(value, dict) and value.get('results') == []:
                    score -= 0.4  # Major penalty for empty results
                elif isinstance(value, list) and not value:
                    score -= 0.3

        return min(1.0, max(0.0, score))

    @classmethod
    def _assess_query_clarity(cls, query: str) -> float:
        """
        Assess how clear the query is

        Clear query: Specific, unambiguous
        Unclear query: Vague, pronouns without context, too short
        """
        score = 1.0  # Start optimistic

        # Too short is often ambiguous
        word_count = len(query.split())
        if word_count < 3:
            score -= 0.3

        # Pronouns without context
        pronouns = ['it', 'that', 'those', 'this', 'them']
        has_pronoun = any(pronoun in query.lower().split() for pronoun in pronouns)

        if has_pronoun and word_count < 8:
            score -= 0.2

        # Very vague terms
        vague_terms = ['something', 'stuff', 'things', 'anything']
        if any(term in query.lower() for term in vague_terms):
            score -= 0.25

        # Question marks without clear question
        if '?' in query and word_count < 4:
            score -= 0.15

        return min(1.0, max(0.0, score))

    @classmethod
    def _assess_completeness(cls, response: str, query: str) -> float:
        """
        Assess if response fully answers the query

        Complete: Addresses all aspects of query
        Incomplete: Partial answer, deflects, says "I don't know"
        """
        score = 0.7  # Assume mostly complete

        response_lower = response.lower()

        # Check for deflection
        deflection_phrases = [
            "i don't know",
            "i'm not sure",
            "i don't have",
            "i can't",
            "unclear"
        ]

        if any(phrase in response_lower for phrase in deflection_phrases):
            score -= 0.4

        # Check response length relative to query complexity
        query_words = len(query.split())
        response_words = len(response.split())

        if query_words > 10 and response_words < 30:
            score -= 0.2  # Too brief for complex query

        # Check if response addresses key terms from query
        query_terms = set(query.lower().split())
        response_terms = set(response_lower.split())

        # Remove stop words
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why'}
        query_terms -= stop_words

        if query_terms:
            overlap = len(query_terms & response_terms) / len(query_terms)
            if overlap < 0.3:
                score -= 0.25

        return min(1.0, max(0.0, score))

    @classmethod
    def _assess_source_reliability(cls, context: Dict[str, Any]) -> float:
        """
        Assess reliability of sources used

        Reliable: Official APIs, verified databases
        Unreliable: Web scraping, unverified sources
        """
        tools_used = context.get('tools_used', [])

        if not tools_used:
            return 0.5  # Neutral if no tools used

        # Reliability scores for different tools
        reliability_map = {
            'archive_api': 0.95,  # Academic papers - very reliable
            'finsight_api': 0.90,  # SEC filings - very reliable
            'shell_execution': 0.85,  # Direct file access - reliable
            'web_search': 0.60,  # Web - less reliable
            'fallback': 0.30  # Fallback responses - low reliability
        }

        # Average reliability of tools used
        reliabilities = [reliability_map.get(tool, 0.5) for tool in tools_used]
        avg_reliability = sum(reliabilities) / len(reliabilities) if reliabilities else 0.5

        return avg_reliability

    @classmethod
    def _assess_consistency(cls, response: str) -> float:
        """
        Assess internal consistency of response

        Consistent: No contradictions, logical flow
        Inconsistent: Contradictions, illogical statements
        """
        score = 1.0  # Assume consistent

        # Check for hedge words that indicate uncertainty
        hedge_words = ['maybe', 'possibly', 'might', 'could', 'perhaps']
        hedge_count = sum(1 for word in hedge_words if f' {word} ' in response.lower())

        if hedge_count > 3:
            score -= 0.2  # Too many hedges suggests uncertainty

        # Check for contradictions
        contradiction_patterns = [
            ('but ', 'however '),
            ('although ', 'though '),
            ('not ', 'no ')
        ]

        contradiction_count = sum(
            1 for pattern_words in contradiction_patterns
            if all(word in response.lower() for word in pattern_words)
        )

        if contradiction_count > 2:
            score -= 0.15

        return min(1.0, max(0.0, score))

    @classmethod
    def _generate_caveat(cls, confidence_score: float, factors: Dict[str, float], context: Dict[str, Any]) -> str:
        """
        Generate appropriate caveat text based on confidence factors
        """
        # Identify the weakest factor
        weakest_factor = min(factors.items(), key=lambda x: x[1])
        factor_name, factor_score = weakest_factor

        caveats = {
            'data_quality': "Based on limited data available, ",
            'query_clarity': "I interpreted your question to mean: ",
            'answer_completeness': "Based on what I could find, ",
            'source_reliability': "According to available sources, ",
            'response_consistency': "To the best of my understanding, "
        }

        caveat_prefix = caveats.get(factor_name, "Based on available information, ")

        # Add severity based on overall confidence
        if confidence_score < cls.LOW_CONFIDENCE:
            caveat_prefix = "⚠️ Low confidence: " + caveat_prefix

        return caveat_prefix

    @classmethod
    def _explain_confidence(cls, confidence_score: float, factors: Dict[str, float]) -> str:
        """Generate explanation of confidence level"""
        level = "high" if confidence_score >= cls.HIGH_CONFIDENCE else \
                "medium" if confidence_score >= cls.MEDIUM_CONFIDENCE else "low"

        # Identify top contributing factors
        sorted_factors = sorted(factors.items(), key=lambda x: x[1], reverse=True)
        top_factor = sorted_factors[0][0]
        bottom_factor = sorted_factors[-1][0]

        reasoning = (
            f"Confidence level: {level} ({confidence_score:.2f}). "
            f"Strongest factor: {top_factor} ({factors[top_factor]:.2f}). "
            f"Weakest factor: {bottom_factor} ({factors[bottom_factor]:.2f})."
        )

        return reasoning

    @classmethod
    def add_caveat_to_response(cls, response: str, caveat: str) -> str:
        """
        Add caveat to response in a natural way

        Inserts caveat at the beginning of the response
        """
        # If response already starts with a caveat-like phrase, don't add another
        caveat_starters = ['based on', 'according to', 'to the best', 'from what']

        response_lower = response.lower()
        if any(starter in response_lower[:50] for starter in caveat_starters):
            return response  # Already has a caveat

        # Add caveat at the start
        return caveat + response[0].lower() + response[1:]


# Convenience function
def assess_and_apply_caveat(response: str, query: str, context: Dict[str, Any]) -> tuple:
    """
    Assess confidence and apply caveat if needed

    Returns:
        (final_response, confidence_assessment)
    """
    assessment = ConfidenceCalibrator.assess_confidence(response, query, context)

    final_response = response
    if assessment.should_add_caveat and assessment.caveat_text:
        final_response = ConfidenceCalibrator.add_caveat_to_response(
            response,
            assessment.caveat_text
        )

    return final_response, assessment
