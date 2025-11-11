"""
Graceful Error Handling - Never Expose Technical Details to Users
Converts technical errors to friendly, actionable messages
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class GracefulErrorHandler:
    """
    Converts all technical errors to user-friendly messages

    PRINCIPLE: Users should never see:
    - Stack traces
    - API error codes
    - Certificate errors
    - Connection details
    - Internal variable names
    - Technical jargon

    PRINCIPLE: Users should always see:
    - What went wrong in simple terms
    - What they can do about it
    - Alternative options if available
    """

    # User-friendly error messages mapped from technical errors
    ERROR_MESSAGES = {
        # Network / Connection
        'ConnectionError': "I'm having trouble connecting right now. Please try again in a moment.",
        'Timeout': "That's taking longer than expected. Let me try a simpler approach.",
        'TimeoutError': "That's taking longer than expected. Let me try a simpler approach.",
        'ConnectTimeout': "I couldn't connect. Please check your network and try again.",

        # API Errors
        'HTTPError': "I encountered an issue accessing that service. Let me try again.",
        'APIError': "Something went wrong on my end. Let me try another way.",
        'RateLimitError': "I've hit my usage limit. Please try again in a few minutes.",
        'QuotaExceeded': "I've reached my daily limit. Please try again tomorrow.",

        # Authentication / Authorization
        'AuthenticationError': "I'm having trouble with authentication. Please check your setup.",
        'PermissionError': "I don't have permission to access that. Please check the permissions.",
        'UnauthorizedError': "I need authorization to access that resource.",

        # Data / Parsing
        'JSONDecodeError': "I received data in an unexpected format. Let me try again.",
        'ParseError': "I couldn't understand the response. Let me try another approach.",
        'ValueError': "I received unexpected data. Let me try again.",
        'KeyError': "I couldn't find the expected information. Let me try differently.",

        # TLS / SSL / Certificate
        'SSLError': "I'm having trouble with the secure connection. Please try again.",
        'CertificateError': "I'm having trouble with the secure connection. Please try again.",
        'TLS_error': "I'm having trouble with the secure connection. Please try again.",

        # File System
        'FileNotFoundError': "I couldn't find that file. Please check the path.",
        'IsADirectoryError': "That's a directory, not a file. Please specify a file path.",
        'NotADirectoryError': "That's a file, not a directory. Please specify a directory path.",
        'PermissionError_file': "I don't have permission to access that file.",

        # General
        'Exception': "Something unexpected happened. Let me try again.",
        'RuntimeError': "I encountered an unexpected issue. Let me try another approach.",
    }

    @classmethod
    def handle_error(
        cls,
        error: Exception,
        context: str = "",
        fallback_action: Optional[str] = None
    ) -> str:
        """
        Convert any error to a user-friendly message

        Args:
            error: The exception that occurred
            context: What the agent was trying to do (e.g., "search papers", "read file")
            fallback_action: What the user can do instead (e.g., "try a different search")

        Returns:
            User-friendly error message (never technical details)
        """
        # Log technical details for debugging (but don't show to user!)
        logger.error(f"Error in {context}: {type(error).__name__}: {str(error)}", exc_info=True)

        # Get error type name
        error_type = type(error).__name__

        # Look up user-friendly message
        user_message = cls.ERROR_MESSAGES.get(error_type)

        # Check for specific error patterns in the message
        error_str = str(error).lower()

        if not user_message:
            # Pattern matching for specific errors
            if 'certificate' in error_str or 'tls' in error_str or 'ssl' in error_str:
                user_message = cls.ERROR_MESSAGES['CertificateError']
            elif 'timeout' in error_str:
                user_message = cls.ERROR_MESSAGES['Timeout']
            elif 'connection' in error_str or 'connect' in error_str:
                user_message = cls.ERROR_MESSAGES['ConnectionError']
            elif 'rate limit' in error_str or 'quota' in error_str:
                user_message = cls.ERROR_MESSAGES['RateLimitError']
            elif 'auth' in error_str or 'unauthorized' in error_str:
                user_message = cls.ERROR_MESSAGES['AuthenticationError']
            elif 'not found' in error_str:
                user_message = cls.ERROR_MESSAGES['FileNotFoundError']
            else:
                # Generic fallback
                user_message = cls.ERROR_MESSAGES['Exception']

        # Add context if provided
        if context:
            full_message = f"While trying to {context}, {user_message.lower()}"
        else:
            full_message = user_message

        # Add fallback action if provided
        if fallback_action:
            full_message += f" {fallback_action}"

        return full_message

    @classmethod
    def wrap_response_with_error_handling(cls, response: str) -> str:
        """
        Scan response for any leaked technical errors and clean them

        This is a safety net in case errors slip through
        """
        # Technical terms that should NEVER appear in user responses
        forbidden_patterns = [
            ('TLS_error', 'secure connection issue'),
            ('CERTIFICATE_VERIFY_FAILED', 'secure connection issue'),
            ('upstream connect error', 'connection issue'),
            ('stack trace', ''),
            ('Traceback (most recent call last)', ''),
            ('Exception:', ''),
            ('ERROR:', ''),
            ('⚠️ I couldn\'t finish the reasoning step', 'I encountered an issue'),
            ('language model call failed', 'I had trouble processing that'),
            ('API call failed', 'I had trouble accessing that service'),
        ]

        cleaned_response = response
        had_technical_errors = False

        for technical_term, friendly_replacement in forbidden_patterns:
            if technical_term.lower() in cleaned_response.lower():
                # If we find technical errors, replace with friendly version
                logger.warning(f"Found leaked technical error in response: {technical_term}")
                had_technical_errors = True

                if friendly_replacement:
                    # Replace with friendly term
                    import re
                    cleaned_response = re.sub(
                        re.escape(technical_term),
                        friendly_replacement,
                        cleaned_response,
                        flags=re.IGNORECASE
                    )
                else:
                    # Remove the line entirely
                    lines = cleaned_response.split('\n')
                    cleaned_response = '\n'.join([
                        line for line in lines
                        if technical_term.lower() not in line.lower()
                    ])

        # If the response became empty or too short AFTER cleaning errors, provide generic friendly message
        # Don't flag legitimately short responses (greetings, acknowledgments, etc.)
        if had_technical_errors and len(cleaned_response.strip()) < 20:
            cleaned_response = "I encountered an issue while processing that. Could you try rephrasing your question?"

        return cleaned_response

    @classmethod
    def create_fallback_response(cls, original_query: str, error: Exception) -> str:
        """
        Create a complete fallback response when main processing fails

        Returns a helpful response instead of exposing the error
        """
        # Get friendly error message
        error_msg = cls.handle_error(error, "process your request")

        # Try to be helpful based on query type
        query_lower = original_query.lower()

        suggestions = []

        if any(word in query_lower for word in ['search', 'find', 'papers', 'research']):
            suggestions.append("• Try a more specific search term")
            suggestions.append("• Check if the topic exists in our database")

        if any(word in query_lower for word in ['revenue', 'stock', 'financial', 'company']):
            suggestions.append("• Try searching for a specific company by name")
            suggestions.append("• Check if the company is publicly traded")

        if any(word in query_lower for word in ['file', 'directory', 'folder', 'read']):
            suggestions.append("• Check if the file path is correct")
            suggestions.append("• Try using an absolute path")

        response_parts = [error_msg]

        if suggestions:
            response_parts.append("\nYou could try:")
            response_parts.extend(suggestions)

        return '\n'.join(response_parts)


# Convenient function for quick error handling
def handle_error_gracefully(
    error: Exception,
    context: str = "",
    fallback_action: Optional[str] = None
) -> str:
    """Shortcut function for graceful error handling"""
    return GracefulErrorHandler.handle_error(error, context, fallback_action)
