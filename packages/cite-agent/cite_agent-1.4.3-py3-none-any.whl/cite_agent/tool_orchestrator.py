"""
Tool Orchestration - Intelligent Multi-Tool Chaining
Chain multiple tools together to solve complex queries

This is what separates basic execution from intelligent problem-solving
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """How to execute tools"""
    PARALLEL = "parallel"  # Execute simultaneously
    SEQUENTIAL = "sequential"  # Execute one after another
    CONDITIONAL = "conditional"  # Execute based on previous results


@dataclass
class ToolStep:
    """A single step in the orchestration plan"""
    step_id: int
    tool_name: str
    tool_params: Dict[str, Any]
    execution_mode: ExecutionMode
    depends_on: Optional[List[int]] = None  # Which steps must complete first
    condition: Optional[str] = None  # Condition for conditional execution


@dataclass
class OrchestrationPlan:
    """Complete plan for executing multiple tools"""
    steps: List[ToolStep]
    total_steps: int
    estimated_time: float  # seconds
    can_parallelize: bool


class ToolOrchestrator:
    """
    Intelligently orchestrate multiple tool executions

    Examples:
    - "Compare Apple and Microsoft revenue" → Parallel fetch both, sequential comparison
    - "Find Python files and list their functions" → Sequential (find → analyze)
    - "Search papers on X and Y" → Parallel searches, sequential synthesis
    """

    @classmethod
    async def create_plan(
        cls,
        query: str,
        context: Dict[str, Any],
        available_tools: List[str]
    ) -> OrchestrationPlan:
        """
        Create an execution plan for the query

        Args:
            query: User query
            context: Available context
            available_tools: List of available tool names

        Returns:
            Orchestration plan with steps
        """
        query_lower = query.lower()
        steps = []

        # Pattern 1: Comparison queries
        if any(word in query_lower for word in ['compare', 'versus', 'vs']):
            plan = cls._plan_comparison(query, available_tools)
            return plan

        # Pattern 2: Multi-entity search
        if 'and' in query_lower and any(word in query_lower for word in ['search', 'find', 'get']):
            plan = cls._plan_multi_search(query, available_tools)
            return plan

        # Pattern 3: Sequential analysis
        if any(word in query_lower for word in ['then', 'after that', 'next']):
            plan = cls._plan_sequential_tasks(query, available_tools)
            return plan

        # Pattern 4: Data aggregation
        if any(word in query_lower for word in ['total', 'sum', 'average', 'aggregate']):
            plan = cls._plan_aggregation(query, available_tools)
            return plan

        # Default: Single-step plan
        return OrchestrationPlan(
            steps=[ToolStep(
                step_id=1,
                tool_name=cls._infer_primary_tool(query, available_tools),
                tool_params={'query': query},
                execution_mode=ExecutionMode.SEQUENTIAL
            )],
            total_steps=1,
            estimated_time=2.0,
            can_parallelize=False
        )

    @classmethod
    def _plan_comparison(cls, query: str, available_tools: List[str]) -> OrchestrationPlan:
        """
        Plan for comparison queries

        Example: "Compare Apple and Microsoft revenue"
        Plan:
        1. [PARALLEL] Fetch Apple data
        2. [PARALLEL] Fetch Microsoft data
        3. [SEQUENTIAL] Compare results
        """
        # Extract entities being compared
        entities = cls._extract_entities_for_comparison(query)

        steps = []

        # Step 1 & 2: Fetch data in parallel
        for i, entity in enumerate(entities, 1):
            tool = cls._infer_tool_for_entity(entity, available_tools)
            steps.append(ToolStep(
                step_id=i,
                tool_name=tool,
                tool_params={'query': entity},
                execution_mode=ExecutionMode.PARALLEL
            ))

        # Step 3: Compare (sequential, depends on previous steps)
        steps.append(ToolStep(
            step_id=len(entities) + 1,
            tool_name='synthesize',
            tool_params={'operation': 'compare'},
            execution_mode=ExecutionMode.SEQUENTIAL,
            depends_on=list(range(1, len(entities) + 1))
        ))

        return OrchestrationPlan(
            steps=steps,
            total_steps=len(steps),
            estimated_time=3.0,  # Parallel saves time
            can_parallelize=True
        )

    @classmethod
    def _plan_multi_search(cls, query: str, available_tools: List[str]) -> OrchestrationPlan:
        """
        Plan for multiple parallel searches

        Example: "Search for papers on quantum computing and machine learning"
        Plan:
        1. [PARALLEL] Search quantum computing
        2. [PARALLEL] Search machine learning
        3. [SEQUENTIAL] Synthesize results
        """
        # Extract search terms
        terms = cls._extract_search_terms(query)

        steps = []

        # Parallel search steps
        for i, term in enumerate(terms, 1):
            steps.append(ToolStep(
                step_id=i,
                tool_name='archive_search',
                tool_params={'query': term},
                execution_mode=ExecutionMode.PARALLEL
            ))

        # Synthesis step
        steps.append(ToolStep(
            step_id=len(terms) + 1,
            tool_name='synthesize',
            tool_params={'operation': 'combine'},
            execution_mode=ExecutionMode.SEQUENTIAL,
            depends_on=list(range(1, len(terms) + 1))
        ))

        return OrchestrationPlan(
            steps=steps,
            total_steps=len(steps),
            estimated_time=4.0,
            can_parallelize=True
        )

    @classmethod
    def _plan_sequential_tasks(cls, query: str, available_tools: List[str]) -> OrchestrationPlan:
        """
        Plan for sequential tasks

        Example: "Find Python files then analyze them for bugs"
        Plan:
        1. [SEQUENTIAL] Find Python files
        2. [SEQUENTIAL] Analyze files (depends on step 1)
        """
        # Parse sequential steps from query
        parts = query.lower().split('then')

        steps = []

        for i, part in enumerate(parts, 1):
            tool = cls._infer_primary_tool(part.strip(), available_tools)
            depends_on = [i-1] if i > 1 else None

            steps.append(ToolStep(
                step_id=i,
                tool_name=tool,
                tool_params={'query': part.strip()},
                execution_mode=ExecutionMode.SEQUENTIAL,
                depends_on=depends_on
            ))

        return OrchestrationPlan(
            steps=steps,
            total_steps=len(steps),
            estimated_time=len(steps) * 2.0,
            can_parallelize=False
        )

    @classmethod
    def _plan_aggregation(cls, query: str, available_tools: List[str]) -> OrchestrationPlan:
        """
        Plan for data aggregation queries

        Example: "Get total revenue for Apple for all quarters"
        Plan:
        1. [PARALLEL] Fetch Q1 data
        2. [PARALLEL] Fetch Q2 data
        3. [PARALLEL] Fetch Q3 data
        4. [PARALLEL] Fetch Q4 data
        5. [SEQUENTIAL] Aggregate results
        """
        # Identify what needs aggregation
        # For now, simple plan
        return OrchestrationPlan(
            steps=[
                ToolStep(
                    step_id=1,
                    tool_name='finsight_search',
                    tool_params={'query': query},
                    execution_mode=ExecutionMode.SEQUENTIAL
                )
            ],
            total_steps=1,
            estimated_time=2.0,
            can_parallelize=False
        )

    @classmethod
    async def execute_plan(
        cls,
        plan: OrchestrationPlan,
        tool_executor: Any  # The agent that can execute tools
    ) -> Dict[str, Any]:
        """
        Execute the orchestration plan

        Args:
            plan: The orchestration plan
            tool_executor: Object with methods to execute tools

        Returns:
            Results from all steps
        """
        results = {}
        pending_steps = plan.steps.copy()

        while pending_steps:
            # Find steps that can execute now (dependencies met)
            ready_steps = [
                step for step in pending_steps
                if not step.depends_on or all(dep in results for dep in step.depends_on)
            ]

            if not ready_steps:
                logger.error("Orchestration deadlock - no steps can execute")
                break

            # Group by execution mode
            parallel_steps = [s for s in ready_steps if s.execution_mode == ExecutionMode.PARALLEL]
            sequential_steps = [s for s in ready_steps if s.execution_mode == ExecutionMode.SEQUENTIAL]

            # Execute parallel steps
            if parallel_steps:
                tasks = []
                for step in parallel_steps:
                    task = cls._execute_tool(step, tool_executor, results)
                    tasks.append((step.step_id, task))

                # Wait for all parallel tasks
                for step_id, task in tasks:
                    result = await task
                    results[step_id] = result

                # Remove completed steps
                for step in parallel_steps:
                    pending_steps.remove(step)

            # Execute sequential steps (one at a time)
            for step in sequential_steps:
                result = await cls._execute_tool(step, tool_executor, results)
                results[step.step_id] = result
                pending_steps.remove(step)

        return results

    @classmethod
    async def _execute_tool(
        cls,
        step: ToolStep,
        tool_executor: Any,
        previous_results: Dict[int, Any]
    ) -> Any:
        """Execute a single tool step"""
        # Get dependencies if needed
        dependencies = {}
        if step.depends_on:
            dependencies = {
                dep_id: previous_results[dep_id]
                for dep_id in step.depends_on
                if dep_id in previous_results
            }

        # Execute the tool
        logger.info(f"Executing step {step.step_id}: {step.tool_name}")

        # Call the appropriate method on tool_executor
        if hasattr(tool_executor, step.tool_name):
            method = getattr(tool_executor, step.tool_name)
            result = await method(**step.tool_params, dependencies=dependencies)
        else:
            logger.warning(f"Tool {step.tool_name} not found")
            result = {"error": f"Tool {step.tool_name} not available"}

        return result

    # Helper methods for parsing queries

    @classmethod
    def _extract_entities_for_comparison(cls, query: str) -> List[str]:
        """Extract entities being compared"""
        # Simple extraction (could be more sophisticated)
        query_lower = query.lower()

        # Remove comparison words
        for word in ['compare', 'versus', 'vs', 'vs.', 'and']:
            query_lower = query_lower.replace(word, ' ')

        # Split and clean
        parts = [p.strip() for p in query_lower.split() if len(p.strip()) > 2]

        # Return first two meaningful terms (could be improved)
        return parts[:2] if len(parts) >= 2 else parts

    @classmethod
    def _extract_search_terms(cls, query: str) -> List[str]:
        """Extract multiple search terms from query"""
        # Split on 'and'
        if ' and ' in query.lower():
            parts = query.lower().split(' and ')
            return [p.strip() for p in parts if len(p.strip()) > 3]

        return [query]

    @classmethod
    def _infer_primary_tool(cls, query: str, available_tools: List[str]) -> str:
        """Infer which tool to use for a query"""
        query_lower = query.lower()

        if any(word in query_lower for word in ['paper', 'research', 'study']):
            return 'archive_search'

        if any(word in query_lower for word in ['revenue', 'stock', 'company', 'financial']):
            return 'finsight_search'

        if any(word in query_lower for word in ['file', 'directory', 'code']):
            return 'shell_command'

        return 'web_search'

    @classmethod
    def _infer_tool_for_entity(cls, entity: str, available_tools: List[str]) -> str:
        """Infer which tool to use for a specific entity"""
        # Check if it's a company name or financial term
        # For now, simple heuristic
        return 'finsight_search'


# Convenience function
async def orchestrate_tools(query: str, context: Dict[str, Any], agent: Any) -> Dict[str, Any]:
    """
    Quick tool orchestration

    Args:
        query: User query
        context: Available context
        agent: Agent object that can execute tools

    Returns:
        Results from orchestrated execution
    """
    available_tools = [
        'archive_search', 'finsight_search', 'shell_command',
        'web_search', 'synthesize'
    ]

    plan = await ToolOrchestrator.create_plan(query, context, available_tools)
    logger.info(f"Created orchestration plan with {plan.total_steps} steps")

    results = await ToolOrchestrator.execute_plan(plan, agent)
    return results
