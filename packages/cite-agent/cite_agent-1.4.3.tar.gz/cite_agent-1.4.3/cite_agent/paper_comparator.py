"""
Smart Paper Comparison - Compare research papers systematically

Provides tools for:
- Comparing methodologies
- Comparing results/metrics
- Finding contradictions
- Analyzing methodology overlap
"""

from typing import List, Dict, Any, Optional
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)


class PaperComparator:
    """Compare papers across multiple dimensions"""

    def __init__(self, paper_reader=None):
        """
        Initialize paper comparator

        Args:
            paper_reader: FullPaperReader instance for reading PDFs
        """
        self.paper_reader = paper_reader

    def compare_methodologies(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare methodologies across papers

        Args:
            papers: List of paper objects with metadata

        Returns:
            Structured comparison of methodologies
        """
        if len(papers) < 2:
            return {"error": "Need at least 2 papers to compare"}

        comparison = {
            'papers': [],
            'dimensions': [],
            'comparison_table': []
        }

        # Extract methodology from each paper
        for paper in papers:
            paper_info = {
                'id': paper.get('paperId') or paper.get('doi'),
                'title': paper.get('title'),
                'year': paper.get('year'),
                'authors': [a.get('name') for a in paper.get('authors', [])[:3]]
            }

            # Try to extract methodology
            methodology = self._extract_methodology(paper)
            paper_info['methodology'] = methodology

            comparison['papers'].append(paper_info)

        # Identify common dimensions
        dimensions = self._identify_methodology_dimensions(comparison['papers'])
        comparison['dimensions'] = dimensions

        # Build comparison table
        for dimension in dimensions:
            row = {
                'dimension': dimension,
                'values': []
            }

            for paper_info in comparison['papers']:
                methodology = paper_info['methodology']
                value = self._extract_dimension_value(methodology, dimension)
                row['values'].append({
                    'paper': paper_info['title'][:50],
                    'value': value
                })

            comparison['comparison_table'].append(row)

        return comparison

    def compare_results(self, papers: List[Dict[str, Any]], metric: Optional[str] = None) -> Dict[str, Any]:
        """
        Compare numerical results/metrics across papers

        Args:
            papers: List of paper objects
            metric: Specific metric to compare (e.g., "accuracy", "F1")

        Returns:
            Comparison of numerical results
        """
        results = {
            'papers': [],
            'metrics': defaultdict(list)
        }

        for paper in papers:
            paper_id = paper.get('paperId') or paper.get('doi')
            title = paper.get('title', 'Unknown')

            # Extract all numerical results
            numbers = self._extract_numbers_from_paper(paper)

            paper_results = {
                'id': paper_id,
                'title': title,
                'year': paper.get('year'),
                'metrics': numbers
            }

            results['papers'].append(paper_results)

            # Group by metric type
            for metric_name, value in numbers.items():
                results['metrics'][metric_name].append({
                    'paper': title[:50],
                    'value': value,
                    'year': paper.get('year')
                })

        # If specific metric requested, filter
        if metric:
            metric_lower = metric.lower()
            filtered_metrics = {
                k: v for k, v in results['metrics'].items()
                if metric_lower in k.lower()
            }
            results['metrics'] = filtered_metrics

        # Add rankings
        for metric_name, values in results['metrics'].items():
            # Sort by value (higher is better for most metrics)
            sorted_values = sorted(values, key=lambda x: x['value'], reverse=True)
            for i, item in enumerate(sorted_values, 1):
                item['rank'] = i

        return results

    def find_contradictions(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Find contradicting findings across papers

        Args:
            papers: List of paper objects

        Returns:
            List of contradictions found
        """
        contradictions = []

        # Extract claims from each paper
        paper_claims = []
        for paper in papers:
            claims = self._extract_claims(paper)
            paper_claims.append({
                'paper': paper.get('title', 'Unknown'),
                'year': paper.get('year'),
                'claims': claims
            })

        # Compare claims pairwise
        for i in range(len(paper_claims)):
            for j in range(i + 1, len(paper_claims)):
                paper1 = paper_claims[i]
                paper2 = paper_claims[j]

                # Check for contradictions
                for claim1 in paper1['claims']:
                    for claim2 in paper2['claims']:
                        if self._are_contradictory(claim1, claim2):
                            contradictions.append({
                                'paper1': paper1['paper'],
                                'year1': paper1['year'],
                                'claim1': claim1,
                                'paper2': paper2['paper'],
                                'year2': paper2['year'],
                                'claim2': claim2,
                                'confidence': 'medium'  # Would need NLP for high confidence
                            })

        return contradictions

    def methodology_overlap(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze methodology overlap across papers

        Args:
            papers: List of paper objects

        Returns:
            Analysis of common techniques and unique approaches
        """
        techniques = defaultdict(list)

        # Extract techniques from each paper
        for paper in papers:
            paper_title = paper.get('title', 'Unknown')
            paper_techniques = self._extract_techniques(paper)

            for technique in paper_techniques:
                techniques[technique].append(paper_title[:50])

        # Categorize
        common_techniques = {k: v for k, v in techniques.items() if len(v) >= len(papers) / 2}
        unique_techniques = {k: v for k, v in techniques.items() if len(v) == 1}
        partial_overlap = {k: v for k, v in techniques.items() if 1 < len(v) < len(papers) / 2}

        return {
            'total_papers': len(papers),
            'common_techniques': common_techniques,  # Used by most papers
            'unique_techniques': unique_techniques,  # Used by only one paper
            'partial_overlap': partial_overlap,  # Used by some papers
            'overlap_score': len(common_techniques) / max(len(techniques), 1)
        }

    def _extract_methodology(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Extract methodology information from paper"""
        methodology = {
            'dataset': None,
            'model': None,
            'baseline': None,
            'evaluation': None
        }

        # Try abstract first
        abstract = paper.get('abstract', '')

        # Look for common methodology keywords
        if 'dataset' in abstract.lower():
            dataset_match = re.search(r'(\w+\s+dataset|\w+\s+corpus)', abstract, re.IGNORECASE)
            if dataset_match:
                methodology['dataset'] = dataset_match.group(0)

        if 'model' in abstract.lower() or 'architecture' in abstract.lower():
            model_keywords = ['transformer', 'bert', 'gpt', 'lstm', 'cnn', 'neural network']
            for keyword in model_keywords:
                if keyword.lower() in abstract.lower():
                    methodology['model'] = keyword
                    break

        if 'baseline' in abstract.lower():
            methodology['baseline'] = 'Yes (mentioned)'

        # Evaluation metrics
        metrics = ['accuracy', 'f1', 'precision', 'recall', 'bleu', 'rouge', 'perplexity']
        found_metrics = [m for m in metrics if m.lower() in abstract.lower()]
        if found_metrics:
            methodology['evaluation'] = ', '.join(found_metrics)

        return methodology

    def _identify_methodology_dimensions(self, papers: List[Dict[str, Any]]) -> List[str]:
        """Identify common methodology dimensions across papers"""
        dimensions = set()

        for paper in papers:
            methodology = paper.get('methodology', {})
            dimensions.update(methodology.keys())

        return sorted(list(dimensions))

    def _extract_dimension_value(self, methodology: Dict[str, Any], dimension: str) -> str:
        """Extract value for a specific methodology dimension"""
        value = methodology.get(dimension)
        return str(value) if value else 'Not mentioned'

    def _extract_numbers_from_paper(self, paper: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical results from paper"""
        numbers = {}
        abstract = paper.get('abstract', '')

        # Common metric patterns
        patterns = {
            'accuracy': r'accuracy[:\s]+(\d+\.?\d*)%?',
            'f1_score': r'f1[:\s]+(\d+\.?\d*)',
            'precision': r'precision[:\s]+(\d+\.?\d*)%?',
            'recall': r'recall[:\s]+(\d+\.?\d*)%?',
            'bleu': r'bleu[:\s]+(\d+\.?\d*)',
            'rouge': r'rouge[:\s]+(\d+\.?\d*)',
        }

        for metric, pattern in patterns.items():
            match = re.search(pattern, abstract, re.IGNORECASE)
            if match:
                try:
                    numbers[metric] = float(match.group(1))
                except ValueError:
                    pass

        return numbers

    def _extract_claims(self, paper: Dict[str, Any]) -> List[str]:
        """Extract key claims from paper"""
        claims = []
        abstract = paper.get('abstract', '')

        # Simple heuristic: sentences with strong verbs
        strong_verbs = ['show', 'demonstrate', 'prove', 'achieve', 'outperform', 'improve']

        sentences = abstract.split('.')
        for sentence in sentences:
            if any(verb in sentence.lower() for verb in strong_verbs):
                claims.append(sentence.strip())

        return claims[:5]  # Top 5 claims

    def _are_contradictory(self, claim1: str, claim2: str) -> bool:
        """Check if two claims contradict each other (simple heuristic)"""
        # Simple keyword-based contradiction detection
        contradictory_pairs = [
            ('outperform', 'underperform'),
            ('better', 'worse'),
            ('increase', 'decrease'),
            ('improve', 'degrade'),
            ('superior', 'inferior')
        ]

        claim1_lower = claim1.lower()
        claim2_lower = claim2.lower()

        for word1, word2 in contradictory_pairs:
            if word1 in claim1_lower and word2 in claim2_lower:
                return True
            if word2 in claim1_lower and word1 in claim2_lower:
                return True

        return False

    def _extract_techniques(self, paper: Dict[str, Any]) -> List[str]:
        """Extract methodological techniques from paper"""
        techniques = []
        abstract = paper.get('abstract', '').lower()

        # Common ML/NLP techniques
        technique_keywords = [
            'transformer', 'attention', 'bert', 'gpt', 'lstm', 'rnn', 'cnn',
            'fine-tuning', 'pre-training', 'transfer learning',
            'neural network', 'deep learning', 'reinforcement learning',
            'supervised', 'unsupervised', 'semi-supervised',
            'embedding', 'representation learning',
            'data augmentation', 'regularization', 'dropout'
        ]

        for technique in technique_keywords:
            if technique in abstract:
                techniques.append(technique.title())

        return techniques


def get_paper_comparator(paper_reader=None) -> PaperComparator:
    """
    Get PaperComparator instance

    Args:
        paper_reader: FullPaperReader instance

    Returns:
        PaperComparator instance
    """
    return PaperComparator(paper_reader)
