"""
Response Enhancer - Polish responses to 0.80+ quality
Takes good responses and makes them great

Target: Every response should score 0.80+ on quality metrics
"""

import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ResponseEnhancer:
    """
    Enhances responses to maximize quality scores

    Focus areas:
    1. Completeness - Address all key terms from query
    2. Structure - Add bullets, headers, emphasis
    3. Clarity - Make more direct and specific
    4. Scannability - Break up walls of text
    """

    @classmethod
    def enhance(cls, response: str, query: str, context: Dict[str, Any]) -> str:
        """
        Enhance a response to maximize quality

        Args:
            response: Original response
            query: User's query
            context: Context including tools, data, etc.

        Returns:
            Enhanced response
        """
        if not response or len(response) < 10:
            return response

        enhanced = response

        # Enhancement 1: Add structure if missing
        enhanced = cls._add_structure(enhanced, query)

        # Enhancement 2: Make more complete by addressing key terms
        enhanced = cls._improve_completeness(enhanced, query, context)

        # Enhancement 3: Improve clarity
        enhanced = cls._improve_clarity(enhanced)

        # Enhancement 4: Make more scannable
        enhanced = cls._improve_scannability(enhanced)

        # Enhancement 5: Add specificity
        enhanced = cls._add_specificity(enhanced, context)

        return enhanced

    @classmethod
    def _add_structure(cls, response: str, query: str) -> str:
        """Add structure if response is unstructured"""
        # Check if response lacks structure
        has_bullets = '•' in response or '- ' in response
        has_emphasis = '**' in response
        has_paragraphs = '\n\n' in response

        if has_bullets and has_emphasis:
            return response  # Already well-structured

        lines = response.split('\n')

        # If it's a short response (< 100 words), structure is less important
        if len(response.split()) < 100:
            return response

        # If it's listing things but not using bullets, add them
        if len(lines) > 1 and not has_bullets:
            # Check if lines look like a list
            list_indicators = ['1.', '2.', 'first', 'second', 'also', 'additionally']
            looks_like_list = sum(1 for line in lines if any(ind in line.lower() for ind in list_indicators))

            if looks_like_list >= 2:
                # Convert to bulleted list
                enhanced_lines = []
                for line in lines:
                    stripped = line.strip()
                    if stripped and not stripped.endswith(':'):
                        if not stripped.startswith('•'):
                            enhanced_lines.append(f"• {stripped}")
                        else:
                            enhanced_lines.append(stripped)
                    else:
                        enhanced_lines.append(stripped)

                return '\n'.join(enhanced_lines)

        return response

    @classmethod
    def _improve_completeness(cls, response: str, query: str, context: Dict[str, Any]) -> str:
        """Make response more complete by addressing key query terms"""
        # Extract key terms from query
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where', 'who', 'which', 'do', 'does', 'did', 'can', 'could', 'would', 'should', 'me', 'my', 'you', 'your', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'from'}

        query_terms = [
            word.lower().strip('?.,!:;')
            for word in query.split()
            if len(word) > 3 and word.lower() not in stop_words
        ]

        if not query_terms:
            return response

        response_lower = response.lower()

        # Find terms that aren't addressed
        missing_terms = [term for term in query_terms if term not in response_lower]

        # If we're missing major terms, try to add context
        if len(missing_terms) > len(query_terms) * 0.5:  # Missing > 50% of key terms
            # Check if we have context that addresses these terms
            if context.get('api_results') or context.get('tools_used'):
                # Add note about what was checked
                tools_used = context.get('tools_used', [])

                if 'shell_execution' in tools_used:
                    # File/directory query
                    if any(term in query.lower() for term in ['file', 'directory', 'folder']):
                        if 'file' in missing_terms or 'directory' in missing_terms:
                            # Make it clear we checked files/directories
                            response = response.replace(
                                "We're in",
                                "I checked the current directory. We're in"
                            )

        return response

    @classmethod
    def _improve_clarity(cls, response: str) -> str:
        """Make response more clear and direct"""
        # Remove excessive hedging
        hedge_phrases = {
            'i think maybe': 'probably',
            'i believe that possibly': 'likely',
            'it seems like perhaps': 'it appears',
            'i might suggest': 'i suggest',
            'it could potentially be': 'it may be',
        }

        enhanced = response
        for wordy, concise in hedge_phrases.items():
            enhanced = enhanced.replace(wordy, concise)

        # Remove filler phrases at start
        filler_starters = [
            'Well, ',
            'So, ',
            'Basically, ',
            'Actually, ',
            'You know, ',
        ]

        for filler in filler_starters:
            if enhanced.startswith(filler):
                enhanced = enhanced[len(filler):]
                # Capitalize first letter
                if enhanced:
                    enhanced = enhanced[0].upper() + enhanced[1:]

        return enhanced

    @classmethod
    def _improve_scannability(cls, response: str) -> str:
        """Make response more scannable"""
        # Break up very long paragraphs
        if '\n\n' not in response and len(response) > 300:
            # Split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', response)

            if len(sentences) >= 4:
                # Group into paragraphs of 2-3 sentences
                paragraphs = []
                current = []

                for sent in sentences:
                    current.append(sent)
                    if len(current) >= 2:
                        paragraphs.append(' '.join(current))
                        current = []

                if current:
                    paragraphs.append(' '.join(current))

                if len(paragraphs) > 1:
                    return '\n\n'.join(paragraphs)

        # Check line length - break up super long lines
        lines = response.split('\n')
        enhanced_lines = []

        for line in lines:
            if len(line) > 200 and ',' in line:
                # Split on commas for readability
                parts = line.split(', ')
                if len(parts) >= 3:
                    # Make it a bulleted list
                    enhanced_lines.append(parts[0] + ':')
                    for part in parts[1:]:
                        enhanced_lines.append(f"  • {part.strip()}")
                else:
                    enhanced_lines.append(line)
            else:
                enhanced_lines.append(line)

        return '\n'.join(enhanced_lines)

    @classmethod
    def _add_specificity(cls, response: str, context: Dict[str, Any]) -> str:
        """Add specific details from context if response is vague"""
        # Check if response is vague
        vague_phrases = [
            'some files',
            'a few',
            'several',
            'multiple',
            'various',
        ]

        response_lower = response.lower()
        is_vague = any(phrase in response_lower for phrase in vague_phrases)

        if not is_vague:
            return response

        # Try to add specifics from context
        api_results = context.get('api_results', {})

        # If we have file data, be specific about count
        if 'files' in response_lower and isinstance(api_results, dict):
            # Look for file lists in results
            for key, value in api_results.items():
                if isinstance(value, (list, tuple)) and len(value) > 0:
                    # Found a list - add count
                    count = len(value)
                    response = response.replace('some files', f'{count} files')
                    response = response.replace('a few files', f'{count} files')
                    response = response.replace('several files', f'{count} files')
                    break

        return response


def enhance_response(response: str, query: str, context: Dict[str, Any] = None) -> str:
    """Convenience function to enhance a response"""
    return ResponseEnhancer.enhance(response, query, context or {})
