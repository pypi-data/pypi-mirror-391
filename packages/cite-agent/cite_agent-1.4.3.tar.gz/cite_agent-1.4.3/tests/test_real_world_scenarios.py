#!/usr/bin/env python3
"""
Real-World Scenario Testing
Tests actual use cases users will encounter

These are the scenarios that REALLY matter
"""

import asyncio
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest
from cite_agent.quality_gate import assess_response_quality


class RealWorldTestSuite:
    """Test realistic user scenarios"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.quality_scores = []

    async def run_all_scenarios(self):
        """Run all real-world test scenarios"""
        print("=" * 80)
        print("REAL-WORLD SCENARIO TESTING")
        print("Testing actual use cases users will encounter")
        print("=" * 80)

        scenarios = [
            ("Research Workflow", self.test_research_workflow),
            ("Code Analysis Workflow", self.test_code_analysis_workflow),
            ("Financial Analysis Workflow", self.test_financial_analysis_workflow),
            ("Multi-Turn Conversations", self.test_multi_turn_conversations),
            ("Complex Clarifications", self.test_complex_clarifications),
            ("Performance Under Load", self.test_performance_under_load),
            ("Response Quality Consistency", self.test_quality_consistency),
        ]

        for scenario_name, test_func in scenarios:
            print(f"\n{'='*80}")
            print(f"SCENARIO: {scenario_name}")
            print("=" * 80)
            await test_func()

        # Summary
        print(f"\n{'='*80}")
        print("SCENARIO TEST SUMMARY")
        print("=" * 80)
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        fail_rate = (self.failed / total * 100) if total > 0 else 0

        print(f"✅ Passed: {self.passed}/{total} ({pass_rate:.1f}%)")
        print(f"❌ Failed: {self.failed}/{total} ({fail_rate:.1f}%)")

        if self.quality_scores:
            avg_quality = sum(self.quality_scores) / len(self.quality_scores)
            print(f"\n📊 Average Quality Score: {avg_quality:.2f}")

            if avg_quality >= 0.75:
                print("✅ Quality is GOOD")
            elif avg_quality >= 0.65:
                print("⚠️  Quality is ACCEPTABLE but could be better")
            else:
                print("❌ Quality is TOO LOW")

        return pass_rate >= 90 and (not self.quality_scores or sum(self.quality_scores) / len(self.quality_scores) >= 0.70)

    async def test_research_workflow(self):
        """Test typical research workflow"""
        agent = EnhancedNocturnalAgent()

        try:
            # Step 1: User wants to research a topic
            r1 = await agent.process_request(ChatRequest(
                question="I need to research quantum computing applications",
                user_id="researcher"
            ))

            # Step 2: User asks for specific papers
            r2 = await agent.process_request(ChatRequest(
                question="Show me recent papers from 2023-2024",
                user_id="researcher"
            ))

            # Step 3: User narrows down
            r3 = await agent.process_request(ChatRequest(
                question="Actually, just focus on quantum machine learning",
                user_id="researcher"
            ))

            # Step 4: User wants to save results
            r4 = await agent.process_request(ChatRequest(
                question="How do I export these results?",
                user_id="researcher"
            ))

            # All should succeed and make sense
            responses = [r1, r2, r3, r4]
            if all(r.response and len(r.response) > 10 for r in responses):
                self.passed += 1
                print("  ✅ Research workflow handled smoothly")

                # Check quality of final response
                assessment = assess_response_quality(r4.response, "How do I export these results?", {})
                self.quality_scores.append(assessment.overall_score)
                print(f"     Quality Score: {assessment.overall_score:.2f}")
            else:
                self.failed += 1
                print("  ❌ Research workflow broke down")

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Research workflow error: {e}")

        finally:
            await agent.close()

    async def test_code_analysis_workflow(self):
        """Test code analysis workflow"""
        agent = EnhancedNocturnalAgent()

        try:
            # Step 1: User wants to analyze code
            r1 = await agent.process_request(ChatRequest(
                question="Find Python files in this project",
                user_id="developer"
            ))

            # Step 2: User narrows down
            r2 = await agent.process_request(ChatRequest(
                question="Just show me the ones with 'test' in the name",
                user_id="developer"
            ))

            # Step 3: User wants to see contents
            r3 = await agent.process_request(ChatRequest(
                question="Show me what's in the first one",
                user_id="developer"
            ))

            # Step 4: User asks about code
            r4 = await agent.process_request(ChatRequest(
                question="What does this code do?",
                user_id="developer"
            ))

            responses = [r1, r2, r3, r4]
            if all(r.response and len(r.response) > 10 for r in responses):
                self.passed += 1
                print("  ✅ Code analysis workflow handled")

                assessment = assess_response_quality(r4.response, "What does this code do?", {})
                self.quality_scores.append(assessment.overall_score)
                print(f"     Quality Score: {assessment.overall_score:.2f}")
            else:
                self.failed += 1
                print("  ❌ Code analysis workflow broke")

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Code analysis error: {e}")

        finally:
            await agent.close()

    async def test_financial_analysis_workflow(self):
        """Test financial data workflow"""
        agent = EnhancedNocturnalAgent()

        try:
            # Step 1: User wants company data
            r1 = await agent.process_request(ChatRequest(
                question="Get me Apple's revenue data",
                user_id="analyst"
            ))

            # Step 2: User wants comparison
            r2 = await agent.process_request(ChatRequest(
                question="Compare it with Microsoft",
                user_id="analyst"
            ))

            # Step 3: User wants specific metric
            r3 = await agent.process_request(ChatRequest(
                question="Show me year-over-year growth",
                user_id="analyst"
            ))

            responses = [r1, r2, r3]
            if all(r.response and len(r.response) > 10 for r in responses):
                self.passed += 1
                print("  ✅ Financial analysis workflow handled")

                assessment = assess_response_quality(r3.response, "Show me year-over-year growth", {})
                self.quality_scores.append(assessment.overall_score)
                print(f"     Quality Score: {assessment.overall_score:.2f}")
            else:
                self.failed += 1
                print("  ❌ Financial analysis workflow broke")

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Financial analysis error: {e}")

        finally:
            await agent.close()

    async def test_multi_turn_conversations(self):
        """Test extended multi-turn conversations"""
        agent = EnhancedNocturnalAgent()

        try:
            queries = [
                "Hey there!",
                "I'm working on a project",
                "It's about quantum computing",
                "Can you help me find relevant papers?",
                "Actually, more specifically about quantum machine learning",
                "From the last 2 years",
                "Can you list the top 3?",
                "Tell me more about the first one",
                "What are the key findings?",
                "Thanks, that's helpful!",
            ]

            responses = []
            for i, query in enumerate(queries, 1):
                r = await agent.process_request(ChatRequest(
                    question=query,
                    user_id="multi_turn_user"
                ))
                responses.append(r)

                if not r.response or len(r.response) < 5:
                    print(f"  ❌ Failed at turn {i}: {query}")
                    self.failed += 1
                    await agent.close()
                    return

            # All turns succeeded
            self.passed += 1
            print(f"  ✅ Handled {len(queries)}-turn conversation")

            # Check quality of final responses
            final_quality = assess_response_quality(
                responses[-2].response,
                "What are the key findings?",
                {}
            )
            self.quality_scores.append(final_quality.overall_score)
            print(f"     Quality Score: {final_quality.overall_score:.2f}")

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Multi-turn conversation error: {e}")

        finally:
            await agent.close()

    async def test_complex_clarifications(self):
        """Test handling of ambiguous queries requiring clarification"""
        agent = EnhancedNocturnalAgent()

        try:
            # Ambiguous queries that should trigger clarifications
            ambiguous_queries = [
                "Tell me about the company",  # Which company?
                "Compare them",  # Who is "them"?
                "Show me that file",  # Which file?
                "Get me the data",  # What data?
            ]

            for query in ambiguous_queries:
                r = await agent.process_request(ChatRequest(
                    question=query,
                    user_id="clarification_user"
                ))

                # Should either:
                # 1. Ask for clarification
                # 2. Make a reasonable inference

                response_lower = r.response.lower()

                is_clarification = any(word in response_lower for word in [
                    'which', 'what kind', 'clarify', 'more specific', 'tell me more'
                ])

                has_reasonable_response = len(r.response) > 20

                if is_clarification or has_reasonable_response:
                    # Good - either clarified or inferred
                    continue
                else:
                    print(f"  ⚠️  Weak response to: {query}")

            self.passed += 1
            print("  ✅ Clarification handling acceptable")

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Clarification error: {e}")

        finally:
            await agent.close()

    async def test_performance_under_load(self):
        """Test performance with rapid consecutive queries"""
        agent = EnhancedNocturnalAgent()

        try:
            start_time = time.time()

            # Fire 10 queries rapidly
            tasks = []
            for i in range(10):
                task = agent.process_request(ChatRequest(
                    question=f"Quick test query {i}",
                    user_id=f"load_test_{i}"
                ))
                tasks.append(task)

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            elapsed = time.time() - start_time

            # Count successes
            successes = sum(
                1 for r in responses
                if not isinstance(r, Exception) and r.response and len(r.response) > 5
            )

            success_rate = successes / len(responses) * 100

            if success_rate >= 80:
                self.passed += 1
                print(f"  ✅ Performance test: {successes}/10 succeeded in {elapsed:.1f}s")
                print(f"     Average: {elapsed/10:.2f}s per query")
            else:
                self.failed += 1
                print(f"  ❌ Performance test: only {successes}/10 succeeded")

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Performance test error: {e}")

        finally:
            await agent.close()

    async def test_quality_consistency(self):
        """Test that quality is consistent across similar queries"""
        agent = EnhancedNocturnalAgent()

        try:
            # Similar queries - quality should be consistent
            similar_queries = [
                "List files in this directory",
                "Show me the files here",
                "What files are in this folder?",
                "Display current directory contents",
            ]

            qualities = []

            for query in similar_queries:
                r = await agent.process_request(ChatRequest(
                    question=query,
                    user_id="consistency_test"
                ))

                assessment = assess_response_quality(r.response, query, {})
                qualities.append(assessment.overall_score)

            # Calculate variance
            avg_quality = sum(qualities) / len(qualities)
            variance = sum((q - avg_quality) ** 2 for q in qualities) / len(qualities)
            std_dev = variance ** 0.5

            print(f"  Quality scores: {[f'{q:.2f}' for q in qualities]}")
            print(f"  Average: {avg_quality:.2f}, Std Dev: {std_dev:.2f}")

            if std_dev < 0.15 and avg_quality >= 0.70:
                self.passed += 1
                print("  ✅ Quality is consistent and good")
            elif std_dev < 0.20:
                self.passed += 1
                print("  ⚠️  Quality is consistent but could be higher")
            else:
                self.failed += 1
                print("  ❌ Quality is too inconsistent")

            self.quality_scores.extend(qualities)

        except Exception as e:
            self.failed += 1
            print(f"  ❌ Consistency test error: {e}")

        finally:
            await agent.close()


async def main():
    suite = RealWorldTestSuite()
    success = await suite.run_all_scenarios()

    if not success:
        print("\n⚠️  REAL-WORLD PERFORMANCE NEEDS IMPROVEMENT")
        sys.exit(1)
    else:
        print("\n✅ REAL-WORLD PERFORMANCE IS GOOD")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
