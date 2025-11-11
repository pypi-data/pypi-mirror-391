"""
Response Style Enhancer - Make responses PLEASANT and STYLISH

Transforms robotic, formal responses into warm, friendly, conversational ones
Target: 0.80+ style score on all responses

Key transformations:
1. Warm greetings instead of formal ones
2. Natural language instead of robotic phrasing
3. Elegant formatting with bullets and structure
4. Anticipatory offers to help more
5. Personality and friendliness
"""

import re
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ResponseStyleEnhancer:
    """
    Enhances response style to be pleasant and stylish

    Focus areas:
    1. WARMTH - Replace cold/formal with friendly/warm
    2. NATURAL - Replace robotic with conversational
    3. ELEGANT - Add beautiful formatting
    4. ANTICIPATORY - Offer to help with next steps
    5. PERSONALITY - Make it feel like a smart friend
    """

    # Formal → Warm transformations
    GREETING_TRANSFORMS = {
        r'^Hello\.\s*How can I assist you today\?': 'Hi there! Ready to help - what can I dig into for you?',
        r'^Hello\.\s*': 'Hi! ',
        r'^Greetings\.\s*': 'Hey there! ',
        r'^Good (morning|afternoon|evening)\.\s*': 'Hi! ',
        r'How may I help you\?': 'What can I help you with?',
        r'How can I assist you\?': 'What would you like to know?',
        r'Is there anything else\?': 'Need anything else?',
    }

    # Robotic → Natural transformations
    NATURAL_TRANSFORMS = {
        r'I have analyzed': "I've looked at",
        r'I have determined': "I found",
        r'I have located': "I found",
        r'I have identified': "I see",
        r'I have processed': "I've checked",
        r'I have executed': "I ran",
        r'Processing complete': "All done",
        r'Execution successful': "Got it",
        r'Operation completed': "Done",
        r'Please note that': "Note:",
        r'It should be noted': "Keep in mind",
        r'Additionally,': "Also,",
        r'Furthermore,': "Plus,",
        r'However,': "But",
        r'Therefore,': "So",
        r'Subsequently,': "Then",
        r'You are welcome': "Happy to help! Let me know if you need anything else",
    }

    # Cold → Warm phrases
    WARM_TRANSFORMS = {
        r'You must': 'You should',
        r'You need to': "You'll want to",
        r'It is required': "You'll need to",
        r'It is necessary': "You'll want to",
        r'Error:': 'Hmm,',
        r'Failed to': "Couldn't",
        r'Unable to': "Can't",
    }

    # Add anticipatory phrases based on context
    ANTICIPATORY_PATTERNS = [
        (r'(I found|Here are|Here\'s)\s+(\d+)\s+(files?|items?|results?)',
         lambda m: f"{m.group(0)}\n\nWant me to show you what's in any of these?"),
        (r'(The|This)\s+(file|code|function)\s+(\w+)',
         lambda m: f"{m.group(0)}. Want me to walk through how it works?"),
        (r'(Here\'s|Here is)\s+(what|how|the)',
         lambda m: f"{m.group(0)}"),  # Keep as is, will add offer at end
    ]

    @classmethod
    def enhance(cls, response: str, query: str, context: Dict[str, Any]) -> str:
        """
        Enhance response style to be pleasant and stylish

        Args:
            response: Original response
            query: User's query
            context: Context including tools, data, etc.

        Returns:
            Enhanced stylish response
        """
        if not response or len(response) < 5:
            return response

        enhanced = response

        # Step 1: Make greetings warm and friendly
        enhanced = cls._enhance_greetings(enhanced, query)

        # Step 2: Make language natural instead of robotic
        enhanced = cls._make_natural(enhanced)

        # Step 3: Add warmth
        enhanced = cls._add_warmth(enhanced)

        # Step 4: Improve formatting to be elegant
        enhanced = cls._make_elegant(enhanced, context)

        # Step 5: Add anticipatory offers
        enhanced = cls._add_anticipatory_offers(enhanced, query, context)

        # Step 6: Add personality touches
        enhanced = cls._add_personality(enhanced, query)

        return enhanced

    @classmethod
    def _enhance_greetings(cls, response: str, query: str) -> str:
        """Replace formal greetings with warm friendly ones"""
        # Check if query is a greeting
        query_lower = query.lower().strip()
        is_greeting = any(g in query_lower for g in ['hi', 'hello', 'hey', 'greetings'])

        if is_greeting and len(query_lower) < 20:
            # Replace formal greeting responses
            for pattern, replacement in cls.GREETING_TRANSFORMS.items():
                response = re.sub(pattern, replacement, response, flags=re.IGNORECASE)

        return response

    @classmethod
    def _make_natural(cls, response: str) -> str:
        """Replace robotic phrasing with natural conversation"""
        enhanced = response

        for pattern, replacement in cls.NATURAL_TRANSFORMS.items():
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)

        return enhanced

    @classmethod
    def _add_warmth(cls, response: str) -> str:
        """Replace cold/formal phrases with warm ones"""
        enhanced = response

        for pattern, replacement in cls.WARM_TRANSFORMS.items():
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)

        return enhanced

    @classmethod
    def _make_elegant(cls, response: str, context: Dict[str, Any]) -> str:
        """
        Add elegant formatting

        - Convert plain lists to bulleted lists
        - Add proper spacing
        - Use emphasis where appropriate
        """
        # Check if response has lists that aren't bulleted
        lines = response.split('\n')

        # Detect list patterns like "file1, file2, file3"
        for i, line in enumerate(lines):
            # If line has comma-separated items (3+)
            if line.count(',') >= 2 and len(line) < 200:
                parts = [p.strip() for p in line.split(',')]

                if len(parts) >= 3:
                    # Check if these look like filenames or items
                    if any(ext in line for ext in ['.py', '.js', '.md', '.txt', '.json']) or \
                       all(len(p) < 50 for p in parts):
                        # Convert to bulleted list
                        intro = "I found these:" if i == 0 else ""
                        bulleted = '\n'.join([f"• {p}" for p in parts])
                        lines[i] = f"{intro}\n\n{bulleted}" if intro else bulleted

        enhanced = '\n'.join(lines)

        # Add proper paragraph spacing if missing
        if enhanced.count('\n\n') == 0 and len(enhanced) > 200:
            # Split into paragraphs at sentence boundaries
            sentences = re.split(r'(?<=[.!?])\s+', enhanced)
            if len(sentences) >= 3:
                # Group into 2-3 sentence paragraphs
                paragraphs = []
                current = []
                for sent in sentences:
                    current.append(sent)
                    if len(current) >= 2:
                        paragraphs.append(' '.join(current))
                        current = []
                if current:
                    paragraphs.append(' '.join(current))

                enhanced = '\n\n'.join(paragraphs)

        return enhanced

    @classmethod
    def _add_anticipatory_offers(cls, response: str, query: str, context: Dict[str, Any]) -> str:
        """
        Add anticipatory offers - BUT IN ACTION-FIRST MODE

        Instead of "Want me to X?", the agent should have ALREADY DONE X
        So we SKIP adding asking phrases in action-first mode

        DISABLED: User wants action-first, not conversation-first
        """
        # ACTION-FIRST MODE: Don't add asking phrases
        # The agent should have already done the obvious next step
        # If it didn't, that's a different problem to fix

        return response  # Return unchanged - no asking phrases added

    @classmethod
    def _add_personality(cls, response: str, query: str) -> str:
        """Add personality touches to make it feel like a smart friend"""
        # Check query sentiment
        query_lower = query.lower()

        # If user said thanks
        if any(word in query_lower for word in ['thanks', 'thank you', 'appreciate']):
            # Make response warmer
            if 'you are welcome' in response.lower() or 'you\'re welcome' in response.lower():
                response = re.sub(
                    r"you'?re? welcome\.?",
                    "Happy to help! Let me know if you need anything else.",
                    response,
                    flags=re.IGNORECASE
                )

        # If user seems excited (exclamation marks)
        if '!' in query and len(query) < 50:
            # Match energy slightly
            if not '!' in response:
                # Add one exclamation at the end if appropriate
                response = response.rstrip('.') + '!'

        # If response is very short and abrupt, make it friendlier
        if len(response) < 20 and '?' not in response:
            # Add friendly suffix
            if not any(word in response.lower() for word in ['happy', 'glad', 'sure']):
                response += " Let me know if you need anything else!"

        return response


def enhance_style(response: str, query: str, context: Dict[str, Any] = None) -> str:
    """Convenience function to enhance response style"""
    return ResponseStyleEnhancer.enhance(response, query, context or {})
