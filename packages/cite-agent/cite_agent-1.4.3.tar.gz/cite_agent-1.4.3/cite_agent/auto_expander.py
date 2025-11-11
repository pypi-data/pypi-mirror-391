"""
Automatic Response Expansion

When agent returns minimal info, automatically fetch and show more detail

Examples:
- List of files → Show preview of main file
- List of papers → Show abstracts
- Data query → Show breakdown/visualization
"""

import logging
import re
from typing import Dict, Any, Optional

from .proactive_boundaries import ProactiveBoundaries

logger = logging.getLogger(__name__)


class AutoExpander:
    """
    Automatically expands minimal responses with useful detail

    PHILOSOPHY: Don't make user ask twice for obvious next step
    """

    @classmethod
    def should_expand(cls, response: str, query: str, context: Dict[str, Any]) -> bool:
        """
        Check if response should be automatically expanded

        Returns True if response is minimal and expansion would be useful
        """
        expansion_info = ProactiveBoundaries.get_auto_expansion_for_query(query, response)
        return expansion_info['should_expand']

    @classmethod
    def expand(cls, response: str, query: str, context: Dict[str, Any]) -> str:
        """
        Detect when expansion is needed and log it

        NOTE: With our action-first prompt changes, the LLM should already
        be providing expanded responses. This function mainly serves as a
        quality check - if it detects expansion is needed, it means the
        LLM didn't follow the action-first guidelines.

        In production, this could trigger a second LLM call to expand,
        but for now we just log the issue.
        """
        expansion_info = ProactiveBoundaries.get_auto_expansion_for_query(query, response)

        if not expansion_info['should_expand']:
            return response  # No expansion needed - response is already good

        # Response needs expansion - this is a problem!
        logger.warning(f"⚠️ Response needs expansion but LLM didn't provide it")
        logger.warning(f"   Reason: {expansion_info['reason']}")
        logger.warning(f"   Missing actions: {expansion_info['expansion_actions']}")
        logger.warning(f"   This suggests prompt needs improvement or LLM isn't following guidelines")

        # For now, return original response
        # In production, we could trigger a second LLM call here to expand
        return response


# Convenience function
def auto_expand(response: str, query: str, context: Dict[str, Any] = None) -> str:
    """Quick auto-expansion"""
    return AutoExpander.expand(response, query, context or {})
