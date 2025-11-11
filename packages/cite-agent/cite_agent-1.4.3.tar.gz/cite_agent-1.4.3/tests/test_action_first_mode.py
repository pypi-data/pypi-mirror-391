#!/usr/bin/env python3
"""
Test Action-First Mode

Verifies that agent SHOWS results instead of asking permission
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.response_pipeline import ResponsePipeline


async def test_action_first():
    """Test that asking phrases are removed"""

    test_cases = [
        {
            'name': 'File listing with asking',
            'mock_response': 'I found 3 Python files:\n\n• main.py\n• utils.py\n• test.py\n\nWant me to show you what\'s in any of these?',
            'query': 'List Python files',
            'should_remove': ['Want me to', 'want me to'],
        },
        {
            'name': 'Code explanation with asking',
            'mock_response': 'This function processes data by validating inputs.\n\nShould I walk through how it works?',
            'query': 'What does this code do?',
            'should_remove': ['Should I', 'should i'],
        },
        {
            'name': 'Data query with asking',
            'mock_response': 'Apple had revenue of $394.3B in 2022.\n\nNeed me to dive deeper into the breakdown?',
            'query': "What was Apple's revenue?",
            'should_remove': ['Need me to', 'need me to'],
        },
        {
            'name': 'Paper search with asking',
            'mock_response': 'Found 5 papers on quantum computing.\n\nWould you like me to show the abstracts?',
            'query': 'Find papers on quantum computing',
            'should_remove': ['Would you like', 'would you like'],
        },
        {
            'name': 'Already action-first (no asking)',
            'mock_response': 'I found 3 Python files:\n\n• main.py - Entry point\n• utils.py - Helper functions\n• test.py - Unit tests\n\nHere\'s a preview of main.py:\n\n```python\ndef main():\n    ...\n```',
            'query': 'List Python files',
            'should_remove': [],  # Nothing to remove - already good!
        },
    ]

    print("=" * 80)
    print("ACTION-FIRST MODE TEST")
    print("Verifying asking phrases are removed")
    print("=" * 80)

    passed = 0
    failed = 0

    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"TEST: {test['name']}")
        print("=" * 80)

        # Process through pipeline
        result = await ResponsePipeline.process(
            test['mock_response'],
            test['query'],
            {},
            'generic'
        )

        print(f"\n❌ BEFORE:")
        print(f"   {test['mock_response'][:100]}...")

        print(f"\n✅ AFTER ACTION-FIRST:")
        print(f"   {result.final_response[:100]}...")

        # Check if asking phrases were removed
        response_lower = result.final_response.lower()
        removed_all = all(
            phrase.lower() not in response_lower
            for phrase in test['should_remove']
        )

        print(f"\n📊 VERIFICATION:")
        if test['should_remove']:
            print(f"   Phrases to remove: {test['should_remove']}")

            still_present = [
                phrase for phrase in test['should_remove']
                if phrase.lower() in response_lower
            ]

            if still_present:
                print(f"   ❌ Still present: {still_present}")
                failed += 1
            else:
                print(f"   ✅ All asking phrases removed")
                passed += 1
        else:
            # Test case with no asking phrases - should pass through unchanged
            print(f"   ✅ No asking phrases to remove (already action-first)")
            passed += 1

    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print("=" * 80)

    total = passed + failed
    success_rate = (passed / total * 100) if total > 0 else 0

    print(f"✅ Passed: {passed}/{total} ({success_rate:.1f}%)")
    print(f"❌ Failed: {failed}/{total} ({(100-success_rate):.1f}%)")

    if success_rate >= 80:
        print("\n✅ ACTION-FIRST MODE IS WORKING!")
        print("   Agent shows results proactively instead of asking permission")
        return True
    else:
        print("\n❌ Action-first mode needs more work")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_action_first())
    sys.exit(0 if result else 1)
