"""
Thinking Blocks - Visible Reasoning Process
Shows users the internal reasoning like Claude does

This is the "why" behind responses, not just the "what"
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ThinkingStep:
    """A single step in the reasoning process"""
    step_number: int
    thought: str
    reasoning_type: str  # analysis, planning, verification, decision
    confidence: float  # 0.0-1.0


class ThinkingBlockGenerator:
    """
    Generates visible thinking blocks to show reasoning process

    Similar to Claude's <thinking> tags, but formatted for terminal output
    """

    @classmethod
    async def generate_thinking(
        cls,
        query: str,
        context: Dict[str, Any],
        llm_client: Optional[Any] = None
    ) -> List[ThinkingStep]:
        """
        Generate thinking steps for a query

        Args:
            query: User's question
            context: Available context (tools, data, history)
            llm_client: LLM client to generate thinking (optional - can be rule-based too)

        Returns:
            List of thinking steps showing reasoning process
        """
        steps = []

        # Step 1: Understand the query
        understanding_step = cls._analyze_query(query, context)
        steps.append(understanding_step)

        # Step 2: Plan approach
        planning_step = cls._plan_approach(query, context, understanding_step)
        steps.append(planning_step)

        # Step 3: Identify what tools/data needed
        tools_step = cls._identify_tools_needed(query, context, planning_step)
        steps.append(tools_step)

        # Step 4: Consider potential issues
        issues_step = cls._consider_issues(query, context)
        if issues_step:
            steps.append(issues_step)

        return steps

    @classmethod
    def _analyze_query(cls, query: str, context: Dict[str, Any]) -> ThinkingStep:
        """Analyze what the user is really asking"""
        query_lower = query.lower()

        # Determine query type
        if any(word in query_lower for word in ['find', 'search', 'look for']):
            thought = f"User wants me to search for something. Need to determine: search where (files/papers/data)?"

        elif any(word in query_lower for word in ['list', 'show', 'what']):
            thought = f"User wants information listed. Need to figure out: what kind of listing?"

        elif any(word in query_lower for word in ['how', 'why', 'explain']):
            thought = f"User wants an explanation. Need to: understand the topic and provide clear reasoning."

        elif any(word in query_lower for word in ['compare', 'versus', 'vs']):
            thought = f"User wants a comparison. Need to: identify what's being compared and on what metric."

        elif any(word in query_lower for word in ['bug', 'error', 'fix', 'wrong']):
            thought = f"User has a problem that needs fixing. Need to: identify the issue and suggest a solution."

        else:
            thought = f"User's query is: '{query}'. Need to understand the intent first."

        return ThinkingStep(
            step_number=1,
            thought=thought,
            reasoning_type="analysis",
            confidence=0.8
        )

    @classmethod
    def _plan_approach(
        cls,
        query: str,
        context: Dict[str, Any],
        understanding: ThinkingStep
    ) -> ThinkingStep:
        """Plan how to approach answering this query"""
        query_lower = query.lower()

        # Determine best approach based on understanding
        if 'search' in understanding.thought.lower():
            # Search query
            if any(word in query_lower for word in ['paper', 'research', 'study']):
                thought = "Best approach: Use Archive API to search academic papers."

            elif any(word in query_lower for word in ['file', 'directory', 'code']):
                thought = "Best approach: Use shell commands (find/grep) to search the filesystem."

            elif any(word in query_lower for word in ['company', 'revenue', 'stock']):
                thought = "Best approach: Use FinSight API to get financial data."

            else:
                thought = "Best approach: Try web search first, fallback to file search if needed."

        elif 'list' in understanding.thought.lower():
            # Listing query
            if 'file' in query_lower or 'directory' in query_lower:
                thought = "Best approach: Execute 'ls' or 'find' command to list files."

            else:
                thought = "Best approach: Determine what needs listing, then use appropriate tool."

        elif 'comparison' in understanding.thought.lower():
            # Comparison query
            thought = "Best approach: Gather data for both items, then create comparison."

        elif 'problem' in understanding.thought.lower():
            # Debugging query
            thought = "Best approach: Read the relevant code/file, identify issue, suggest fix."

        else:
            # Generic
            thought = "Best approach: Gather necessary information, then synthesize a clear answer."

        return ThinkingStep(
            step_number=2,
            thought=thought,
            reasoning_type="planning",
            confidence=0.85
        )

    @classmethod
    def _identify_tools_needed(
        cls,
        query: str,
        context: Dict[str, Any],
        plan: ThinkingStep
    ) -> ThinkingStep:
        """Identify what tools/APIs are needed"""
        plan_lower = plan.thought.lower()

        needed_tools = []

        if 'archive api' in plan_lower:
            needed_tools.append("Archive API (for papers)")

        if 'finsight api' in plan_lower:
            needed_tools.append("FinSight API (for financial data)")

        if 'shell' in plan_lower or 'command' in plan_lower:
            needed_tools.append("Shell commands (for file operations)")

        if 'web search' in plan_lower:
            needed_tools.append("Web search")

        if needed_tools:
            tools_list = ", ".join(needed_tools)
            thought = f"Tools I'll need: {tools_list}"
        else:
            thought = "I can answer this directly without external tools."

        return ThinkingStep(
            step_number=3,
            thought=thought,
            reasoning_type="planning",
            confidence=0.9
        )

    @classmethod
    def _consider_issues(
        cls,
        query: str,
        context: Dict[str, Any]
    ) -> Optional[ThinkingStep]:
        """Consider potential issues or ambiguities"""
        query_lower = query.lower()

        # Check for ambiguities
        if len(query.split()) < 3:
            return ThinkingStep(
                step_number=4,
                thought="Query is very short - might be ambiguous. Will try to infer from context, or ask for clarification if needed.",
                reasoning_type="verification",
                confidence=0.6
            )

        # Check for pronouns without clear referents
        pronouns = ['it', 'that', 'those', 'this', 'them']
        has_pronoun = any(pronoun in query_lower.split() for pronoun in pronouns)

        if has_pronoun and not context.get('conversation_history'):
            return ThinkingStep(
                step_number=4,
                thought="Query uses pronouns but I don't have conversation context. Might need to ask what they're referring to.",
                reasoning_type="verification",
                confidence=0.5
            )

        return None

    @classmethod
    def format_for_display(cls, thinking_steps: List[ThinkingStep], show_full: bool = False) -> str:
        """
        Format thinking steps for terminal display

        Args:
            thinking_steps: List of thinking steps
            show_full: If True, show all details. If False, show compact version.

        Returns:
            Formatted string for display
        """
        if not thinking_steps:
            return ""

        lines = []

        if show_full:
            lines.append("\n💭 **Thinking Process:**\n")
            for step in thinking_steps:
                lines.append(f"{step.step_number}. {step.thought}")

        else:
            # Compact version - just show the key thoughts
            lines.append("\n💭 *Thinking:* " + thinking_steps[0].thought)

        return "\n".join(lines)

    @classmethod
    def should_show_thinking(cls, query: str, context: Dict[str, Any]) -> bool:
        """
        Determine if we should show thinking blocks for this query

        Show thinking for:
        - Complex queries (> 10 words)
        - Ambiguous queries
        - Queries that require multi-step reasoning
        - Debugging/analysis queries

        Don't show for:
        - Simple greetings
        - Very short queries
        - Trivial questions
        """
        query_lower = query.lower()

        # Don't show for greetings
        if any(word in query_lower for word in ['hi', 'hey', 'hello', 'thanks']):
            if len(query.split()) <= 3:
                return False

        # Show for complex queries
        if len(query.split()) > 10:
            return True

        # Show for debugging queries
        if any(word in query_lower for word in ['bug', 'error', 'fix', 'wrong', 'broken']):
            return True

        # Show for comparison queries
        if any(word in query_lower for word in ['compare', 'versus', 'vs', 'difference']):
            return True

        # Show for analysis queries
        if any(word in query_lower for word in ['analyze', 'explain', 'why', 'how does']):
            return True

        # Default: don't show for simple queries
        return False


# Convenience function
async def generate_and_format_thinking(
    query: str,
    context: Dict[str, Any],
    show_full: bool = False
) -> str:
    """
    Generate thinking and format for display in one call

    Returns empty string if thinking should not be shown
    """
    if not ThinkingBlockGenerator.should_show_thinking(query, context):
        return ""

    steps = await ThinkingBlockGenerator.generate_thinking(query, context)
    return ThinkingBlockGenerator.format_for_display(steps, show_full)
