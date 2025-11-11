"""
Proactive Action Boundaries

Defines what actions the agent can do automatically vs what needs explicit permission

PHILOSOPHY: Be proactive with READ operations, cautious with WRITE operations
"""

from typing import Dict, List, Set
import re


class ProactiveBoundaries:
    """
    Defines safe boundaries for proactive agent behavior

    SAFE TO AUTO-DO (read-only, informational):
    - These enhance user experience without risk

    NEEDS PERMISSION (write/destructive):
    - These could cause problems if done incorrectly
    """

    # Commands/actions that are SAFE to do proactively
    SAFE_AUTO_ACTIONS: Set[str] = {
        # File operations (read-only)
        'list_files',
        'read_file',
        'preview_file',
        'search_in_files',
        'find_files',
        'show_file_info',
        'cat',
        'head',
        'tail',
        'less',
        'grep',
        'find',

        # Directory operations (read-only)
        'list_directory',
        'show_directory_tree',
        'navigate_directory',  # cd is safe
        'pwd',
        'ls',
        'tree',

        # Code analysis (read-only)
        'explain_code',
        'show_functions',
        'analyze_structure',
        'find_definitions',

        # Data operations (read-only)
        'query_api',
        'fetch_data',
        'show_stats',
        'search_papers',
        'get_financial_data',

        # Git operations (read-only)
        'git_status',
        'git_log',
        'git_diff',
        'git_show',
        'git_blame',

        # System info (read-only)
        'show_env',
        'check_dependencies',
        'list_processes',
    }

    # Commands/actions that NEED EXPLICIT PERMISSION
    NEEDS_PERMISSION: Set[str] = {
        # File operations (write/destructive)
        'create_file',
        'delete_file',
        'modify_file',
        'move_file',
        'rename_file',
        'chmod',
        'chown',
        'touch',
        'mkdir',
        'rmdir',
        'rm',
        'mv',
        'cp',  # Can overwrite

        # Code execution (potentially dangerous)
        'run_script',
        'execute_code',
        'eval',
        'exec',

        # Package management
        'install_package',
        'uninstall_package',
        'update_packages',
        'pip',
        'npm',
        'apt',
        'brew',

        # Git operations (write)
        'git_add',
        'git_commit',
        'git_push',
        'git_pull',
        'git_merge',
        'git_rebase',
        'git_reset',

        # Network operations (write/external)
        'send_request',
        'post_data',
        'upload_file',
        'download_file',

        # System operations
        'change_settings',
        'modify_config',
        'kill_process',
        'start_service',
        'stop_service',
    }

    @classmethod
    def is_safe_to_auto_do(cls, action: str) -> bool:
        """
        Check if action is safe to do automatically

        Returns:
            True if safe to do proactively
            False if needs explicit user permission
        """
        action_lower = action.lower()

        # Check exact matches
        if action_lower in cls.SAFE_AUTO_ACTIONS:
            return True

        if action_lower in cls.NEEDS_PERMISSION:
            return False

        # Check patterns
        # Safe patterns
        safe_patterns = [
            r'^(ls|pwd|cd|find|grep|cat|head|tail|less)',
            r'^git\s+(status|log|diff|show|blame)',
            r'search|find|list|show|display|preview|read',
        ]

        for pattern in safe_patterns:
            if re.search(pattern, action_lower):
                return True

        # Dangerous patterns
        dangerous_patterns = [
            r'^(rm|mv|cp|touch|mkdir|chmod)',
            r'^git\s+(add|commit|push|pull|merge|rebase|reset)',
            r'(delete|remove|modify|edit|create|install|update)',
            r'^(pip|npm|apt|brew)',
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, action_lower):
                return False

        # Default: be conservative - if unsure, ask permission
        return False

    @classmethod
    def get_auto_expansion_for_query(cls, query: str, initial_result: str) -> Dict[str, any]:
        """
        Determine what automatic expansion to do based on query and initial result

        Returns dict with:
        - should_expand: bool
        - expansion_actions: List[str] - actions to take automatically
        - reason: str - why expanding
        """
        query_lower = query.lower()
        result_lower = initial_result.lower()

        expansions = {
            'should_expand': False,
            'expansion_actions': [],
            'reason': ''
        }

        # Pattern 1: Listed files → preview main one
        if any(word in query_lower for word in ['list', 'show', 'find']) and \
           any(word in query_lower for word in ['file', 'files', 'py', 'js']):

            # Check if result is just a list (short, has bullets/lines, BUT no code/details)
            has_code_block = '```' in initial_result
            has_detailed_descriptions = ' - ' in initial_result or ': ' in result_lower
            is_short_list = len(initial_result) < 300 and ('•' in initial_result or '\n' in initial_result)

            if is_short_list and not has_code_block and not has_detailed_descriptions:
                expansions['should_expand'] = True
                expansions['expansion_actions'] = ['preview_main_file']
                expansions['reason'] = 'Listed files but no content shown - auto-preview main file'

        # Pattern 2: Found papers → show abstracts
        if 'paper' in query_lower and 'found' in result_lower:
            if 'abstract' not in result_lower:
                expansions['should_expand'] = True
                expansions['expansion_actions'] = ['show_paper_abstracts']
                expansions['reason'] = 'Found papers but no abstracts - auto-show summaries'

        # Pattern 3: Code query → show examples
        if any(word in query_lower for word in ['function', 'class', 'code']) and \
           'how' in query_lower:
            if '```' not in initial_result and len(initial_result) < 200:
                expansions['should_expand'] = True
                expansions['expansion_actions'] = ['show_code_examples']
                expansions['reason'] = 'Code explanation without examples - auto-show code'

        # Pattern 4: Data query → show sample/visualization
        if any(word in query_lower for word in ['data', 'revenue', 'metrics', 'stats']):
            if len(initial_result) < 150:  # Just a number, not detailed
                expansions['should_expand'] = True
                expansions['expansion_actions'] = ['show_data_breakdown']
                expansions['reason'] = 'Data query with minimal detail - auto-show breakdown'

        return expansions

    @classmethod
    def validate_proactive_action(cls, action: str, context: Dict) -> Dict[str, any]:
        """
        Validate if a proactive action should be allowed

        Returns:
        - allowed: bool
        - reason: str
        - requires_confirmation: bool
        """
        is_safe = cls.is_safe_to_auto_do(action)

        if is_safe:
            return {
                'allowed': True,
                'reason': 'Safe read-only operation',
                'requires_confirmation': False
            }
        else:
            return {
                'allowed': False,
                'reason': 'Write/destructive operation requires explicit permission',
                'requires_confirmation': True
            }


# Convenience functions
def is_safe_to_auto_do(action: str) -> bool:
    """Quick check if action is safe to do automatically"""
    return ProactiveBoundaries.is_safe_to_auto_do(action)


def should_auto_expand(query: str, result: str) -> bool:
    """Quick check if result should be automatically expanded"""
    expansion = ProactiveBoundaries.get_auto_expansion_for_query(query, result)
    return expansion['should_expand']
