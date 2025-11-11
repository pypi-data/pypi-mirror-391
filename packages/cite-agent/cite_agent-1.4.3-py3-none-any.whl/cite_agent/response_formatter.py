"""
Response Formatter - Claude/Cursor-level Response Quality
Creates well-structured, scannable, professional responses
"""

import os
import re
from typing import List, Dict, Any, Optional
from pathlib import Path


class ResponseFormatter:
    """
    Formats responses to be Cursor/Claude quality:
    - Scannable (bullets, headers, structure)
    - Progressive disclosure (summary → details)
    - Appropriate tone for context
    - Right amount of information
    """

    @staticmethod
    def format_file_listing(
        files: List[str],
        query_context: str = "",
        max_display: int = 10
    ) -> str:
        """
        Format file listings clearly and scannably

        BAD:
        /home/user/project/src/main.py
        /home/user/project/src/utils.py
        ... [dumps everything]

        GOOD:
        I found 47 files. Here are the Python files (8):
        • main.py - Main entry point
        • utils.py - Utility functions
        ... (6 more)

        Want to see all files or filter further?
        """
        if not files:
            return "No files found matching that criteria."

        # Determine what type of files these are from context/extensions
        file_type = ResponseFormatter._infer_file_type(files, query_context)

        # Group files by directory for better organization
        grouped = ResponseFormatter._group_files_by_directory(files)

        total_count = len(files)

        # Build response
        parts = []

        # Summary line
        if file_type:
            parts.append(f"I found {total_count} {file_type}:\n")
        else:
            parts.append(f"I found {total_count} files:\n")

        # Show files (organized by directory if multiple dirs)
        if len(grouped) == 1:
            # All in one directory - just list files
            dir_path, file_list = list(grouped.items())[0]
            display_files = file_list[:max_display]

            for file_path in display_files:
                filename = os.path.basename(file_path)
                parts.append(f"• {filename}")

            remaining = total_count - len(display_files)
            if remaining > 0:
                parts.append(f"... ({remaining} more)\n")
        else:
            # Multiple directories - organize by directory
            shown_count = 0
            for dir_path, file_list in list(grouped.items())[:3]:  # Show up to 3 dirs
                parts.append(f"\n**{dir_path}:**")
                for file_path in file_list[:5]:  # Show up to 5 files per dir
                    filename = os.path.basename(file_path)
                    parts.append(f"  • {filename}")
                    shown_count += 1

                    if shown_count >= max_display:
                        break

                if shown_count >= max_display:
                    break

            remaining = total_count - shown_count
            if remaining > 0:
                remaining_dirs = len(grouped) - 3
                if remaining_dirs > 0:
                    parts.append(f"\n... ({remaining} more files in {remaining_dirs} more directories)")
                else:
                    parts.append(f"\n... ({remaining} more files)")

        # Helpful follow-up
        parts.append(f"\nTotal: {total_count} files")

        if total_count > max_display:
            parts.append("Want to see all files, or filter further?")

        return "\n".join(parts)

    @staticmethod
    def format_clarification(
        question: str,
        options: List[str],
        context: str = ""
    ) -> str:
        """
        Format clarification requests clearly

        BAD:
        "Tell me a bit more about what you're looking for"

        GOOD:
        Which kind of analysis are you interested in?
        • Revenue analysis
        • Market share comparison
        • Growth trends

        Let me know what you'd like to focus on.
        """
        parts = []

        # Lead-in question
        if context:
            parts.append(f"{context}\n")
        else:
            parts.append(f"{question}\n")

        # Options as bullets
        for opt in options:
            parts.append(f"• {opt}")

        # Friendly closing
        parts.append("\nLet me know what you'd like to focus on.")

        return "\n".join(parts)

    @staticmethod
    def format_code_explanation(
        code: str,
        file_path: str = "",
        summary: str = "",
        key_points: Optional[List[str]] = None
    ) -> str:
        """
        Format code explanations with progressive disclosure

        Structure:
        1. Summary (what it does - 1 sentence)
        2. Key points (bullets)
        3. Code sample (if needed)
        4. Follow-up offer
        """
        parts = []

        # Summary
        if summary:
            parts.append(f"**Summary:** {summary}\n")
        elif file_path:
            filename = os.path.basename(file_path)
            parts.append(f"Here's **{filename}**:\n")

        # Key points
        if key_points:
            parts.append("**Key points:**")
            for point in key_points:
                parts.append(f"• {point}")
            parts.append("")

        # Code (show first 30 lines max unless it's short)
        code_lines = code.split('\n')
        if len(code_lines) <= 40:
            # Show all
            parts.append("```")
            parts.append(code)
            parts.append("```")
        else:
            # Show excerpt
            parts.append("```")
            parts.append('\n'.join(code_lines[:30]))
            parts.append("... (truncated)")
            parts.append("```")
            parts.append(f"\n*Showing first 30 of {len(code_lines)} lines*")

        # Offer to help more
        parts.append("\nWant me to explain any specific parts or look for issues?")

        return "\n".join(parts)

    @staticmethod
    def format_data_table(
        data: List[Dict[str, Any]],
        title: str = "",
        max_rows: int = 10
    ) -> str:
        """
        Format data as readable table

        Example:
        **Apple Revenue (Quarterly)**

        | Quarter | Revenue | Growth |
        |---------|---------|--------|
        | Q4 2023 | $89.5B  | +12%   |
        | Q3 2023 | $81.8B  | +8%    |
        """
        if not data:
            return "No data available."

        parts = []

        if title:
            parts.append(f"**{title}**\n")

        # Get column names from first row
        if data:
            columns = list(data[0].keys())

            # Create header
            header = "| " + " | ".join(columns) + " |"
            separator = "|" + "|".join(["-" * (len(col) + 2) for col in columns]) + "|"

            parts.append(header)
            parts.append(separator)

            # Add rows (limit to max_rows)
            for row in data[:max_rows]:
                row_str = "| " + " | ".join([str(row.get(col, "")) for col in columns]) + " |"
                parts.append(row_str)

            # Show count if truncated
            if len(data) > max_rows:
                parts.append(f"\n*Showing {max_rows} of {len(data)} rows*")
                parts.append("Want to see more data or a specific time period?")

        return "\n".join(parts)

    @staticmethod
    def format_greeting(query: str = "") -> str:
        """
        Format friendly greeting responses

        Good greetings:
        - Natural and warm
        - Show availability
        - Hint at capabilities
        - No unnecessary details
        """
        greetings = [
            "Hi there! I'm ready to help. What can I dig into for you?",
            "Hey! I'm here and ready. What do you need?",
            "Hello! Ready to help with research, data, or code. What's up?",
        ]

        # Simple rotation (could be more sophisticated)
        import hashlib
        index = int(hashlib.md5(query.encode()).hexdigest(), 16) % len(greetings)
        return greetings[index]

    @staticmethod
    def format_acknowledgment(query: str = "") -> str:
        """Format thanks/acknowledgment responses"""
        responses = [
            "Happy to help! Feel free to ask anything else.",
            "You're welcome! Let me know if you need anything else.",
            "Glad I could help! I'm here if you need more.",
        ]

        import hashlib
        index = int(hashlib.md5(query.encode()).hexdigest(), 16) % len(responses)
        return responses[index]

    @staticmethod
    def format_shell_output(
        command: str,
        output: str,
        output_type: str = "generic"
    ) -> str:
        """
        Format shell command output clearly

        PRINCIPLE: Show RESULTS, not commands (unless asked)

        BAD:
        $ find . -name "*.py"
        ./src/main.py
        ./src/utils.py
        [dumps everything]

        GOOD:
        I found 8 Python files:
        • main.py (in src/)
        • utils.py (in src/)
        ... (6 more)
        """
        if output_type == "file_search":
            # Parse file paths from output
            files = [line.strip() for line in output.split('\n') if line.strip()]
            return ResponseFormatter.format_file_listing(files, "search results")

        elif output_type == "directory_listing":
            # Format directory contents
            files = [line.strip() for line in output.split('\n') if line.strip()]
            return ResponseFormatter.format_file_listing(files, "directory contents")

        elif output_type == "current_directory":
            # Just show the path cleanly
            path = output.strip().split('\n')[-1]  # Last line is usually the path
            return f"We're in **{path}**"

        else:
            # Generic output - show key information, not overwhelming details
            lines = output.strip().split('\n')

            if len(lines) <= 10:
                # Short output - show all
                return output.strip()
            else:
                # Long output - show excerpt
                parts = []
                parts.append('\n'.join(lines[:8]))
                parts.append(f"... ({len(lines) - 8} more lines)")
                parts.append("\nWant to see the full output?")
                return '\n'.join(parts)

    @staticmethod
    def _infer_file_type(files: List[str], context: str) -> str:
        """Infer what type of files these are"""
        if not files:
            return ""

        # Check file extensions
        extensions = set()
        for f in files:
            ext = Path(f).suffix.lower()
            if ext:
                extensions.add(ext)

        # Common patterns
        if extensions == {'.py'}:
            return "Python files"
        elif extensions == {'.js', '.jsx', '.ts', '.tsx'}:
            return "JavaScript/TypeScript files"
        elif extensions == {'.md'}:
            return "Markdown files"
        elif extensions == {'.json'}:
            return "JSON files"
        elif extensions == {'.csv'}:
            return "CSV files"
        elif extensions == {'.txt'}:
            return "text files"

        # Check for test files
        if any('test' in f.lower() for f in files[:5]):
            return "test files"

        # Check context
        if 'test' in context.lower():
            return "test files"
        elif 'python' in context.lower():
            return "Python files"
        elif 'config' in context.lower():
            return "configuration files"

        return "files"

    @staticmethod
    def _group_files_by_directory(files: List[str]) -> Dict[str, List[str]]:
        """Group files by their parent directory"""
        grouped = {}

        for file_path in files:
            dir_path = str(Path(file_path).parent)
            if dir_path == '.':
                dir_path = "(current directory)"

            if dir_path not in grouped:
                grouped[dir_path] = []

            grouped[dir_path].append(file_path)

        return grouped

    @staticmethod
    def apply_progressive_disclosure(
        content: str,
        content_type: str = "generic",
        max_length: int = 500
    ) -> str:
        """
        Apply progressive disclosure pattern
        Show summary first, offer details

        Pattern:
        1. Summary (key point)
        2. Details (if short)
        3. Offer more (if long)
        """
        # If content is short, just return as-is
        if len(content) <= max_length:
            return content

        # Content is long - apply progressive disclosure
        if content_type == "code":
            lines = content.split('\n')
            summary = '\n'.join(lines[:20])
            total_lines = len(lines)

            return (
                f"{summary}\n\n"
                f"... (showing first 20 of {total_lines} lines)\n\n"
                f"Want to see more, or should I explain specific parts?"
            )

        elif content_type == "data":
            # Show first few items + count
            parts = content.split('\n\n')
            summary = '\n\n'.join(parts[:3])
            total_parts = len(parts)

            return (
                f"{summary}\n\n"
                f"... ({total_parts - 3} more items)\n\n"
                f"Want to see everything, or filter further?"
            )

        else:
            # Generic - show first ~300 chars
            summary = content[:max_length].rsplit('.', 1)[0] + '.'

            return (
                f"{summary}\n\n"
                f"... (truncated for length)\n\n"
                f"Want me to continue or focus on something specific?"
            )


# Convenience functions
def format_file_list(files: List[str], context: str = "") -> str:
    """Quick file list formatting"""
    return ResponseFormatter.format_file_listing(files, context)


def format_clarify(question: str, options: List[str]) -> str:
    """Quick clarification formatting"""
    return ResponseFormatter.format_clarification(question, options)


def format_greeting() -> str:
    """Quick greeting"""
    return ResponseFormatter.format_greeting()
