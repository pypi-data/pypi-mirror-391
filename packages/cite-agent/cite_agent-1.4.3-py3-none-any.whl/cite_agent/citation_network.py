"""
Citation Network Mapper - Find foundational papers and research lineages

Provides tools for:
- Mapping citation networks
- Finding seminal papers
- Tracing research lineage
- Suggesting reading order
"""

from typing import List, Dict, Any, Optional, Set, Tuple
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class CitationNetwork:
    """Maps and analyzes citation networks between papers"""

    def __init__(self, archive_client=None):
        """
        Initialize citation network mapper

        Args:
            archive_client: ArchiveAPIClient instance for fetching citation data
        """
        self.archive_client = archive_client
        self._citation_cache = {}
        self._reference_cache = {}

    def map_citations(self, paper_id: str, depth: int = 1, max_papers: int = 50) -> Dict[str, Any]:
        """
        Map citation network for a paper

        Args:
            paper_id: DOI, arXiv ID, or Semantic Scholar ID
            depth: How many citation levels to traverse (1-3)
            max_papers: Maximum papers to include

        Returns:
            Dictionary with nodes (papers) and edges (citations)
        """
        if not self.archive_client:
            logger.warning("No archive client provided - citation mapping unavailable")
            return {"nodes": [], "edges": [], "error": "Archive client required"}

        try:
            # Get base paper
            base_paper = self._fetch_paper(paper_id)
            if not base_paper:
                return {"nodes": [], "edges": [], "error": f"Paper {paper_id} not found"}

            nodes = []
            edges = []
            visited = set()

            # BFS traversal
            queue = deque([(base_paper, 0)])  # (paper, current_depth)

            while queue and len(nodes) < max_papers:
                paper, current_depth = queue.popleft()
                paper_id = paper.get('paperId') or paper.get('id')

                if not paper_id or paper_id in visited:
                    continue

                visited.add(paper_id)

                # Add node
                nodes.append({
                    'id': paper_id,
                    'title': paper.get('title', 'Unknown'),
                    'year': paper.get('year'),
                    'citationCount': paper.get('citationCount', 0),
                    'authors': [a.get('name') for a in paper.get('authors', [])[:3]],
                    'depth': current_depth
                })

                # Get citations if within depth limit
                if current_depth < depth:
                    citations = self._fetch_citations(paper_id)
                    for cited_paper in citations[:20]:  # Limit per paper
                        cited_id = cited_paper.get('paperId') or cited_paper.get('id')
                        if cited_id and cited_id not in visited:
                            edges.append({
                                'source': paper_id,
                                'target': cited_id,
                                'type': 'cites'
                            })
                            queue.append((cited_paper, current_depth + 1))

            return {
                'nodes': nodes,
                'edges': edges,
                'stats': {
                    'total_papers': len(nodes),
                    'total_citations': len(edges),
                    'max_depth': depth,
                    'most_cited': max(nodes, key=lambda x: x['citationCount']) if nodes else None
                }
            }

        except Exception as e:
            logger.error(f"Error mapping citations: {e}")
            return {"nodes": [], "edges": [], "error": str(e)}

    def find_seminal_papers(self, topic: str, min_citations: int = 100, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Find foundational/seminal papers in a field

        Args:
            topic: Research topic or query
            min_citations: Minimum citation count
            limit: Maximum papers to return

        Returns:
            List of highly-cited foundational papers
        """
        if not self.archive_client:
            return []

        try:
            # Search for papers
            results = self.archive_client.search_papers(
                query=topic,
                limit=limit * 2,  # Get more to filter
                fields=['title', 'authors', 'year', 'citationCount', 'abstract', 'paperId']
            )

            papers = results.get('data', [])

            # Filter by citation count and sort
            seminal = [p for p in papers if p.get('citationCount', 0) >= min_citations]
            seminal.sort(key=lambda x: x.get('citationCount', 0), reverse=True)

            # Enhance with network metrics
            enhanced = []
            for paper in seminal[:limit]:
                paper_id = paper.get('paperId') or paper.get('id')

                # Get citation velocity (citations per year)
                year = paper.get('year', 2024)
                age = max(1, 2025 - year)
                citations = paper.get('citationCount', 0)
                velocity = citations / age

                enhanced.append({
                    'id': paper_id,
                    'title': paper.get('title'),
                    'authors': [a.get('name') for a in paper.get('authors', [])[:5]],
                    'year': year,
                    'citations': citations,
                    'citation_velocity': round(velocity, 1),
                    'abstract': paper.get('abstract', '')[:300],
                    'influential': citations > min_citations * 2  # Highly influential
                })

            return enhanced

        except Exception as e:
            logger.error(f"Error finding seminal papers: {e}")
            return []

    def trace_research_lineage(self, paper1_id: str, paper2_id: str, max_depth: int = 4) -> Dict[str, Any]:
        """
        Find citation path between two papers

        Args:
            paper1_id: First paper ID
            paper2_id: Second paper ID
            max_depth: Maximum path length to search

        Returns:
            Shortest citation path between papers
        """
        if not self.archive_client:
            return {"path": [], "error": "Archive client required"}

        try:
            # BFS to find shortest path
            queue = deque([(paper1_id, [paper1_id])])
            visited = {paper1_id}

            while queue:
                current_id, path = queue.popleft()

                if len(path) > max_depth:
                    continue

                if current_id == paper2_id:
                    # Found path! Get paper details
                    detailed_path = []
                    for pid in path:
                        paper = self._fetch_paper(pid)
                        if paper:
                            detailed_path.append({
                                'id': pid,
                                'title': paper.get('title'),
                                'year': paper.get('year'),
                                'authors': [a.get('name') for a in paper.get('authors', [])[:3]]
                            })

                    return {
                        'path': detailed_path,
                        'length': len(path) - 1,
                        'connection_type': 'direct' if len(path) == 2 else 'indirect'
                    }

                # Explore citations and references
                citations = self._fetch_citations(current_id)
                references = self._fetch_references(current_id)

                for paper in citations + references:
                    paper_id = paper.get('paperId') or paper.get('id')
                    if paper_id and paper_id not in visited:
                        visited.add(paper_id)
                        queue.append((paper_id, path + [paper_id]))

            return {
                'path': [],
                'error': f'No citation path found within {max_depth} steps'
            }

        except Exception as e:
            logger.error(f"Error tracing lineage: {e}")
            return {"path": [], "error": str(e)}

    def suggest_reading_order(self, paper_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Suggest optimal reading order based on citations

        Args:
            paper_ids: List of paper IDs to order

        Returns:
            Papers sorted by foundational-to-recent order
        """
        if not self.archive_client:
            return []

        try:
            # Fetch all papers
            papers = []
            for pid in paper_ids:
                paper = self._fetch_paper(pid)
                if paper:
                    papers.append(paper)

            # Build citation graph
            citation_graph = defaultdict(set)

            for paper in papers:
                paper_id = paper.get('paperId') or paper.get('id')
                references = self._fetch_references(paper_id)

                for ref in references:
                    ref_id = ref.get('paperId') or ref.get('id')
                    if ref_id in paper_ids:
                        citation_graph[paper_id].add(ref_id)

            # Topological sort (foundational papers first)
            ordered = []
            visited = set()

            def dfs(paper_id):
                if paper_id in visited:
                    return
                visited.add(paper_id)

                # Visit dependencies first
                for dep_id in citation_graph.get(paper_id, []):
                    dfs(dep_id)

                # Find paper details
                paper = next((p for p in papers if p.get('paperId') == paper_id or p.get('id') == paper_id), None)
                if paper and paper not in ordered:
                    ordered.append(paper)

            # Process all papers
            for paper in papers:
                paper_id = paper.get('paperId') or paper.get('id')
                dfs(paper_id)

            # Format output
            result = []
            for i, paper in enumerate(ordered, 1):
                result.append({
                    'order': i,
                    'id': paper.get('paperId') or paper.get('id'),
                    'title': paper.get('title'),
                    'year': paper.get('year'),
                    'authors': [a.get('name') for a in paper.get('authors', [])[:3]],
                    'reason': 'Foundational' if i <= len(ordered) // 3 else 'Recent' if i > 2 * len(ordered) // 3 else 'Core'
                })

            return result

        except Exception as e:
            logger.error(f"Error suggesting reading order: {e}")
            return []

    def _fetch_paper(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Fetch paper details from API or cache"""
        if paper_id in self._citation_cache:
            return self._citation_cache[paper_id]

        if not self.archive_client:
            return None

        try:
            result = self.archive_client.get_paper(
                paper_id,
                fields=['paperId', 'title', 'authors', 'year', 'citationCount', 'abstract']
            )

            if result:
                self._citation_cache[paper_id] = result
                return result

        except Exception as e:
            logger.warning(f"Could not fetch paper {paper_id}: {e}")

        return None

    def _fetch_citations(self, paper_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch papers citing this paper"""
        if paper_id in self._citation_cache:
            cached = self._citation_cache[paper_id]
            if 'citations' in cached:
                return cached['citations']

        if not self.archive_client:
            return []

        try:
            # Semantic Scholar API: /paper/{id}/citations
            citations = self.archive_client.get_paper_citations(paper_id, limit=limit)
            return citations if citations else []

        except Exception as e:
            logger.warning(f"Could not fetch citations for {paper_id}: {e}")
            return []

    def _fetch_references(self, paper_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch papers referenced by this paper"""
        if paper_id in self._reference_cache:
            return self._reference_cache[paper_id]

        if not self.archive_client:
            return []

        try:
            # Semantic Scholar API: /paper/{id}/references
            references = self.archive_client.get_paper_references(paper_id, limit=limit)

            if references:
                self._reference_cache[paper_id] = references
                return references

        except Exception as e:
            logger.warning(f"Could not fetch references for {paper_id}: {e}")

        return []


def get_citation_network(archive_client=None) -> CitationNetwork:
    """
    Get CitationNetwork instance

    Args:
        archive_client: ArchiveAPIClient instance

    Returns:
        CitationNetwork instance
    """
    return CitationNetwork(archive_client)
