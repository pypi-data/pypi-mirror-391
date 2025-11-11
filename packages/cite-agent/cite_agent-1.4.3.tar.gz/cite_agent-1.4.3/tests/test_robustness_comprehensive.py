#!/usr/bin/env python3
"""
Comprehensive Robustness Testing
Tests EVERYTHING that could possibly break

Goal: < 10% failure rate across ALL edge cases
"""

import asyncio
import sys
from pathlib import Path
import traceback

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest


class RobustnessTestSuite:
    """Brutal test suite designed to break things"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    async def run_all_tests(self):
        """Run every brutal test we can think of"""
        print("=" * 80)
        print("COMPREHENSIVE ROBUSTNESS TEST SUITE")
        print("Goal: < 10% failure rate")
        print("=" * 80)

        test_categories = [
            ("Edge Case Inputs", self.test_edge_case_inputs),
            ("Malformed Inputs", self.test_malformed_inputs),
            ("Extreme Inputs", self.test_extreme_inputs),
            ("Ambiguous Inputs", self.test_ambiguous_inputs),
            ("Contradictory Inputs", self.test_contradictory_inputs),
            ("Context Switches", self.test_context_switches),
            ("Multiple Questions", self.test_multiple_questions),
            ("Special Characters", self.test_special_characters),
            ("Error Recovery", self.test_error_recovery),
            ("Concurrent Handling", self.test_concurrent_handling),
        ]

        for category_name, test_func in test_categories:
            print(f"\n{'='*80}")
            print(f"TESTING: {category_name}")
            print("=" * 80)
            await test_func()

        # Summary
        print(f"\n{'='*80}")
        print("TEST SUMMARY")
        print("=" * 80)
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        fail_rate = (self.failed / total * 100) if total > 0 else 0

        print(f"✅ Passed: {self.passed}/{total} ({pass_rate:.1f}%)")
        print(f"❌ Failed: {self.failed}/{total} ({fail_rate:.1f}%)")

        if fail_rate > 10:
            print(f"\n⚠️  FAIL RATE TOO HIGH: {fail_rate:.1f}% (target: < 10%)")
        else:
            print(f"\n✅ PASS RATE ACCEPTABLE: {fail_rate:.1f}% failure rate")

        if self.errors:
            print(f"\n{'='*80}")
            print("ERRORS ENCOUNTERED")
            print("=" * 80)
            for i, error in enumerate(self.errors[:10], 1):  # Show first 10
                print(f"\n{i}. {error['test']}")
                print(f"   Input: {error['input'][:100]}")
                print(f"   Error: {error['error']}")

        return fail_rate <= 10  # Return True if acceptable

    async def _test_query(self, test_name: str, query: str, should_succeed: bool = True) -> bool:
        """Test a single query and track results"""
        agent = EnhancedNocturnalAgent()

        try:
            request = ChatRequest(question=query, user_id="test_robustness")
            response = await agent.process_request(request)

            # Check response quality
            if not response.response:
                raise ValueError("Empty response")

            if len(response.response) < 5:
                raise ValueError("Response too short")

            # Check for technical errors leaked
            bad_terms = ['traceback', 'exception:', 'tls_error', 'certificate_verify']
            response_lower = response.response.lower()

            if any(term in response_lower for term in bad_terms):
                raise ValueError(f"Technical error leaked: {response.response[:200]}")

            # Success
            self.passed += 1
            print(f"  ✅ {test_name}")
            return True

        except Exception as e:
            self.failed += 1
            self.errors.append({
                'test': test_name,
                'input': query,
                'error': str(e)
            })
            print(f"  ❌ {test_name}: {str(e)[:100]}")
            return False

        finally:
            await agent.close()

    async def test_edge_case_inputs(self):
        """Test edge cases"""
        tests = [
            ("Empty string", ""),
            ("Single space", " "),
            ("Only whitespace", "   \n  \t  "),
            ("Just punctuation", "???!!!"),
            ("Single character", "a"),
            ("Very short", "hi"),
            ("Just emoji", "😀😀😀"),
            ("Just numbers", "123456"),
            ("Just symbols", "!@#$%^&*()"),
        ]

        for test_name, query in tests:
            await self._test_query(test_name, query)

    async def test_malformed_inputs(self):
        """Test malformed/invalid inputs"""
        tests = [
            ("Incomplete sentence", "What is the"),
            ("No verb", "apple microsoft revenue"),
            ("Random words", "banana telescope refrigerator quantum"),
            ("Mixed languages", "Hello 你好 Bonjour"),
            ("Broken unicode", "Hello\x00World"),
            ("SQL injection attempt", "'; DROP TABLE users; --"),
            ("Script tag", "<script>alert('xss')</script>"),
            ("Path traversal", "../../../etc/passwd"),
            ("Null bytes", "hello\x00world"),
        ]

        for test_name, query in tests:
            await self._test_query(test_name, query)

    async def test_extreme_inputs(self):
        """Test extreme inputs"""
        tests = [
            ("Very long query", "What is " + "very " * 500 + "long question?"),
            ("Repeated characters", "a" * 1000),
            ("Many questions", " ".join(["What?"] * 100)),
            ("Deep nesting", "(" * 100 + "question" + ")" * 100),
            ("All caps", "WHAT IS THE ANSWER TO EVERYTHING"),
            ("No spaces", "whatistheanswertothisquestionwithoutanyspaces"),
        ]

        for test_name, query in tests:
            await self._test_query(test_name, query)

    async def test_ambiguous_inputs(self):
        """Test ambiguous queries"""
        tests = [
            ("Just pronoun", "it"),
            ("Vague pronoun", "What about that?"),
            ("No context pronoun", "Tell me about those"),
            ("Incomplete reference", "Compare them"),
            ("Unclear intent", "Do the thing"),
            ("Contradictory pronouns", "Show me this but not that"),
        ]

        for test_name, query in tests:
            await self._test_query(test_name, query)

    async def test_contradictory_inputs(self):
        """Test contradictory instructions"""
        tests = [
            ("Be brief but detailed", "Explain quantum physics briefly but in great detail"),
            ("Show and hide", "Show me all files but hide Python files"),
            ("Do and don't", "Search for papers but don't use the archive"),
            ("Contradictory comparison", "Compare Apple and Microsoft but only show Apple"),
        ]

        for test_name, query in tests:
            await self._test_query(test_name, query)

    async def test_context_switches(self):
        """Test sudden context switches"""
        agent = EnhancedNocturnalAgent()

        try:
            # Start with one topic
            r1 = await agent.process_request(ChatRequest(
                question="What is quantum computing?",
                user_id="test_context"
            ))

            # Sudden switch
            r2 = await agent.process_request(ChatRequest(
                question="Actually, tell me about pizza recipes",
                user_id="test_context"
            ))

            # Another switch
            r3 = await agent.process_request(ChatRequest(
                question="No wait, list Python files",
                user_id="test_context"
            ))

            # Check all responses are valid
            if all(r.response and len(r.response) > 5 for r in [r1, r2, r3]):
                self.passed += 1
                print("  ✅ Context switches handled")
            else:
                self.failed += 1
                print("  ❌ Context switches broke agent")

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Context switches: {e}")

        finally:
            await agent.close()

    async def test_multiple_questions(self):
        """Test multiple questions in one query"""
        tests = [
            ("Two questions", "What is X? And what is Y?"),
            ("Three questions", "Tell me about A. Also B. And C?"),
            ("Many questions", "What? Why? How? When? Where? Who?"),
            ("Nested questions", "What is X (and why does it matter)?"),
        ]

        for test_name, query in tests:
            await self._test_query(test_name, query)

    async def test_special_characters(self):
        """Test special characters"""
        tests = [
            ("Quotes", 'What is "test" and \'test\'?'),
            ("Backticks", "Show me `code` examples"),
            ("Brackets", "What about [this] and {that}?"),
            ("Math symbols", "What is 2+2 and x/y?"),
            ("Currency", "Show me $100 vs €50 vs ¥1000"),
            ("Unicode", "What is café and naïve?"),
            ("Arrows", "Show me A→B and X←Y"),
            ("Newlines", "First line\nSecond line\nThird line"),
        ]

        for test_name, query in tests:
            await self._test_query(test_name, query)

    async def test_error_recovery(self):
        """Test recovery from errors"""
        agent = EnhancedNocturnalAgent()

        try:
            # Cause an error (invalid query)
            r1 = await agent.process_request(ChatRequest(
                question="",
                user_id="test_recovery"
            ))

            # Try a valid query after
            r2 = await agent.process_request(ChatRequest(
                question="Hello",
                user_id="test_recovery"
            ))

            # Should still work
            if r2.response and len(r2.response) > 5:
                self.passed += 1
                print("  ✅ Recovered from error")
            else:
                self.failed += 1
                print("  ❌ Failed to recover from error")

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Error recovery: {e}")

        finally:
            await agent.close()

    async def test_concurrent_handling(self):
        """Test concurrent requests"""
        agent = EnhancedNocturnalAgent()

        try:
            # Fire 5 requests concurrently
            tasks = [
                agent.process_request(ChatRequest(
                    question=f"Query {i}",
                    user_id=f"test_concurrent_{i}"
                ))
                for i in range(5)
            ]

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            # Check how many succeeded
            successes = sum(1 for r in responses if not isinstance(r, Exception) and r.response)

            if successes >= 4:  # At least 4/5 should succeed
                self.passed += 1
                print(f"  ✅ Concurrent handling: {successes}/5 succeeded")
            else:
                self.failed += 1
                print(f"  ❌ Concurrent handling: only {successes}/5 succeeded")

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Concurrent handling: {e}")

        finally:
            await agent.close()


async def main():
    suite = RobustnessTestSuite()
    success = await suite.run_all_tests()

    if not success:
        print("\n⚠️  ROBUSTNESS INSUFFICIENT - NEEDS MORE WORK")
        sys.exit(1)
    else:
        print("\n✅ ROBUSTNESS ACCEPTABLE")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
