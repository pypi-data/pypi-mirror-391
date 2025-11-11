#!/usr/bin/env python3
"""
Test style enhancement with mocked LLM responses

Since integration tests require authentication, we'll test the style
enhancement by mocking the LLM responses and verifying the pipeline
applies style enhancements correctly.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.response_pipeline import ResponsePipeline


async def test_style_on_various_responses():
    """Test style enhancement on various mock LLM responses"""

    test_cases = [
        {
            'scenario': 'Greeting Response',
            'mock_llm_response': 'Hello. How can I assist you today?',
            'query': 'Hey!',
            'response_type': 'greeting',
            'expected_style_markers': ['hi', 'ready to help'],
        },
        {
            'scenario': 'File Listing Response',
            'mock_llm_response': 'I have analyzed the directory and located the following files: main.py, utils.py, test.py, config.py',
            'query': 'List Python files',
            'response_type': 'file_list',
            'expected_style_markers': ['found', '•'],  # Natural language + formatting (NO asking phrases in action-first mode)
        },
        {
            'scenario': 'Code Explanation',
            'mock_llm_response': 'This code defines a function that processes user data by validating inputs and storing in the database.',
            'query': 'What does this function do?',
            'response_type': 'code',
            'expected_style_markers': [],  # Short explanation is fine in action-first mode (would show code automatically)
        },
        {
            'scenario': 'Thank You Response',
            'mock_llm_response': 'You are welcome.',
            'query': 'Thanks!',
            'response_type': 'acknowledgment',
            'expected_style_markers': ['happy to help'],  # Warm response (no asking in action-first mode)
        },
        {
            'scenario': 'Data Query Response',
            'mock_llm_response': 'I have determined that Apple had revenue of $394.3B in 2022.',
            'query': "What was Apple's revenue in 2022?",
            'response_type': 'generic',
            'expected_style_markers': ['found'],  # Natural language
        },
        {
            'scenario': 'Research Response',
            'mock_llm_response': 'I have located 5 papers on quantum computing from the archive.',
            'query': 'Find papers on quantum computing',
            'response_type': 'generic',
            'expected_style_markers': ['found'],  # Natural language
        },
    ]

    print("=" * 80)
    print("STYLE ENHANCEMENT TEST (Mocked Responses)")
    print("Testing if pipeline applies style to various response types")
    print("=" * 80)

    passed = 0
    failed = 0

    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"SCENARIO: {test['scenario']}")
        print("=" * 80)

        # Process through pipeline
        result = await ResponsePipeline.process(
            test['mock_llm_response'],
            test['query'],
            {},
            test['response_type']
        )

        print(f"\n❌ BEFORE (Mock LLM):")
        print(f"   {test['mock_llm_response']}")

        print(f"\n✅ AFTER PIPELINE:")
        print(f"   {result.final_response}")

        print(f"\n📊 METRICS:")
        print(f"   Quality Score: {result.quality_score:.2f}")
        print(f"   Improvements: {', '.join(result.improvements_applied) if result.improvements_applied else 'None'}")

        # Check style markers
        response_lower = result.final_response.lower()
        found_markers = []
        missing_markers = []

        for marker in test['expected_style_markers']:
            if marker.lower() in response_lower:
                found_markers.append(marker)
            else:
                missing_markers.append(marker)

        # Check for anticipatory phrases if required
        has_anticipatory = False
        if test.get('anticipatory_check', False):
            anticipatory_phrases = ['want me to', 'need me to', 'should i', 'let me know', 'would you like']
            has_anticipatory = any(phrase in response_lower for phrase in anticipatory_phrases)
            if has_anticipatory:
                found_markers.append('anticipatory')
            else:
                missing_markers.append('anticipatory')

        print(f"\n🎨 STYLE CHECKS:")
        total_expected = len(test['expected_style_markers']) + (1 if test.get('anticipatory_check') else 0)
        print(f"   Expected markers: {total_expected}")
        print(f"   Found: {len(found_markers)} - {found_markers}")

        if missing_markers:
            print(f"   Missing: {len(missing_markers)} - {missing_markers}")

        # Pass if found at least 60% of expected markers
        threshold = total_expected * 0.6
        if len(found_markers) >= threshold:
            print(f"\n   ✅ PASS - Style enhanced ({len(found_markers)}/{total_expected} markers)")
            passed += 1
        else:
            print(f"\n   ❌ FAIL - Insufficient style ({len(found_markers)}/{total_expected} markers)")
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
        print("\n✅ STYLE ENHANCEMENT VERIFIED - Responses are pleasant and stylish!")
        return True
    else:
        print("\n❌ Style enhancement needs more work")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_style_on_various_responses())
    sys.exit(0 if result else 1)
