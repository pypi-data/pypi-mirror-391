"""
Response Quality Gate - Assess Before Sending
Ensures every response meets quality standards

This is the "reflection" step that Claude/Cursor has but this agent was missing
"""

import re
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QualityAssessment:
    """Results of quality assessment"""
    overall_score: float  # 0.0-1.0
    should_retry: bool    # True if quality too low
    issues: List[str]     # Problems found
    suggestions: List[str]  # How to improve
    strengths: List[str]  # What's good
    category_scores: Dict[str, float]  # Detailed scores


class ResponseQualityGate:
    """
    Gate-keeper for response quality
    Assesses responses before sending to ensure they meet standards

    Standards:
    1. Clarity - Is it easy to understand?
    2. Completeness - Does it answer the question?
    3. Structure - Is it scannable?
    4. Appropriateness - Right tone and level?
    5. Safety - No technical errors exposed?
    """

    # Minimum acceptable quality score
    MIN_ACCEPTABLE_SCORE = 0.6  # Below this, we should retry

    # Weights for different aspects
    WEIGHTS = {
        'clarity': 0.25,
        'completeness': 0.30,
        'structure': 0.20,
        'appropriateness': 0.15,
        'safety': 0.10
    }

    @classmethod
    def assess(
        cls,
        response: str,
        original_query: str,
        context: Dict[str, Any]
    ) -> QualityAssessment:
        """
        Comprehensive quality assessment

        Returns assessment with scores, issues, and suggestions
        """
        issues = []
        suggestions = []
        strengths = []
        scores = {}

        # 1. Clarity - Is it understandable?
        scores['clarity'] = cls._assess_clarity(response, issues, suggestions, strengths)

        # 2. Completeness - Does it answer the question?
        scores['completeness'] = cls._assess_completeness(
            response, original_query, context, issues, suggestions, strengths
        )

        # 3. Structure - Is it scannable?
        scores['structure'] = cls._assess_structure(response, issues, suggestions, strengths)

        # 4. Appropriateness - Right tone/level?
        scores['appropriateness'] = cls._assess_appropriateness(
            response, original_query, issues, suggestions, strengths
        )

        # 5. Safety - No technical leakage?
        scores['safety'] = cls._assess_safety(response, issues, suggestions, strengths)

        # Calculate overall score
        overall_score = sum(scores[k] * cls.WEIGHTS[k] for k in cls.WEIGHTS)

        # Determine if we should retry
        should_retry = overall_score < cls.MIN_ACCEPTABLE_SCORE

        return QualityAssessment(
            overall_score=overall_score,
            should_retry=should_retry,
            issues=issues,
            suggestions=suggestions,
            strengths=strengths,
            category_scores=scores
        )

    @classmethod
    def _assess_clarity(
        cls,
        response: str,
        issues: List[str],
        suggestions: List[str],
        strengths: List[str]
    ) -> float:
        """Assess: Is the response clear and easy to understand?"""
        score = 1.0

        # Check for excessive hedging/uncertainty
        hedge_words = ['might', 'could', 'possibly', 'perhaps', 'maybe', 'probably']
        hedge_count = sum(1 for word in hedge_words if f' {word} ' in response.lower())

        if hedge_count > 4:
            score -= 0.2
            issues.append(f"Too many uncertain words ({hedge_count})")
            suggestions.append("Be more definitive where possible")

        # Check for run-on sentences
        sentences = re.split(r'[.!?]+', response)
        long_sentences = [s for s in sentences if len(s.split()) > 40]

        if len(long_sentences) > 2:
            score -= 0.15
            issues.append("Has overly long sentences")
            suggestions.append("Break up long sentences for clarity")

        # Check for jargon without explanation
        jargon_terms = [
            'api', 'json', 'http', 'ssl', 'tls', 'tcp', 'latency',
            'throughput', 'endpoint', 'payload', 'schema'
        ]
        jargon_found = [term for term in jargon_terms if term in response.lower()]

        if len(jargon_found) > 3:
            score -= 0.2
            issues.append(f"Contains unexplained jargon: {', '.join(jargon_found[:3])}")
            suggestions.append("Explain technical terms or use simpler language")

        # Positive signals
        if any(marker in response for marker in ['•', '- ', '**', '__']):
            strengths.append("Uses formatting for clarity")
            score = min(1.0, score + 0.1)

        return max(0.0, score)

    @classmethod
    def _assess_completeness(
        cls,
        response: str,
        query: str,
        context: Dict[str, Any],
        issues: List[str],
        suggestions: List[str],
        strengths: List[str]
    ) -> float:
        """Assess: Does the response actually answer the question?"""
        score = 0.7  # Start with assumption it's mostly complete

        query_lower = query.lower()
        response_lower = response.lower()

        # Check for deflection without attempt
        deflection_phrases = [
            "i don't have access",
            "i can't help",
            "i'm not sure",
            "i don't know"
        ]

        has_deflection = any(phrase in response_lower for phrase in deflection_phrases)

        if has_deflection:
            # Deflection is OK if response offers alternatives
            offers_alternative = any(word in response_lower for word in ['try', 'instead', 'alternatively', 'you could'])

            if not offers_alternative:
                score -= 0.3
                issues.append("Deflects without offering alternatives")
                suggestions.append("Suggest what the user can do instead")
            else:
                strengths.append("Deflects gracefully with alternatives")

        # Check if response is too brief for complex query
        query_complexity = len(query.split())
        response_length = len(response.split())

        if query_complexity > 15 and response_length < 30:
            score -= 0.2
            issues.append("Response too brief for complex query")
            suggestions.append("Provide more detailed explanation")

        # Check if response addresses key terms from query
        # Extract important words from query (not stop words)
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where', 'who'}
        query_keywords = [
            word.lower().strip('?.,!')
            for word in query.split()
            if len(word) > 3 and word.lower() not in stop_words
        ]

        # Check how many keywords are addressed
        if query_keywords:
            addressed = sum(1 for kw in query_keywords if kw in response_lower)
            coverage = addressed / len(query_keywords)

            if coverage < 0.3:
                score -= 0.25
                issues.append("Doesn't address key terms from query")
                suggestions.append(f"Address these terms: {', '.join(query_keywords[:3])}")
            elif coverage > 0.7:
                strengths.append("Addresses key terms from query")

        # Positive: Provides specific information
        has_specifics = (
            any(char.isdigit() for char in response) or  # Numbers
            '/' in response or  # Paths
            bool(re.search(r'\w+\.\w+', response))  # File extensions or domains
        )

        if has_specifics:
            strengths.append("Provides specific information")
            score = min(1.0, score + 0.1)

        return max(0.0, score)

    @classmethod
    def _assess_structure(
        cls,
        response: str,
        issues: List[str],
        suggestions: List[str],
        strengths: List[str]
    ) -> float:
        """Assess: Is the response well-structured and scannable?"""
        score = 0.5  # Neutral start

        # Good structure indicators
        has_bullets = ('•' in response or
                      re.search(r'^\s*[-*]\s', response, re.MULTILINE) or
                      re.search(r'^\s*\d+\.\s', response, re.MULTILINE))

        has_paragraphs = '\n\n' in response or response.count('\n') >= 2

        has_emphasis = '**' in response or '__' in response

        # Score based on structure elements
        if has_bullets:
            score += 0.2
            strengths.append("Uses bullets/lists for structure")

        if has_paragraphs:
            score += 0.15
            strengths.append("Breaks into readable paragraphs")

        if has_emphasis:
            score += 0.15
            strengths.append("Uses emphasis for key points")

        # Negative: Wall of text
        if not has_paragraphs and len(response) > 200:
            score -= 0.25
            issues.append("Wall of text - hard to scan")
            suggestions.append("Break into paragraphs or use bullets")

        # Negative: Lines too long
        lines = response.split('\n')
        max_line_length = max(len(line) for line in lines) if lines else 0

        if max_line_length > 200:
            score -= 0.2
            issues.append("Very long lines - hard to scan")
            suggestions.append("Break up long lines")

        # Check if it starts well
        if response and response[0].isupper():
            strengths.append("Starts with proper capitalization")
        else:
            score -= 0.1
            issues.append("Doesn't start with capital letter")

        return min(1.0, max(0.0, score))

    @classmethod
    def _assess_appropriateness(
        cls,
        response: str,
        query: str,
        issues: List[str],
        suggestions: List[str],
        strengths: List[str]
    ) -> float:
        """Assess: Is the tone and level appropriate for the query?"""
        score = 1.0

        query_lower = query.lower()
        response_lower = response.lower()

        # Check tone matches query
        # Simple/casual query should get simple/casual response
        is_casual_query = any(word in query_lower for word in ['hey', 'hi', 'hello', 'thanks'])

        if is_casual_query:
            # Response should be brief and friendly
            if len(response.split()) > 50:
                score -= 0.2
                issues.append("Too verbose for casual query")
                suggestions.append("Keep casual responses brief")

        # Technical query should get detailed response
        is_technical_query = any(word in query_lower for word in ['function', 'class', 'code', 'bug', 'error'])

        if is_technical_query:
            # Response should have details
            if len(response.split()) < 30:
                score -= 0.15
                issues.append("Too brief for technical query")
                suggestions.append("Provide more technical detail")

        # Check for inappropriate phrasing
        inappropriate_phrases = [
            "i think you're confused",
            "that's wrong",
            "you should know",
            "obviously",
            "clearly you"
        ]

        for phrase in inappropriate_phrases:
            if phrase in response_lower:
                score -= 0.3
                issues.append(f"Inappropriate phrasing: '{phrase}'")
                suggestions.append("Be more respectful and helpful")

        # Check for overly apologetic
        apology_count = response_lower.count("sorry") + response_lower.count("apolog")

        if apology_count > 2:
            score -= 0.1
            issues.append("Too apologetic")
            suggestions.append("Be helpful without excessive apologies")

        return max(0.0, score)

    @classmethod
    def _assess_safety(
        cls,
        response: str,
        issues: List[str],
        suggestions: List[str],
        strengths: List[str]
    ) -> float:
        """Assess: Are technical errors hidden from user?"""
        score = 1.0

        # Technical error patterns that should NEVER appear
        forbidden_patterns = [
            ('traceback', 'Contains stack trace'),
            ('exception:', 'Shows exception'),
            ('error:', 'Shows raw error'),
            ('tls_error', 'Shows TLS error'),
            ('certificate_verify_failed', 'Shows certificate error'),
            ('upstream connect error', 'Shows connection error'),
            ('api call failed', 'Shows API error'),
            ('⚠️ i couldn\'t finish', 'Shows internal error message')
        ]

        response_lower = response.lower()

        for pattern, description in forbidden_patterns:
            if pattern in response_lower:
                score = 0.0  # Immediate fail
                issues.append(f"CRITICAL: {description}")
                suggestions.append("Replace with user-friendly error message")
                break

        if score == 1.0:
            strengths.append("No technical errors exposed")

        return score

    @classmethod
    def improve_response(
        cls,
        response: str,
        assessment: QualityAssessment,
        query: str
    ) -> str:
        """
        Apply automatic improvements based on assessment

        This can fix some issues without LLM call:
        - Add structure (bullets)
        - Fix capitalization
        - Remove technical errors
        - Trim excessive length
        """
        improved = response

        # Fix: No paragraphs (add line breaks at sentence boundaries)
        if "Wall of text" in str(assessment.issues):
            sentences = re.split(r'([.!?]+)', improved)
            chunks = []
            for i in range(0, len(sentences), 4):  # Group ~2 sentences
                chunk = ''.join(sentences[i:i+4])
                if chunk.strip():
                    chunks.append(chunk.strip())
            improved = '\n\n'.join(chunks)

        # Fix: Doesn't start with capital
        if improved and not improved[0].isupper():
            improved = improved[0].upper() + improved[1:]

        # Fix: Technical errors exposed (try to clean)
        if "technical errors exposed" in ' '.join(assessment.issues).lower():
            # Remove lines with technical errors
            forbidden_terms = ['traceback', 'exception:', 'error:', 'tls_error', 'certificate']
            lines = improved.split('\n')
            cleaned_lines = [
                line for line in lines
                if not any(term in line.lower() for term in forbidden_terms)
            ]
            improved = '\n'.join(cleaned_lines)

            # If we removed too much, add generic message
            if len(improved.strip()) < 20:
                improved = "I encountered an issue while processing that. Could you try rephrasing?"

        return improved


def assess_response_quality(
    response: str,
    query: str,
    context: Dict[str, Any] = None
) -> QualityAssessment:
    """Convenience function for quality assessment"""
    return ResponseQualityGate.assess(response, query, context or {})
