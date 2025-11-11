#!/usr/bin/env python3
"""
Tests for new high-ROI features:
- Citation Network Mapper
- Smart Paper Comparison
- Enhanced Export Formats
- Research Trend Analyzer
- Similarity Finder
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from cite_agent.citation_network import CitationNetwork, get_citation_network
from cite_agent.paper_comparator import PaperComparator, get_paper_comparator
from cite_agent.trend_analyzer import ResearchTrendAnalyzer, get_trend_analyzer
from cite_agent.similarity_finder import SimilarityFinder, get_similarity_finder
from cite_agent.workflow import Paper


class TestCitationNetwork:
    """Test citation network mapping"""

    def test_citation_network_initialization(self):
        """Test that citation network can be initialized"""
        network = get_citation_network()
        assert network is not None
        assert isinstance(network, CitationNetwork)

    def test_map_citations_without_client(self):
        """Test citation mapping with no client returns error"""
        network = CitationNetwork(archive_client=None)
        result = network.map_citations("test_id")

        assert "error" in result
        assert len(result['nodes']) == 0
        assert len(result['edges']) == 0

    def test_find_seminal_papers_without_client(self):
        """Test seminal paper finding with no client"""
        network = CitationNetwork(archive_client=None)
        result = network.find_seminal_papers("machine learning")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_trace_lineage_without_client(self):
        """Test lineage tracing with no client"""
        network = CitationNetwork(archive_client=None)
        result = network.trace_research_lineage("paper1", "paper2")

        assert "error" in result
        assert len(result['path']) == 0

    def test_suggest_reading_order_without_client(self):
        """Test reading order suggestion with no client"""
        network = CitationNetwork(archive_client=None)
        result = network.suggest_reading_order(["paper1", "paper2"])

        assert isinstance(result, list)
        assert len(result) == 0


class TestPaperComparator:
    """Test paper comparison functionality"""

    def test_paper_comparator_initialization(self):
        """Test that paper comparator can be initialized"""
        comparator = get_paper_comparator()
        assert comparator is not None
        assert isinstance(comparator, PaperComparator)

    def test_compare_methodologies_insufficient_papers(self):
        """Test methodology comparison with too few papers"""
        comparator = PaperComparator()
        result = comparator.compare_methodologies([{"title": "One Paper"}])

        assert "error" in result

    def test_compare_methodologies_with_papers(self):
        """Test methodology comparison with valid papers"""
        comparator = PaperComparator()

        papers = [
            {
                "paperId": "1",
                "title": "Transformers for NLP",
                "year": 2020,
                "authors": [{"name": "Author A"}],
                "abstract": "We use transformer model on ImageNet dataset with accuracy evaluation"
            },
            {
                "paperId": "2",
                "title": "BERT for Text Classification",
                "year": 2021,
                "authors": [{"name": "Author B"}],
                "abstract": "We apply BERT model on text corpus with F1 score evaluation"
            }
        ]

        result = comparator.compare_methodologies(papers)

        assert "papers" in result
        assert "dimensions" in result
        assert "comparison_table" in result
        assert len(result['papers']) == 2

    def test_compare_results_extracts_metrics(self):
        """Test that numerical results are extracted"""
        comparator = PaperComparator()

        papers = [
            {
                "paperId": "1",
                "title": "Paper 1",
                "year": 2020,
                "abstract": "We achieved accuracy: 95.5%"
            },
            {
                "paperId": "2",
                "title": "Paper 2",
                "year": 2021,
                "abstract": "Our accuracy: 92.3%"
            }
        ]

        result = comparator.compare_results(papers)

        assert "papers" in result
        assert "metrics" in result
        assert len(result['papers']) == 2

    def test_methodology_overlap(self):
        """Test methodology overlap analysis"""
        comparator = PaperComparator()

        papers = [
            {
                "title": "Paper 1",
                "abstract": "Using transformer and attention mechanism"
            },
            {
                "title": "Paper 2",
                "abstract": "Using transformer and BERT"
            }
        ]

        result = comparator.methodology_overlap(papers)

        assert "common_techniques" in result
        assert "unique_techniques" in result
        assert "overlap_score" in result


class TestEnhancedExportFormats:
    """Test new export formats"""

    @pytest.fixture
    def sample_paper(self):
        """Create a sample paper for testing"""
        return Paper(
            title="Test Paper on Machine Learning",
            authors=["John Doe", "Jane Smith"],
            year=2023,
            doi="10.1234/test.2023",
            abstract="This is a test abstract about machine learning research.",
            venue="Test Conference",
            citation_count=42,
            tags=["machine-learning", "test"]
        )

    def test_to_ris_format(self, sample_paper):
        """Test RIS format export"""
        ris = sample_paper.to_ris()

        assert "TY  - JOUR" in ris
        assert "TI  - Test Paper on Machine Learning" in ris
        assert "AU  - John Doe" in ris
        assert "AU  - Jane Smith" in ris
        assert "PY  - 2023" in ris
        assert "DO  - 10.1234/test.2023" in ris
        assert "ER  - " in ris

    def test_to_endnote_xml(self, sample_paper):
        """Test EndNote XML format export"""
        xml = sample_paper.to_endnote_xml()

        assert '<?xml version="1.0"' in xml
        assert "<record>" in xml
        assert "Test Paper on Machine Learning" in xml
        assert "John Doe" in xml
        assert "2023" in xml
        assert "</record>" in xml

    def test_to_zotero_json(self, sample_paper):
        """Test Zotero JSON format export"""
        zotero = sample_paper.to_zotero_json()

        assert isinstance(zotero, dict)
        assert zotero['itemType'] == "journalArticle"
        assert zotero['title'] == "Test Paper on Machine Learning"
        assert len(zotero['creators']) == 2
        assert zotero['DOI'] == "10.1234/test.2023"
        assert len(zotero['tags']) == 2

    def test_to_obsidian_md(self, sample_paper):
        """Test Obsidian markdown format export"""
        md = sample_paper.to_obsidian_md()

        assert "---" in md  # YAML frontmatter
        assert "title: Test Paper on Machine Learning" in md
        assert "[[John Doe]]" in md  # Backlinks
        assert "[[Jane Smith]]" in md
        assert "#machine-learning" in md  # Tags
        assert "## Abstract" in md
        assert "## Notes" in md

    def test_xml_escaping(self, sample_paper):
        """Test that XML characters are properly escaped"""
        paper_with_special_chars = Paper(
            title="Test & <Special> Characters",
            authors=["John \"Doe\""],
            year=2023
        )

        xml = paper_with_special_chars.to_endnote_xml()

        assert "&amp;" in xml
        assert "&lt;" in xml
        assert "&gt;" in xml
        assert "&quot;" in xml


class TestResearchTrendAnalyzer:
    """Test research trend analysis"""

    def test_trend_analyzer_initialization(self):
        """Test that trend analyzer can be initialized"""
        analyzer = get_trend_analyzer()
        assert analyzer is not None
        assert isinstance(analyzer, ResearchTrendAnalyzer)

    def test_analyze_topic_evolution_without_client(self):
        """Test topic evolution analysis with no client"""
        analyzer = ResearchTrendAnalyzer(archive_client=None)
        result = analyzer.analyze_topic_evolution("deep learning", years=5)

        assert "error" in result

    def test_emerging_topics_without_client(self):
        """Test emerging topics detection with no client"""
        analyzer = ResearchTrendAnalyzer(archive_client=None)
        result = analyzer.emerging_topics("AI")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_predict_next_papers_without_client(self):
        """Test paper prediction with no client"""
        analyzer = ResearchTrendAnalyzer(archive_client=None)
        result = analyzer.predict_next_papers("machine learning")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_trend_classification(self):
        """Test trend classification logic"""
        analyzer = ResearchTrendAnalyzer()

        assert analyzer._classify_trend(1.5) == "exponential_growth"
        assert analyzer._classify_trend(0.7) == "strong_growth"
        assert analyzer._classify_trend(0.3) == "moderate_growth"
        assert analyzer._classify_trend(0.0) == "stable"
        assert analyzer._classify_trend(-0.3) == "declining"

    def test_calculate_growth_rate(self):
        """Test growth rate calculation"""
        analyzer = ResearchTrendAnalyzer()

        yearly_data = {
            2020: {'paper_count': 10},
            2021: {'paper_count': 15},
            2022: {'paper_count': 25}
        }

        growth = analyzer._calculate_growth_rate(yearly_data)
        assert growth == 1.5  # 150% growth from 10 to 25


class TestSimilarityFinder:
    """Test similarity finding functionality"""

    def test_similarity_finder_initialization(self):
        """Test that similarity finder can be initialized"""
        finder = get_similarity_finder()
        assert finder is not None
        assert isinstance(finder, SimilarityFinder)

    def test_find_similar_papers_without_client(self):
        """Test similar paper finding with no client"""
        finder = SimilarityFinder(archive_client=None)
        result = finder.find_similar_papers("paper_id")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_find_similar_researchers_without_client(self):
        """Test researcher finding with no client"""
        finder = SimilarityFinder(archive_client=None)
        result = finder.find_similar_researchers("deep learning")

        assert isinstance(result, list)
        assert len(result) == 0

    def test_h_index_calculation(self):
        """Test h-index calculation"""
        finder = SimilarityFinder()

        # h-index = 3 (3 papers with ≥3 citations)
        citations = [10, 8, 5, 4, 3]
        h_index = finder._calculate_h_index(citations)
        assert h_index == 4

        # h-index = 5
        citations = [100, 50, 20, 10, 5, 3, 1]
        h_index = finder._calculate_h_index(citations)
        assert h_index == 5

    def test_calculate_similarity_score(self):
        """Test similarity score calculation"""
        finder = SimilarityFinder()

        base_paper = {
            "year": 2020,
            "citationCount": 100,
            "authors": [{"name": "John Doe"}, {"name": "Jane Smith"}]
        }

        candidate = {
            "year": 2021,  # Close year
            "citationCount": 90,  # Similar citations
            "authors": [{"name": "John Doe"}]  # One shared author
        }

        score = finder._calculate_similarity_score(base_paper, candidate, "citations")

        assert score > 0
        assert isinstance(score, float)

    def test_explain_similarity(self):
        """Test similarity explanation generation"""
        finder = SimilarityFinder()

        base_paper = {
            "year": 2020,
            "citationCount": 100,
            "authors": [{"name": "John Doe"}]
        }

        candidate = {
            "year": 2021,
            "citationCount": 95,
            "authors": [{"name": "John Doe"}]
        }

        reasons = finder._explain_similarity(base_paper, candidate)

        assert isinstance(reasons, list)
        assert len(reasons) > 0
        assert any("author" in r.lower() for r in reasons)


class TestIntegration:
    """Integration tests for new features"""

    def test_all_modules_importable(self):
        """Test that all new modules can be imported"""
        from cite_agent import citation_network
        from cite_agent import paper_comparator
        from cite_agent import trend_analyzer
        from cite_agent import similarity_finder

        assert citation_network is not None
        assert paper_comparator is not None
        assert trend_analyzer is not None
        assert similarity_finder is not None

    def test_export_formats_compatibility(self):
        """Test that all export formats work together"""
        paper = Paper(
            title="Test Integration",
            authors=["Test Author"],
            year=2023
        )

        # All formats should work without errors
        bibtex = paper.to_bibtex()
        ris = paper.to_ris()
        xml = paper.to_endnote_xml()
        zotero = paper.to_zotero_json()
        obsidian = paper.to_obsidian_md()

        assert all([bibtex, ris, xml, zotero, obsidian])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
