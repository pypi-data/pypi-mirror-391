"""
Action-First Response Mode

Makes agent SHOW results proactively instead of just talking about them

Key principles:
1. DO the obvious next step without asking
2. SHOW data, don't just describe it
3. Less talk, more action
4. Proactive, not reactive
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class ActionFirstMode:
    """
    Transforms agent from conversation-first to action-first

    BEFORE (conversation-first):
    User: "List Python files"
    Agent: "I found 3 files. Want me to show you what's in them?"

    AFTER (action-first):
    User: "List Python files"
    Agent: [Shows list + Shows preview of main file + Shows key functions]
    """

    @classmethod
    def should_auto_expand(cls, query: str, response: str, context: Dict[str, Any]) -> bool:
        """
        Determine if agent should automatically show more detail

        Returns True if:
        - Listed files → should preview main one
        - Listed papers → should show abstracts
        - Listed code → should show key functions
        - Found data → should show sample
        """
        query_lower = query.lower()
        response_lower = response.lower()

        # If response just lists things without details, should expand
        if any(word in response_lower for word in ['found', 'here are', 'listed']):
            # Check if it's a list without details
            has_bullets = '•' in response or '\n-' in response
            is_short = len(response) < 300

            if has_bullets and is_short:
                return True

        # If listing files, should preview
        if any(word in query_lower for word in ['list', 'show', 'find']) and \
           any(word in query_lower for word in ['file', 'files', 'code']):
            return True

        # If finding papers, should show abstracts
        if 'papers' in query_lower or 'research' in query_lower:
            return True

        # If data query, should show sample
        if any(word in query_lower for word in ['data', 'revenue', 'metrics', 'stats']):
            return True

        return False

    @classmethod
    def get_auto_expansion_prompt(cls, query: str, initial_response: str, context: Dict[str, Any]) -> str:
        """
        Generate prompt for automatic expansion

        This tells the agent to SHOW more detail proactively
        """
        query_lower = query.lower()

        # File listing → preview main file
        if 'file' in query_lower and any(ext in initial_response for ext in ['.py', '.js', '.md']):
            return "Now show a preview (first 50 lines) of the most important file automatically. Don't ask - just show it."

        # Papers → show abstracts
        if 'paper' in query_lower:
            return "Now show the abstract/summary of the top 2-3 papers automatically. Don't ask - just show them."

        # Code → show key functions
        if 'code' in query_lower or 'function' in query_lower:
            return "Now show the key functions/classes in the main file automatically. Don't ask - just show them."

        # Data → show sample
        if 'data' in query_lower or 'revenue' in query_lower:
            return "Now show a sample/visualization of the data automatically. Don't ask - just show it."

        return "Show the most useful additional detail automatically without asking permission."

    @classmethod
    def remove_asking_phrases(cls, response: str) -> str:
        """
        Remove phrases that ASK instead of DO

        "Want me to..." → Just do it
        "Should I..." → Just do it
        "Would you like..." → Just do it
        """
        import re

        asking_patterns = [
            r'Want me to[^?]+\?',
            r'Should I[^?]+\?',
            r'Would you like[^?]+\?',
            r'Need me to[^?]+\?',
            r'Let me know if you want me to[^.]+\.',
            r'Let me know if you need[^.]+\.',
        ]

        cleaned = response
        for pattern in asking_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)

        # Clean up extra whitespace/newlines
        cleaned = re.sub(r'\n\n+', '\n\n', cleaned)
        cleaned = cleaned.strip()

        return cleaned

    @classmethod
    def make_action_first(cls, response: str, query: str, context: Dict[str, Any]) -> str:
        """
        Transform response to be action-first

        1. Remove asking phrases
        2. If response is just a list, it should have been auto-expanded
        3. Focus on SHOWING not TELLING
        """
        # Remove asking phrases
        action_response = cls.remove_asking_phrases(response)

        # If response is still too conversation-heavy, make it data-heavy
        if len(action_response) < 200 and not any(marker in action_response for marker in ['```', '•', '\n-']):
            # Response is short and has no data structure - flag for expansion
            logger.warning("Response is conversation-heavy, should be more action-first")

        return action_response


# Convenience function
def make_action_first(response: str, query: str, context: Dict[str, Any] = None) -> str:
    """Quick action-first transformation"""
    return ActionFirstMode.make_action_first(response, query, context or {})
