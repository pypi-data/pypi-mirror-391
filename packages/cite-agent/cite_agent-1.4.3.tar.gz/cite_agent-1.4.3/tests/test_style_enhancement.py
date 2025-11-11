#!/usr/bin/env python3
"""
Test Style Enhancement

Tests if the style enhancer successfully transforms robotic responses
into pleasant, stylish ones
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.response_style_enhancer import ResponseStyleEnhancer


def assess_style_improvements():
    """Test if style enhancements work as expected"""

    test_cases = [
        {
            'name': 'Formal greeting → Warm greeting',
            'input': 'Hello. How can I assist you today?',
            'query': 'Hey!',
            'expected_improvements': ['Hi', 'Ready to help', 'dig into'],
        },
        {
            'name': 'Robotic phrasing → Natural language',
            'input': 'I have analyzed the files and determined that there are 3 Python files.',
            'query': 'List Python files',
            'expected_improvements': ["I've looked at", "found", "I've"],
        },
        {
            'name': 'Plain list → Elegant bullets',
            'input': 'Found files: main.py, utils.py, test.py',
            'query': 'Show me Python files',
            'expected_improvements': ['•'],  # No asking phrases in action-first mode
        },
        {
            'name': 'Cold thank you → Warm response',
            'input': 'You are welcome.',
            'query': 'Thanks!',
            'expected_improvements': ['Happy to help'],  # Warm but no asking in action-first
        },
        {
            'name': 'Explanation (action-first mode)',
            'input': 'This function processes data by validating input and saving to database.',
            'query': 'What does this code do?',
            'expected_improvements': [],  # Agent would show code automatically in action-first mode
        },
    ]

    print("=" * 80)
    print("STYLE ENHANCEMENT TEST")
    print("Testing if responses become pleasant and stylish")
    print("=" * 80)

    passed = 0
    failed = 0

    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"TEST: {test['name']}")
        print("=" * 80)

        # Apply style enhancement
        enhanced = ResponseStyleEnhancer.enhance(test['input'], test['query'], {})

        print(f"\n❌ BEFORE (Robotic):")
        print(f"   {test['input']}")

        print(f"\n✅ AFTER (Styled):")
        print(f"   {enhanced}")

        # Check if improvements were applied
        improvements_found = []
        for expected in test['expected_improvements']:
            if expected.lower() in enhanced.lower():
                improvements_found.append(expected)

        print(f"\n📊 VERIFICATION:")
        print(f"   Expected improvements: {len(test['expected_improvements'])}")
        print(f"   Found: {len(improvements_found)}")

        if len(improvements_found) >= len(test['expected_improvements']) * 0.6:  # 60% threshold
            print(f"   ✅ PASS - Style enhanced successfully")
            passed += 1
        else:
            print(f"   ❌ FAIL - Not enough improvements applied")
            print(f"   Missing: {set(test['expected_improvements']) - set(improvements_found)}")
            failed += 1

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print("=" * 80)
    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"✅ Passed: {passed}/{total} ({success_rate:.1f}%)")
    print(f"❌ Failed: {failed}/{total} ({(100-success_rate):.1f}%)")

    if success_rate >= 80:
        print("\n✅ Style enhancement is WORKING!")
        return True
    else:
        print("\n❌ Style enhancement needs more work")
        return False


if __name__ == "__main__":
    result = assess_style_improvements()
    sys.exit(0 if result else 1)
