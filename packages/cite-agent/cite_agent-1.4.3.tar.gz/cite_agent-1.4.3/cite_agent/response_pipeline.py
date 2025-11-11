"""
Response Pipeline - Comprehensive Quality Processing
Integrates all quality improvements into a single pipeline

This is the "intelligence layer" that was missing
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .error_handler import GracefulErrorHandler
from .response_formatter import ResponseFormatter
from .quality_gate import ResponseQualityGate, QualityAssessment
from .response_enhancer import ResponseEnhancer
from .response_style_enhancer import ResponseStyleEnhancer
from .action_first_mode import ActionFirstMode
from .auto_expander import AutoExpander

logger = logging.getLogger(__name__)


@dataclass
class ProcessedResponse:
    """Result of pipeline processing"""
    final_response: str
    quality_score: float
    improvements_applied: list
    processing_notes: list


class ResponsePipeline:
    """
    End-to-end response processing pipeline

    Steps:
    1. Clean any technical errors
    2. Apply appropriate formatting
    3. Assess quality
    4. Improve if needed
    5. Final safety check
    """

    @classmethod
    async def process(
        cls,
        raw_response: str,
        query: str,
        context: Dict[str, Any],
        response_type: str = "generic"
    ) -> ProcessedResponse:
        """
        Process a response through the quality pipeline

        Args:
            raw_response: The initial response from LLM
            query: The original user query
            context: Additional context (tools used, API results, etc.)
            response_type: Type of response (greeting, file_list, data, code, etc.)

        Returns:
            ProcessedResponse with final polished response and metadata
        """
        improvements = []
        notes = []

        # Step 1: Clean technical errors (safety first!)
        cleaned_response = GracefulErrorHandler.wrap_response_with_error_handling(raw_response)

        if cleaned_response != raw_response:
            improvements.append("Removed technical error messages")
            notes.append(f"Cleaned {len(raw_response) - len(cleaned_response)} chars of technical details")

        # Step 2: Apply appropriate formatting based on response type
        formatted_response = cls._apply_smart_formatting(
            cleaned_response,
            query,
            context,
            response_type
        )

        if formatted_response != cleaned_response:
            improvements.append("Applied smart formatting")

        # Step 3: Assess quality
        assessment = ResponseQualityGate.assess(formatted_response, query, context)

        notes.append(f"Quality score: {assessment.overall_score:.2f}")
        if assessment.issues:
            notes.append(f"Issues: {', '.join(assessment.issues[:3])}")

        # Step 4: Apply automatic improvements
        if assessment.should_retry or assessment.overall_score < 0.75:
            improved_response = ResponseQualityGate.improve_response(
                formatted_response,
                assessment,
                query
            )

            if improved_response != formatted_response:
                improvements.append("Applied automatic quality improvements")
                formatted_response = improved_response

                # Re-assess after improvements
                new_assessment = ResponseQualityGate.assess(improved_response, query, context)
                notes.append(f"Improved quality: {new_assessment.overall_score:.2f}")
                assessment = new_assessment

        # Step 4.5: ENHANCE to push quality even higher
        if assessment.overall_score < 0.80:
            enhanced_response = ResponseEnhancer.enhance(
                formatted_response,
                query,
                context
            )

            if enhanced_response != formatted_response:
                improvements.append("Enhanced for higher quality")
                formatted_response = enhanced_response

                # Re-assess after enhancement
                final_assessment = ResponseQualityGate.assess(enhanced_response, query, context)
                notes.append(f"Enhanced quality: {final_assessment.overall_score:.2f}")
                assessment = final_assessment

        # Step 4.7: STYLE ENHANCEMENT - Make responses pleasant and stylish
        # This is what makes responses ACTUALLY GOOD, not just functional
        styled_response = ResponseStyleEnhancer.enhance(
            formatted_response,
            query,
            context
        )

        if styled_response != formatted_response:
            improvements.append("Enhanced style to be pleasant and friendly")
            notes.append("Applied style enhancements: warm, natural")
            formatted_response = styled_response

        # Step 4.8: ACTION-FIRST MODE - Remove asking phrases, prioritize action over talk
        # User wants agent to DO things, not ask permission
        action_first_response = ActionFirstMode.make_action_first(
            formatted_response,
            query,
            context
        )

        if action_first_response != formatted_response:
            improvements.append("Transformed to action-first mode")
            notes.append("Removed asking phrases - agent shows results proactively")
            formatted_response = action_first_response

        # Step 4.9: AUTO-EXPANSION CHECK - Detect if response needs more detail
        # This is a quality check - if it detects expansion needed, it means
        # the LLM didn't follow action-first guidelines properly
        checked_response = AutoExpander.expand(formatted_response, query, context)
        # (This currently just logs warnings if expansion is detected as needed)

        # Step 5: Final safety check
        final_response = GracefulErrorHandler.wrap_response_with_error_handling(checked_response)

        return ProcessedResponse(
            final_response=final_response,
            quality_score=assessment.overall_score,
            improvements_applied=improvements,
            processing_notes=notes
        )

    @classmethod
    def _apply_smart_formatting(
        cls,
        response: str,
        query: str,
        context: Dict[str, Any],
        response_type: str
    ) -> str:
        """
        Apply intelligent formatting based on response type and context
        """
        # Detect response type if not specified
        if response_type == "generic":
            response_type = cls._detect_response_type(response, query, context)

        # Apply appropriate formatter
        if response_type == "greeting":
            # Greetings should be brief and friendly
            if len(response.split()) > 30:
                return ResponseFormatter.format_greeting(query)
            return response

        elif response_type == "acknowledgment":
            # Thanks/acknowledgments should be brief
            if len(response.split()) > 20:
                return ResponseFormatter.format_acknowledgment(query)
            return response

        elif response_type == "file_list":
            # File listings should be structured
            # Extract file paths from response
            import re
            file_pattern = r'[\/\w\-\.]+\.[\w]+'
            files = re.findall(file_pattern, response)

            if files:
                return ResponseFormatter.format_file_listing(files, query)
            return response

        elif response_type == "clarification":
            # Clarifications should have bullets
            # Extract options if present
            lines = response.split('\n')
            options = [line.strip('- •*').strip() for line in lines if line.strip().startswith(('-', '•', '*'))]

            if not options:
                # No bullets found - check for sentence-based options
                sentences = response.split('.')
                if len(sentences) >= 2:
                    # Try to extract options from sentences
                    options = [s.strip() + '.' for s in sentences[1:4] if len(s.strip()) > 10]

            if options:
                question = lines[0] if lines else "What would you like to focus on?"
                return ResponseFormatter.format_clarification(question, options)
            return response

        elif response_type == "code":
            # Code should have structure (summary + code + offer)
            return response  # Already should be formatted

        elif response_type == "shell_output":
            # Shell output should be clean and focused
            output_type = context.get('shell_output_type', 'generic')
            command = context.get('command', '')
            output = context.get('output', response)

            return ResponseFormatter.format_shell_output(command, output, output_type)

        # Default: apply progressive disclosure if too long
        elif len(response) > 600:
            return ResponseFormatter.apply_progressive_disclosure(response, "generic", 500)

        return response

    @classmethod
    def _detect_response_type(cls, response: str, query: str, context: Dict[str, Any]) -> str:
        """
        Detect what type of response this is
        """
        query_lower = query.lower()
        response_lower = response.lower()

        # Greeting
        if any(word in query_lower for word in ['hi', 'hey', 'hello']) and len(query.split()) <= 3:
            return "greeting"

        # Acknowledgment
        if any(word in query_lower for word in ['thanks', 'thank you', 'thx']):
            return "acknowledgment"

        # File listing
        if ('file' in query_lower or 'directory' in query_lower or 'folder' in query_lower):
            if any(ext in response for ext in ['.py', '.js', '.md', '.txt', '.json', '.csv']):
                return "file_list"

        # Clarification
        if '?' in response and any(word in response_lower for word in ['which', 'what kind', 'tell me more']):
            return "clarification"

        # Code
        if '```' in response or 'def ' in response or 'class ' in response:
            return "code"

        # Shell output
        if context.get('tools_used') and 'shell_execution' in context.get('tools_used', []):
            return "shell_output"

        return "generic"


# Convenience function
async def process_response(
    response: str,
    query: str,
    context: Dict[str, Any] = None,
    response_type: str = "generic"
) -> str:
    """
    Quick response processing - returns just the final response string
    """
    result = await ResponsePipeline.process(
        response,
        query,
        context or {},
        response_type
    )
    return result.final_response
