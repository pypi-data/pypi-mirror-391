#!/usr/bin/env python3
"""
Test Proactive Boundaries

Verifies that agent correctly identifies safe vs unsafe actions
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.proactive_boundaries import ProactiveBoundaries


def test_safe_actions():
    """Test that safe read-only actions are allowed"""
    safe_actions = [
        'ls',
        'pwd',
        'cd /tmp',
        'cat file.txt',
        'head -50 script.py',
        'grep pattern *.py',
        'find . -name "*.py"',
        'git status',
        'git log',
        'git diff',
        'list_files',
        'read_file',
        'preview_file',
        'search_in_files',
        'query_api',
        'fetch_data',
    ]

    print("=" * 80)
    print("TESTING SAFE ACTIONS (should all be allowed)")
    print("=" * 80)

    passed = 0
    failed = 0

    for action in safe_actions:
        result = ProactiveBoundaries.is_safe_to_auto_do(action)

        if result:
            print(f"✅ {action:30} → ALLOWED (correct)")
            passed += 1
        else:
            print(f"❌ {action:30} → BLOCKED (incorrect - should be allowed)")
            failed += 1

    return passed, failed


def test_dangerous_actions():
    """Test that dangerous write/destructive actions are blocked"""
    dangerous_actions = [
        'rm file.txt',
        'rm -rf /',
        'mv old.txt new.txt',
        'touch newfile.txt',
        'mkdir newdir',
        'chmod 777 file.txt',
        'git add .',
        'git commit -m "test"',
        'git push',
        'pip install package',
        'npm install',
        'create_file',
        'delete_file',
        'modify_file',
        'install_package',
    ]

    print("\n" + "=" * 80)
    print("TESTING DANGEROUS ACTIONS (should all be blocked)")
    print("=" * 80)

    passed = 0
    failed = 0

    for action in dangerous_actions:
        result = ProactiveBoundaries.is_safe_to_auto_do(action)

        if not result:
            print(f"✅ {action:30} → BLOCKED (correct)")
            passed += 1
        else:
            print(f"❌ {action:30} → ALLOWED (incorrect - should be blocked!)")
            failed += 1

    return passed, failed


def test_auto_expansion_detection():
    """Test automatic expansion detection"""
    test_cases = [
        {
            'query': 'List Python files',
            'result': 'I found 3 files:\n• main.py\n• utils.py\n• test.py',
            'should_expand': True,
            'reason': 'Short list without content'
        },
        {
            'query': 'List Python files',
            'result': 'I found 3 files:\n\n• main.py - Entry point with main() function\n• utils.py - Helper utilities\n• test.py - Unit tests\n\nHere\'s a preview of main.py:\n\n```python\ndef main():\n    pass\n```',
            'should_expand': False,
            'reason': 'Already has detailed content'
        },
        {
            'query': 'Find papers on quantum computing',
            'result': 'Found 5 papers on quantum computing from arxiv.',
            'should_expand': True,
            'reason': 'Found papers but no abstracts'
        },
        {
            'query': 'What was Apple\'s revenue?',
            'result': 'Apple had revenue of $394.3B in 2022.',
            'should_expand': True,
            'reason': 'Data query with minimal detail'
        },
    ]

    print("\n" + "=" * 80)
    print("TESTING AUTO-EXPANSION DETECTION")
    print("=" * 80)

    passed = 0
    failed = 0

    for test in test_cases:
        expansion = ProactiveBoundaries.get_auto_expansion_for_query(
            test['query'],
            test['result']
        )

        expected = test['should_expand']
        actual = expansion['should_expand']

        if actual == expected:
            print(f"✅ Query: {test['query'][:40]}")
            print(f"   Expected expand={expected}, Got={actual} (correct)")
            if actual:
                print(f"   Actions: {expansion['expansion_actions']}")
                print(f"   Reason: {expansion['reason']}")
            passed += 1
        else:
            print(f"❌ Query: {test['query'][:40]}")
            print(f"   Expected expand={expected}, Got={actual} (incorrect)")
            failed += 1

        print()

    return passed, failed


def main():
    """Run all boundary tests"""
    total_passed = 0
    total_failed = 0

    # Test safe actions
    passed, failed = test_safe_actions()
    total_passed += passed
    total_failed += failed

    # Test dangerous actions
    passed, failed = test_dangerous_actions()
    total_passed += passed
    total_failed += failed

    # Test auto-expansion
    passed, failed = test_auto_expansion_detection()
    total_passed += passed
    total_failed += failed

    # Summary
    print("=" * 80)
    print("FINAL SUMMARY")
    print("=" * 80)

    total = total_passed + total_failed
    success_rate = (total_passed / total * 100) if total > 0 else 0

    print(f"✅ Passed: {total_passed}/{total} ({success_rate:.1f}%)")
    print(f"❌ Failed: {total_failed}/{total} ({(100-success_rate):.1f}%)")

    if success_rate >= 90:
        print("\n✅ PROACTIVE BOUNDARIES ARE WORKING!")
        print("   Safe actions allowed, dangerous actions blocked")
        return True
    else:
        print("\n❌ Proactive boundaries need adjustment")
        return False


if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
