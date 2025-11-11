"""
Research Trend Analyzer - Analyze research trends and predict future directions

Provides tools for:
- Topic evolution analysis
- Emerging topic detection
- Publication trend visualization
- Research direction prediction
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)


class ResearchTrendAnalyzer:
    """Analyze trends in academic research"""

    def __init__(self, archive_client=None):
        """
        Initialize trend analyzer

        Args:
            archive_client: ArchiveAPIClient instance for fetching papers
        """
        self.archive_client = archive_client

    def analyze_topic_evolution(self, topic: str, years: int = 10, granularity: str = "year") -> Dict[str, Any]:
        """
        Analyze how a research topic has evolved over time

        Args:
            topic: Research topic to analyze
            years: Number of years to look back
            granularity: Time granularity ("year" or "quarter")

        Returns:
            Evolution data with publication counts, citation trends, key papers
        """
        if not self.archive_client:
            return {"error": "Archive client required"}

        try:
            current_year = datetime.now().year
            start_year = current_year - years

            # Fetch papers from each year
            yearly_data = {}

            for year in range(start_year, current_year + 1):
                papers = self._fetch_papers_for_year(topic, year)

                yearly_data[year] = {
                    'year': year,
                    'paper_count': len(papers),
                    'total_citations': sum(p.get('citationCount', 0) for p in papers),
                    'avg_citations': sum(p.get('citationCount', 0) for p in papers) / max(len(papers), 1),
                    'top_papers': sorted(
                        papers,
                        key=lambda x: x.get('citationCount', 0),
                        reverse=True
                    )[:5],
                    'keywords': self._extract_trending_keywords(papers)
                }

            # Calculate growth metrics
            growth_rate = self._calculate_growth_rate(yearly_data)

            # Detect inflection points
            inflection_points = self._detect_inflection_points(yearly_data)

            # Extract emerging keywords
            emerging_keywords = self._identify_emerging_keywords(yearly_data)

            return {
                'topic': topic,
                'time_range': f'{start_year}-{current_year}',
                'yearly_data': yearly_data,
                'growth_rate': growth_rate,
                'inflection_points': inflection_points,
                'emerging_keywords': emerging_keywords,
                'trend': self._classify_trend(growth_rate)
            }

        except Exception as e:
            logger.error(f"Error analyzing topic evolution: {e}")
            return {"error": str(e)}

    def emerging_topics(self, field: str, min_papers: int = 20, time_window: int = 2) -> List[Dict[str, Any]]:
        """
        Detect emerging research topics in a field

        Args:
            field: Research field to analyze
            min_papers: Minimum papers for a topic to be considered
            time_window: Years to look back for "emerging" status

        Returns:
            List of emerging topics with growth metrics
        """
        if not self.archive_client:
            return []

        try:
            current_year = datetime.now().year
            recent_years = range(current_year - time_window, current_year + 1)
            older_years = range(current_year - time_window * 2, current_year - time_window)

            # Fetch papers from both periods
            recent_papers = []
            older_papers = []

            for year in recent_years:
                papers = self._fetch_papers_for_year(field, year, limit=200)
                recent_papers.extend(papers)

            for year in older_years:
                papers = self._fetch_papers_for_year(field, year, limit=200)
                older_papers.extend(papers)

            # Extract keywords/phrases from both periods
            recent_keywords = self._extract_all_keywords(recent_papers)
            older_keywords = self._extract_all_keywords(older_papers)

            # Find keywords with significant growth
            emerging = []

            for keyword, recent_count in recent_keywords.items():
                if recent_count < min_papers:
                    continue

                older_count = older_keywords.get(keyword, 0)

                # Calculate growth
                if older_count == 0:
                    growth = float('inf') if recent_count > 0 else 0
                else:
                    growth = (recent_count - older_count) / older_count

                # Filter for significant growth
                if growth > 1.0:  # 100% growth
                    emerging.append({
                        'topic': keyword,
                        'recent_papers': recent_count,
                        'older_papers': older_count,
                        'growth_rate': round(growth * 100, 1),
                        'status': 'emerging' if older_count < 10 else 'accelerating'
                    })

            # Sort by growth rate
            emerging.sort(key=lambda x: x['growth_rate'], reverse=True)

            return emerging[:20]  # Top 20 emerging topics

        except Exception as e:
            logger.error(f"Error detecting emerging topics: {e}")
            return []

    def predict_next_papers(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Predict/recommend next papers to read based on trends

        Args:
            topic: Research topic
            limit: Maximum papers to return

        Returns:
            List of recommended papers sorted by relevance and recency
        """
        if not self.archive_client:
            return []

        try:
            # Get recent papers (last 2 years)
            current_year = datetime.now().year
            recent_papers = []

            for year in range(current_year - 1, current_year + 1):
                papers = self._fetch_papers_for_year(topic, year, limit=50)
                recent_papers.extend(papers)

            # Score papers by multiple factors
            scored_papers = []

            for paper in recent_papers:
                score = self._calculate_relevance_score(paper)

                scored_papers.append({
                    'paper': paper,
                    'score': score,
                    'title': paper.get('title'),
                    'authors': [a.get('name') for a in paper.get('authors', [])[:3]],
                    'year': paper.get('year'),
                    'citations': paper.get('citationCount', 0),
                    'reason': self._generate_recommendation_reason(paper, score)
                })

            # Sort by score
            scored_papers.sort(key=lambda x: x['score'], reverse=True)

            return scored_papers[:limit]

        except Exception as e:
            logger.error(f"Error predicting next papers: {e}")
            return []

    def compare_research_trends(self, topics: List[str], years: int = 10) -> Dict[str, Any]:
        """
        Compare research trends across multiple topics

        Args:
            topics: List of topics to compare
            years: Number of years to analyze

        Returns:
            Comparative trend data
        """
        if not self.archive_client:
            return {"error": "Archive client required"}

        try:
            current_year = datetime.now().year
            start_year = current_year - years

            comparison = {
                'topics': topics,
                'time_range': f'{start_year}-{current_year}',
                'data': {}
            }

            # Analyze each topic
            for topic in topics:
                yearly_counts = {}

                for year in range(start_year, current_year + 1):
                    papers = self._fetch_papers_for_year(topic, year, limit=100)
                    yearly_counts[year] = len(papers)

                comparison['data'][topic] = {
                    'yearly_counts': yearly_counts,
                    'total_papers': sum(yearly_counts.values()),
                    'avg_per_year': sum(yearly_counts.values()) / len(yearly_counts),
                    'peak_year': max(yearly_counts, key=yearly_counts.get),
                    'trend': self._classify_trend(self._calculate_simple_growth_rate(yearly_counts))
                }

            # Determine leader
            leader = max(
                comparison['data'].items(),
                key=lambda x: x[1]['total_papers']
            )[0]

            comparison['leader'] = leader
            comparison['insights'] = self._generate_comparison_insights(comparison['data'])

            return comparison

        except Exception as e:
            logger.error(f"Error comparing trends: {e}")
            return {"error": str(e)}

    def _fetch_papers_for_year(self, topic: str, year: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch papers for a specific year"""
        if not self.archive_client:
            return []

        try:
            # Query with year filter
            query = f"{topic} year:{year}"

            results = self.archive_client.search_papers(
                query=query,
                limit=limit,
                fields=['paperId', 'title', 'authors', 'year', 'citationCount', 'abstract']
            )

            papers = results.get('data', [])

            # Filter by year (sometimes API returns adjacent years)
            return [p for p in papers if p.get('year') == year]

        except Exception as e:
            logger.warning(f"Could not fetch papers for {year}: {e}")
            return []

    def _extract_trending_keywords(self, papers: List[Dict[str, Any]], top_n: int = 10) -> List[str]:
        """Extract trending keywords from papers"""
        all_words = []

        for paper in papers:
            # Extract from title and abstract
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            text = text.lower()

            # Simple keyword extraction (could be enhanced with NLP)
            words = re.findall(r'\b[a-z]{4,}\b', text)  # Words 4+ chars
            all_words.extend(words)

        # Count and filter common words
        stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'using', 'which', 'their', 'they'}
        word_counts = Counter(w for w in all_words if w not in stop_words)

        return [word for word, count in word_counts.most_common(top_n)]

    def _calculate_growth_rate(self, yearly_data: Dict[int, Dict]) -> float:
        """Calculate overall growth rate"""
        years = sorted(yearly_data.keys())

        if len(years) < 2:
            return 0.0

        first_year_count = yearly_data[years[0]]['paper_count']
        last_year_count = yearly_data[years[-1]]['paper_count']

        if first_year_count == 0:
            return float('inf') if last_year_count > 0 else 0.0

        return (last_year_count - first_year_count) / first_year_count

    def _calculate_simple_growth_rate(self, yearly_counts: Dict[int, int]) -> float:
        """Calculate simple growth rate from year->count mapping"""
        years = sorted(yearly_counts.keys())

        if len(years) < 2:
            return 0.0

        first_count = yearly_counts[years[0]]
        last_count = yearly_counts[years[-1]]

        if first_count == 0:
            return float('inf') if last_count > 0 else 0.0

        return (last_count - first_count) / first_count

    def _detect_inflection_points(self, yearly_data: Dict[int, Dict]) -> List[Dict[str, Any]]:
        """Detect significant inflection points in trend"""
        inflection_points = []
        years = sorted(yearly_data.keys())

        for i in range(1, len(years) - 1):
            prev_year = years[i - 1]
            curr_year = years[i]
            next_year = years[i + 1]

            prev_count = yearly_data[prev_year]['paper_count']
            curr_count = yearly_data[curr_year]['paper_count']
            next_count = yearly_data[next_year]['paper_count']

            # Check for significant change in direction
            if curr_count > prev_count * 1.5 and curr_count > next_count:
                inflection_points.append({
                    'year': curr_year,
                    'type': 'peak',
                    'paper_count': curr_count
                })
            elif curr_count < prev_count * 0.5 and curr_count < next_count:
                inflection_points.append({
                    'year': curr_year,
                    'type': 'trough',
                    'paper_count': curr_count
                })

        return inflection_points

    def _identify_emerging_keywords(self, yearly_data: Dict[int, Dict]) -> List[Dict[str, Any]]:
        """Identify keywords that emerged recently"""
        years = sorted(yearly_data.keys())

        if len(years) < 2:
            return []

        # Compare recent vs older keywords
        recent_years = years[-3:] if len(years) >= 3 else years[-2:]
        older_years = years[:-3] if len(years) >= 3 else years[:-2]

        recent_keywords = Counter()
        older_keywords = Counter()

        for year in recent_years:
            keywords = yearly_data[year]['keywords']
            recent_keywords.update(keywords)

        for year in older_years:
            keywords = yearly_data[year]['keywords']
            older_keywords.update(keywords)

        # Find new keywords
        emerging = []
        for keyword, recent_count in recent_keywords.items():
            older_count = older_keywords.get(keyword, 0)

            if older_count == 0 and recent_count >= 2:
                emerging.append({
                    'keyword': keyword,
                    'recent_mentions': recent_count,
                    'status': 'new'
                })
            elif older_count > 0 and recent_count > older_count * 2:
                emerging.append({
                    'keyword': keyword,
                    'recent_mentions': recent_count,
                    'older_mentions': older_count,
                    'growth': round((recent_count - older_count) / older_count * 100, 1),
                    'status': 'growing'
                })

        return emerging[:10]

    def _classify_trend(self, growth_rate: float) -> str:
        """Classify trend based on growth rate"""
        if growth_rate > 1.0:
            return 'exponential_growth'
        elif growth_rate > 0.5:
            return 'strong_growth'
        elif growth_rate > 0.2:
            return 'moderate_growth'
        elif growth_rate > -0.2:
            return 'stable'
        elif growth_rate > -0.5:
            return 'declining'
        else:
            return 'strong_decline'

    def _extract_all_keywords(self, papers: List[Dict[str, Any]]) -> Counter:
        """Extract and count all keywords from papers"""
        keywords = Counter()

        for paper in papers:
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            text = text.lower()

            # Extract bigrams and trigrams (more meaningful than single words)
            words = re.findall(r'\b[a-z]+\b', text)

            # Bigrams
            for i in range(len(words) - 1):
                bigram = f"{words[i]} {words[i+1]}"
                if len(bigram) > 8:  # Filter very short bigrams
                    keywords[bigram] += 1

            # Trigrams
            for i in range(len(words) - 2):
                trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
                if len(trigram) > 12:
                    keywords[trigram] += 1

        return keywords

    def _calculate_relevance_score(self, paper: Dict[str, Any]) -> float:
        """Calculate relevance score for paper recommendation"""
        score = 0.0

        # Recency (papers from current year get boost)
        current_year = datetime.now().year
        year = paper.get('year', current_year - 10)
        recency = max(0, 1 - (current_year - year) / 10)  # 0-1 score
        score += recency * 30

        # Citations (normalize to 0-40 range)
        citations = paper.get('citationCount', 0)
        citation_score = min(citations / 100, 1.0) * 40
        score += citation_score

        # Citation velocity (citations per year)
        age = max(1, current_year - year)
        velocity = citations / age
        velocity_score = min(velocity / 50, 1.0) * 30
        score += velocity_score

        return round(score, 2)

    def _generate_recommendation_reason(self, paper: Dict[str, Any], score: float) -> str:
        """Generate human-readable reason for recommendation"""
        current_year = datetime.now().year
        year = paper.get('year', current_year)
        citations = paper.get('citationCount', 0)

        reasons = []

        if year >= current_year:
            reasons.append("Very recent")
        elif year >= current_year - 1:
            reasons.append("Recent")

        if citations > 100:
            reasons.append("Highly cited")
        elif citations > 50:
            reasons.append("Well cited")

        age = max(1, current_year - year)
        velocity = citations / age

        if velocity > 50:
            reasons.append("High impact")

        if not reasons:
            reasons.append("Relevant")

        return " · ".join(reasons)

    def _generate_comparison_insights(self, comparison_data: Dict[str, Any]) -> List[str]:
        """Generate insights from comparison data"""
        insights = []

        # Find fastest growing
        growth_rates = {
            topic: self._calculate_simple_growth_rate(data['yearly_counts'])
            for topic, data in comparison_data.items()
        }

        fastest = max(growth_rates, key=growth_rates.get)
        insights.append(f"{fastest} shows the fastest growth")

        # Find most established
        total_papers = {
            topic: data['total_papers']
            for topic, data in comparison_data.items()
        }

        most_established = max(total_papers, key=total_papers.get)
        insights.append(f"{most_established} has the most publications")

        return insights


def get_trend_analyzer(archive_client=None) -> ResearchTrendAnalyzer:
    """
    Get ResearchTrendAnalyzer instance

    Args:
        archive_client: ArchiveAPIClient instance

    Returns:
        ResearchTrendAnalyzer instance
    """
    return ResearchTrendAnalyzer(archive_client)
