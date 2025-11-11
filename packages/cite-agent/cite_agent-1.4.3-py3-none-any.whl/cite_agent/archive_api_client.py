"""
Archive API Client - Wrapper for Semantic Scholar and OpenAlex APIs

Provides a unified interface for:
- Getting paper details
- Getting paper citations
- Getting paper references
- Searching papers
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)


class ArchiveAPIClient:
    """Client for accessing academic paper APIs (Semantic Scholar, OpenAlex)"""

    def __init__(self, timeout: int = 10):
        """
        Initialize API client

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.s2_base_url = "https://api.semanticscholar.org/graph/v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Cite-Agent/1.0 (Academic Research Tool)'
        })

    def get_paper(self, paper_id: str, fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get paper details from Semantic Scholar

        Args:
            paper_id: Paper ID (DOI, arXiv ID, or Semantic Scholar ID)
            fields: Fields to retrieve (default: basic metadata)

        Returns:
            Paper data or None if not found
        """
        if not fields:
            fields = ['paperId', 'title', 'authors', 'year', 'citationCount', 'abstract']

        fields_param = ','.join(fields)
        url = f"{self.s2_base_url}/paper/{quote(paper_id)}?fields={fields_param}"

        try:
            response = self.session.get(url, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Paper not found: {paper_id}")
                return None
            else:
                logger.error(f"S2 API error {response.status_code}: {response.text}")
                return None

        except requests.RequestException as e:
            logger.error(f"Request failed for paper {paper_id}: {e}")
            return None

    def get_paper_citations(self, paper_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get papers that cite this paper

        Args:
            paper_id: Paper ID
            limit: Maximum citations to return

        Returns:
            List of citing papers
        """
        url = f"{self.s2_base_url}/paper/{quote(paper_id)}/citations"
        params = {
            'limit': min(limit, 100),  # S2 API max is 100
            'fields': 'paperId,title,authors,year,citationCount'
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                citations = data.get('data', [])
                # Extract cited paper from each citation
                return [c.get('citingPaper', {}) for c in citations if 'citingPaper' in c]
            else:
                logger.warning(f"Citations request failed: {response.status_code}")
                return []

        except requests.RequestException as e:
            logger.error(f"Request failed for citations of {paper_id}: {e}")
            return []

    def get_paper_references(self, paper_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get papers referenced by this paper

        Args:
            paper_id: Paper ID
            limit: Maximum references to return

        Returns:
            List of referenced papers
        """
        url = f"{self.s2_base_url}/paper/{quote(paper_id)}/references"
        params = {
            'limit': min(limit, 100),
            'fields': 'paperId,title,authors,year,citationCount'
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                references = data.get('data', [])
                # Extract cited paper from each reference
                return [r.get('citedPaper', {}) for r in references if 'citedPaper' in r]
            else:
                logger.warning(f"References request failed: {response.status_code}")
                return []

        except requests.RequestException as e:
            logger.error(f"Request failed for references of {paper_id}: {e}")
            return []

    def search_papers(self, query: str, limit: int = 10, fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for papers

        Args:
            query: Search query
            limit: Maximum papers to return
            fields: Fields to retrieve

        Returns:
            List of papers matching query
        """
        if not fields:
            fields = ['paperId', 'title', 'authors', 'year', 'citationCount', 'abstract']

        url = f"{self.s2_base_url}/paper/search"
        params = {
            'query': query,
            'limit': min(limit, 100),
            'fields': ','.join(fields)
        }

        try:
            response = self.session.get(url, params=params, timeout=self.timeout)

            if response.status_code == 200:
                data = response.json()
                return data.get('data', [])
            else:
                logger.warning(f"Search request failed: {response.status_code}")
                return []

        except requests.RequestException as e:
            logger.error(f"Search request failed for '{query}': {e}")
            return []

    def close(self):
        """Close the session"""
        self.session.close()


def get_archive_client(timeout: int = 10) -> ArchiveAPIClient:
    """
    Get an ArchiveAPIClient instance

    Args:
        timeout: Request timeout in seconds

    Returns:
        ArchiveAPIClient instance
    """
    return ArchiveAPIClient(timeout=timeout)
