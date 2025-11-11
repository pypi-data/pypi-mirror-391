"""
Similarity Finder - Discover similar papers and researchers

Provides tools for:
- Finding similar papers
- Discovering related researchers
- Institution rankings
- Collaboration network analysis
"""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class SimilarityFinder:
    """Find similar papers and researchers"""

    def __init__(self, archive_client=None):
        """
        Initialize similarity finder

        Args:
            archive_client: ArchiveAPIClient instance
        """
        self.archive_client = archive_client

    def find_similar_papers(self, paper_id: str, limit: int = 10, method: str = "citations") -> List[Dict[str, Any]]:
        """
        Find papers similar to a given paper

        Args:
            paper_id: Paper ID (DOI, arXiv, or Semantic Scholar ID)
            limit: Maximum papers to return
            method: Similarity method ("citations", "keywords", or "authors")

        Returns:
            List of similar papers with similarity scores
        """
        if not self.archive_client:
            return []

        try:
            # Get base paper
            base_paper = self.archive_client.get_paper(
                paper_id,
                fields=['paperId', 'title', 'authors', 'year', 'citationCount', 'abstract', 'references']
            )

            if not base_paper:
                return []

            similar = []

            if method == "citations":
                similar = self._find_similar_by_citations(base_paper, limit * 2)
            elif method == "keywords":
                similar = self._find_similar_by_keywords(base_paper, limit * 2)
            elif method == "authors":
                similar = self._find_similar_by_authors(base_paper, limit * 2)
            else:
                # Hybrid approach
                citation_similar = self._find_similar_by_citations(base_paper, limit)
                keyword_similar = self._find_similar_by_keywords(base_paper, limit)
                similar = self._merge_similarity_results([citation_similar, keyword_similar])

            # Score and rank
            scored = []
            for paper in similar:
                score = self._calculate_similarity_score(base_paper, paper, method)
                scored.append({
                    **paper,
                    'similarity_score': score,
                    'similarity_reasons': self._explain_similarity(base_paper, paper)
                })

            # Sort by score and deduplicate
            scored.sort(key=lambda x: x['similarity_score'], reverse=True)

            # Remove base paper if present
            base_id = base_paper.get('paperId')
            scored = [p for p in scored if p.get('paperId') != base_id]

            return scored[:limit]

        except Exception as e:
            logger.error(f"Error finding similar papers: {e}")
            return []

    def find_similar_researchers(self, topic: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Find researchers working on a topic

        Args:
            topic: Research topic
            limit: Maximum researchers to return

        Returns:
            List of researchers with publication counts and metrics
        """
        if not self.archive_client:
            return []

        try:
            # Search for papers on topic
            results = self.archive_client.search_papers(
                query=topic,
                limit=100,
                fields=['authors', 'year', 'citationCount']
            )

            papers = results.get('data', [])

            # Aggregate by author
            author_stats = defaultdict(lambda: {
                'papers': [],
                'total_citations': 0,
                'years': set(),
                'paper_count': 0
            })

            for paper in papers:
                citations = paper.get('citationCount', 0)
                year = paper.get('year')

                for author in paper.get('authors', []):
                    author_id = author.get('authorId')
                    author_name = author.get('name')

                    if not author_name:
                        continue

                    key = author_id or author_name

                    author_stats[key]['name'] = author_name
                    author_stats[key]['author_id'] = author_id
                    author_stats[key]['papers'].append(paper)
                    author_stats[key]['total_citations'] += citations
                    if year:
                        author_stats[key]['years'].add(year)
                    author_stats[key]['paper_count'] += 1

            # Calculate metrics and rank
            researchers = []

            for key, stats in author_stats.items():
                if stats['paper_count'] < 2:  # Filter out one-time authors
                    continue

                years = sorted(list(stats['years']))
                active_years = max(years) - min(years) + 1 if len(years) > 1 else 1

                h_index = self._calculate_h_index([p.get('citationCount', 0) for p in stats['papers']])

                researchers.append({
                    'name': stats['name'],
                    'author_id': stats['author_id'],
                    'paper_count': stats['paper_count'],
                    'total_citations': stats['total_citations'],
                    'avg_citations': round(stats['total_citations'] / stats['paper_count'], 1),
                    'h_index': h_index,
                    'active_years': active_years,
                    'first_year': min(years) if years else None,
                    'latest_year': max(years) if years else None,
                    'productivity': round(stats['paper_count'] / active_years, 2),
                    'relevance_score': self._calculate_researcher_relevance(stats)
                })

            # Sort by relevance
            researchers.sort(key=lambda x: x['relevance_score'], reverse=True)

            return researchers[:limit]

        except Exception as e:
            logger.error(f"Error finding similar researchers: {e}")
            return []

    def find_collaborators(self, author_name: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Find an author's collaborators

        Args:
            author_name: Author name
            limit: Maximum collaborators to return

        Returns:
            List of co-authors with collaboration metrics
        """
        if not self.archive_client:
            return []

        try:
            # Search for author's papers
            results = self.archive_client.search_papers(
                query=f'author:"{author_name}"',
                limit=100,
                fields=['authors', 'year', 'citationCount']
            )

            papers = results.get('data', [])

            # Count co-authorships
            collaborator_stats = defaultdict(lambda: {
                'papers': [],
                'years': set(),
                'total_citations': 0
            })

            for paper in papers:
                citations = paper.get('citationCount', 0)
                year = paper.get('year')

                for author in paper.get('authors', []):
                    name = author.get('name', '')

                    # Skip the author themselves
                    if name.lower() == author_name.lower():
                        continue

                    collaborator_stats[name]['papers'].append(paper)
                    collaborator_stats[name]['total_citations'] += citations
                    if year:
                        collaborator_stats[name]['years'].add(year)

            # Format results
            collaborators = []

            for name, stats in collaborator_stats.items():
                years = sorted(list(stats['years']))

                collaborators.append({
                    'name': name,
                    'joint_papers': len(stats['papers']),
                    'total_citations': stats['total_citations'],
                    'avg_citations': round(stats['total_citations'] / len(stats['papers']), 1),
                    'first_collaboration': min(years) if years else None,
                    'latest_collaboration': max(years) if years else None,
                    'collaboration_span': max(years) - min(years) + 1 if len(years) > 1 else 1
                })

            # Sort by number of joint papers
            collaborators.sort(key=lambda x: x['joint_papers'], reverse=True)

            return collaborators[:limit]

        except Exception as e:
            logger.error(f"Error finding collaborators: {e}")
            return []

    def institution_rankings(self, topic: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Rank institutions by research output in a topic

        Args:
            topic: Research topic
            limit: Maximum institutions to return

        Returns:
            List of institutions with publication metrics
        """
        if not self.archive_client:
            return []

        try:
            # Search for papers
            results = self.archive_client.search_papers(
                query=topic,
                limit=200,
                fields=['authors', 'year', 'citationCount']
            )

            papers = results.get('data', [])

            # Extract institutions from author affiliations
            institution_stats = defaultdict(lambda: {
                'papers': [],
                'authors': set(),
                'total_citations': 0,
                'years': set()
            })

            for paper in papers:
                citations = paper.get('citationCount', 0)
                year = paper.get('year')

                for author in paper.get('authors', []):
                    # Extract institution from author info
                    # Note: Semantic Scholar doesn't always provide affiliations
                    # This is a simplified version
                    author_name = author.get('name', '')

                    # In a real implementation, would need affiliation data
                    # For now, we'll skip this or use heuristics

                    continue

            # Note: Without reliable affiliation data from API,
            # this feature is limited. Would need to:
            # 1. Use OpenAlex API which has better affiliation data
            # 2. Parse affiliations from paper metadata
            # 3. Use a separate affiliation database

            logger.warning("Institution rankings require affiliation data not available in current API")

            return []

        except Exception as e:
            logger.error(f"Error ranking institutions: {e}")
            return []

    def _find_similar_by_citations(self, base_paper: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Find papers with similar citation patterns"""
        similar = []

        try:
            # Get papers cited by this paper (references)
            references = base_paper.get('references', [])

            if not references:
                # Fallback: get references via API
                paper_id = base_paper.get('paperId')
                if paper_id:
                    references = self.archive_client.get_paper_references(paper_id, limit=50)

            # For each reference, find papers that also cite it
            # (papers with similar references are likely similar)
            for ref in references[:10]:  # Sample top references
                ref_id = ref.get('paperId')
                if ref_id:
                    citing_papers = self.archive_client.get_paper_citations(ref_id, limit=20)
                    similar.extend(citing_papers)

        except Exception as e:
            logger.warning(f"Error in citation-based similarity: {e}")

        return similar

    def _find_similar_by_keywords(self, base_paper: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Find papers with similar keywords/topics"""
        similar = []

        try:
            # Extract keywords from title and abstract
            title = base_paper.get('title', '')
            abstract = base_paper.get('abstract', '')

            # Simple keyword extraction (first 3-4 significant words)
            keywords = []

            # Extract from title
            title_words = [w for w in title.lower().split() if len(w) > 4]
            keywords.extend(title_words[:4])

            # Build search query
            query = " ".join(keywords)

            # Search for similar papers
            results = self.archive_client.search_papers(
                query=query,
                limit=limit,
                fields=['paperId', 'title', 'authors', 'year', 'citationCount', 'abstract']
            )

            similar = results.get('data', [])

        except Exception as e:
            logger.warning(f"Error in keyword-based similarity: {e}")

        return similar

    def _find_similar_by_authors(self, base_paper: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """Find papers by the same authors"""
        similar = []

        try:
            authors = base_paper.get('authors', [])

            if not authors:
                return []

            # Get papers by first author
            first_author = authors[0].get('name')

            if first_author:
                results = self.archive_client.search_papers(
                    query=f'author:"{first_author}"',
                    limit=limit,
                    fields=['paperId', 'title', 'authors', 'year', 'citationCount', 'abstract']
                )

                similar = results.get('data', [])

        except Exception as e:
            logger.warning(f"Error in author-based similarity: {e}")

        return similar

    def _merge_similarity_results(self, result_lists: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Merge and deduplicate similarity results from multiple methods"""
        seen = set()
        merged = []

        for results in result_lists:
            for paper in results:
                paper_id = paper.get('paperId')

                if not paper_id or paper_id in seen:
                    continue

                seen.add(paper_id)
                merged.append(paper)

        return merged

    def _calculate_similarity_score(self, base_paper: Dict[str, Any], candidate: Dict[str, Any], method: str) -> float:
        """Calculate similarity score between two papers"""
        score = 0.0

        # Year proximity (papers from similar years are more similar)
        base_year = base_paper.get('year', 2020)
        cand_year = candidate.get('year', 2020)
        year_diff = abs(base_year - cand_year)
        year_score = max(0, 1 - year_diff / 20) * 20
        score += year_score

        # Citation count similarity (papers with similar citation counts)
        base_cites = base_paper.get('citationCount', 0)
        cand_cites = candidate.get('citationCount', 0)

        if base_cites > 0:
            cite_ratio = min(cand_cites / base_cites, base_cites / max(cand_cites, 1))
            cite_score = cite_ratio * 30
            score += cite_score

        # Author overlap
        base_authors = {a.get('name', '').lower() for a in base_paper.get('authors', [])}
        cand_authors = {a.get('name', '').lower() for a in candidate.get('authors', [])}

        overlap = len(base_authors & cand_authors)
        author_score = min(overlap * 25, 50)
        score += author_score

        return round(score, 2)

    def _explain_similarity(self, base_paper: Dict[str, Any], candidate: Dict[str, Any]) -> List[str]:
        """Generate human-readable similarity explanations"""
        reasons = []

        # Check author overlap
        base_authors = {a.get('name', '').lower() for a in base_paper.get('authors', [])}
        cand_authors = {a.get('name', '').lower() for a in candidate.get('authors', [])}

        overlap = base_authors & cand_authors
        if overlap:
            reasons.append(f"Shared authors: {', '.join(overlap)}")

        # Check year proximity
        base_year = base_paper.get('year')
        cand_year = candidate.get('year')

        if base_year and cand_year and abs(base_year - cand_year) <= 2:
            reasons.append(f"Published around same time ({cand_year})")

        # Check citation similarity
        base_cites = base_paper.get('citationCount', 0)
        cand_cites = candidate.get('citationCount', 0)

        if base_cites > 0 and cand_cites > 0:
            ratio = cand_cites / base_cites
            if 0.5 <= ratio <= 2.0:
                reasons.append("Similar citation count")

        if not reasons:
            reasons.append("Related topic")

        return reasons

    def _calculate_h_index(self, citation_counts: List[int]) -> int:
        """Calculate h-index from citation counts"""
        citation_counts_sorted = sorted(citation_counts, reverse=True)

        h = 0
        for i, citations in enumerate(citation_counts_sorted, 1):
            if citations >= i:
                h = i
            else:
                break

        return h

    def _calculate_researcher_relevance(self, stats: Dict[str, Any]) -> float:
        """Calculate relevance score for a researcher"""
        score = 0.0

        # Number of papers
        paper_count = stats['paper_count']
        score += min(paper_count * 10, 40)

        # Total citations
        citations = stats['total_citations']
        score += min(citations / 10, 30)

        # Productivity (papers per year)
        years = len(stats['years'])
        if years > 0:
            productivity = paper_count / years
            score += min(productivity * 10, 30)

        return round(score, 2)


def get_similarity_finder(archive_client=None) -> SimilarityFinder:
    """
    Get SimilarityFinder instance

    Args:
        archive_client: ArchiveAPIClient instance

    Returns:
        SimilarityFinder instance
    """
    return SimilarityFinder(archive_client)
