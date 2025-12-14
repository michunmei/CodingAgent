"""
Advanced arXiv API Client for comprehensive paper data retrieval
Implements efficient caching, batch processing, and category management
"""
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, asdict
import requests
import feedparser
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ArxivPaper:
    """Structure for arXiv paper data"""
    id: str
    title: str
    authors: List[str]
    abstract: str
    published: str
    updated: str
    categories: List[str]
    primary_category: str
    url: str
    pdf_url: str
    doi: Optional[str] = None
    journal_ref: Optional[str] = None
    comment: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

class ArxivCategoryManager:
    """Manages arXiv computer science categories"""
    
    # Complete list of CS categories from arXiv
    CS_CATEGORIES = {
        'cs.AI': 'Artificial Intelligence',
        'cs.AR': 'Hardware Architecture', 
        'cs.CC': 'Computational Complexity',
        'cs.CE': 'Computational Engineering, Finance, and Science',
        'cs.CG': 'Computational Geometry',
        'cs.CL': 'Computation and Language',
        'cs.CR': 'Cryptography and Security',
        'cs.CV': 'Computer Vision and Pattern Recognition',
        'cs.CY': 'Computers and Society',
        'cs.DB': 'Databases',
        'cs.DC': 'Distributed, Parallel, and Cluster Computing',
        'cs.DL': 'Digital Libraries',
        'cs.DM': 'Discrete Mathematics',
        'cs.DS': 'Data Structures and Algorithms',
        'cs.ET': 'Emerging Technologies',
        'cs.FL': 'Formal Languages and Automata Theory',
        'cs.GL': 'General Literature',
        'cs.GR': 'Graphics',
        'cs.GT': 'Computer Science and Game Theory',
        'cs.HC': 'Human-Computer Interaction',
        'cs.IR': 'Information Retrieval',
        'cs.IT': 'Information Theory',
        'cs.LG': 'Machine Learning',
        'cs.LO': 'Logic in Computer Science',
        'cs.MA': 'Multiagent Systems',
        'cs.MM': 'Multimedia',
        'cs.MS': 'Mathematical Software',
        'cs.NA': 'Numerical Analysis',
        'cs.NE': 'Neural and Evolutionary Computing',
        'cs.NI': 'Networking and Internet Architecture',
        'cs.OH': 'Other Computer Science',
        'cs.OS': 'Operating Systems',
        'cs.PF': 'Performance',
        'cs.PL': 'Programming Languages',
        'cs.RO': 'Robotics',
        'cs.SC': 'Symbolic Computation',
        'cs.SD': 'Sound',
        'cs.SE': 'Software Engineering',
        'cs.SI': 'Social and Information Networks',
        'cs.SY': 'Systems and Control'
    }
    
    @classmethod
    def get_all_categories(cls) -> Dict[str, str]:
        """Get all CS categories"""
        return cls.CS_CATEGORIES.copy()
    
    @classmethod
    def get_category_name(cls, category: str) -> str:
        """Get human-readable category name"""
        return cls.CS_CATEGORIES.get(category, category)
    
    @classmethod
    def is_valid_category(cls, category: str) -> bool:
        """Check if category is valid"""
        return category in cls.CS_CATEGORIES

class AdvancedArxivClient:
    """Advanced arXiv API client with caching and batch processing"""
    
    def __init__(self, cache_dir: str = "./cache"):
        """
        Initialize the arXiv client
        
        Args:
            cache_dir: Directory for caching API responses
        """
        self.base_url = "http://export.arxiv.org/api/query"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ArxivClient/1.0 (Multi-Agent System)'
        })
        
        # Setup caching
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 3.0  # 3 seconds between requests
        
        # Categories manager
        self.categories = ArxivCategoryManager()
        
        logger.info(f"AdvancedArxivClient initialized with cache: {self.cache_dir}")
    
    def _rate_limit(self):
        """Implement rate limiting to be respectful to arXiv API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _get_cache_file(self, query_hash: str) -> Path:
        """Get cache file path for a query"""
        return self.cache_dir / f"arxiv_{query_hash}.json"
    
    def _load_from_cache(self, cache_file: Path, max_age_hours: int = 6) -> Optional[List[ArxivPaper]]:
        """Load results from cache if still fresh"""
        try:
            if not cache_file.exists():
                return None
            
            # Check cache age
            cache_age = time.time() - cache_file.stat().st_mtime
            if cache_age > max_age_hours * 3600:
                logger.debug(f"Cache expired: {cache_file}")
                return None
            
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            papers = [ArxivPaper(**paper_data) for paper_data in data]
            logger.info(f"Loaded {len(papers)} papers from cache: {cache_file}")
            return papers
            
        except Exception as e:
            logger.warning(f"Failed to load cache {cache_file}: {str(e)}")
            return None
    
    def _save_to_cache(self, cache_file: Path, papers: List[ArxivPaper]):
        """Save results to cache"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump([paper.to_dict() for paper in papers], f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {len(papers)} papers to cache: {cache_file}")
        except Exception as e:
            logger.warning(f"Failed to save cache {cache_file}: {str(e)}")
    
    def _parse_arxiv_response(self, response_content: str) -> List[ArxivPaper]:
        """Parse arXiv API response and convert to ArxivPaper objects"""
        try:
            feed = feedparser.parse(response_content)
            papers = []
            
            # Check for API errors in the response
            if len(feed.entries) == 1 and hasattr(feed.entries[0], 'id'):
                entry = feed.entries[0]
                if 'api/errors' in entry.id or entry.title == 'Error':
                    error_msg = getattr(entry, 'summary', 'Unknown API error')
                    logger.error(f"arXiv API returned error: {error_msg}")
                    return []
            
            for entry in feed.entries:
                # Skip error entries
                if 'api/errors' in entry.id or entry.title == 'Error':
                    continue
                    
                # Parse authors
                authors = []
                if hasattr(entry, 'authors'):
                    authors = [author.name for author in entry.authors]
                elif hasattr(entry, 'author'):
                    authors = [entry.author]
                
                # Parse categories
                categories = []
                primary_category = ""
                if hasattr(entry, 'tags'):
                    categories = [tag.term for tag in entry.tags]
                    if categories:
                        primary_category = categories[0]
                
                # Extract arXiv ID - validate format
                try:
                    arxiv_id = entry.id.split('/')[-1].split('v')[0]  # Remove version number
                    if not arxiv_id or len(arxiv_id) < 5:  # Basic validation
                        logger.warning(f"Invalid arXiv ID format: {arxiv_id}")
                        continue
                except Exception as e:
                    logger.warning(f"Failed to parse arXiv ID from {entry.id}: {str(e)}")
                    continue
                
                # Build URLs
                abs_url = f"https://arxiv.org/abs/{arxiv_id}"
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                
                paper = ArxivPaper(
                    id=arxiv_id,
                    title=entry.title.strip(),
                    authors=authors,
                    abstract=getattr(entry, 'summary', '').strip(),
                    published=getattr(entry, 'published', ''),
                    updated=getattr(entry, 'updated', ''),
                    categories=categories,
                    primary_category=primary_category,
                    url=abs_url,
                    pdf_url=pdf_url,
                    doi=getattr(entry, 'arxiv_doi', None),
                    journal_ref=getattr(entry, 'arxiv_journal_ref', None),
                    comment=getattr(entry, 'arxiv_comment', None)
                )
                papers.append(paper)
            
            logger.info(f"Parsed {len(papers)} papers from arXiv response")
            return papers
            
        except Exception as e:
            logger.error(f"Failed to parse arXiv response: {str(e)}")
            return []
    
    def search_papers(self, query: str, category: str = None, max_results: int = 100, 
                     sort_by: str = "submittedDate", sort_order: str = "descending") -> List[ArxivPaper]:
        """
        Search for papers on arXiv
        
        Args:
            query: Search query
            category: arXiv category filter (e.g., 'cs.AI')
            max_results: Maximum number of papers to return
            sort_by: Sort criteria ('submittedDate', 'lastUpdatedDate', 'relevance')
            sort_order: Sort order ('ascending', 'descending')
            
        Returns:
            List of ArxivPaper objects
        """
        try:
            # Build search query
            search_query = query
            if category and self.categories.is_valid_category(category):
                # Use simpler query format to avoid server issues
                if query == "*":
                    search_query = f"cat:{category}"
                else:
                    search_query = f"cat:{category} AND ({query})"
            
            # Generate cache key
            cache_key = f"{search_query}_{max_results}_{sort_by}_{sort_order}"
            query_hash = str(hash(cache_key))
            cache_file = self._get_cache_file(query_hash)
            
            # Try loading from cache first
            cached_papers = self._load_from_cache(cache_file)
            if cached_papers is not None:
                return cached_papers
            
            # Rate limiting
            self._rate_limit()
            
            # Build request parameters
            params = {
                'search_query': search_query,
                'start': 0,
                'max_results': min(max_results, 2000),  # arXiv API limit
                'sortBy': sort_by,
                'sortOrder': sort_order
            }
            
            # Make API request with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = self.session.get(self.base_url, params=params, timeout=30)
                    response.raise_for_status()
                    break
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 500 and attempt < max_retries - 1:
                        logger.warning(f"arXiv API 500 error, retry {attempt + 1}/{max_retries}")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise
            
            # Parse response
            papers = self._parse_arxiv_response(response.content)
            
            # Save to cache
            self._save_to_cache(cache_file, papers)
            
            logger.info(f"Found {len(papers)} papers for query: {search_query}")
            return papers
            
        except requests.RequestException as e:
            logger.error(f"arXiv API request failed: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in arXiv search: {str(e)}")
            return []
    
    def get_recent_papers_by_category(self, category: str, days: int = 7, max_results: int = 50) -> List[ArxivPaper]:
        """
        Get recent papers from a specific category
        
        Args:
            category: arXiv category (e.g., 'cs.AI')
            days: Number of recent days to search
            max_results: Maximum number of papers
            
        Returns:
            List of ArxivPaper objects
        """
        try:
            if not self.categories.is_valid_category(category):
                logger.warning(f"Invalid category: {category}")
                return []
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Search recent papers in category
            papers = self.search_papers(
                query="*",  # All papers
                category=category,
                max_results=max_results,
                sort_by="submittedDate",
                sort_order="descending"
            )
            
            # Filter by date (additional filtering since arXiv API doesn't support date ranges)
            recent_papers = []
            for paper in papers:
                try:
                    # Parse submission date
                    pub_date = datetime.fromisoformat(paper.published.replace('Z', '+00:00'))
                    if pub_date.replace(tzinfo=None) >= start_date:
                        recent_papers.append(paper)
                except:
                    # If date parsing fails, include the paper anyway
                    recent_papers.append(paper)
            
            logger.info(f"Found {len(recent_papers)} recent papers in {category} (last {days} days)")
            return recent_papers[:max_results]
            
        except Exception as e:
            logger.error(f"Failed to get recent papers for {category}: {str(e)}")
            return []
    
    def get_daily_papers_all_categories(self, max_per_category: int = 5) -> Dict[str, List[ArxivPaper]]:
        """
        Get recent papers from all CS categories
        
        Args:
            max_per_category: Maximum papers per category
            
        Returns:
            Dictionary mapping category -> list of papers
        """
        all_papers = {}
        categories = self.categories.get_all_categories()
        
        logger.info(f"Fetching recent papers from {len(categories)} CS categories")
        
        for category_code, category_name in categories.items():
            try:
                logger.info(f"Fetching papers for {category_code} ({category_name})")
                papers = self.get_recent_papers_by_category(category_code, days=7, max_results=max_per_category)
                
                if papers:
                    all_papers[category_code] = papers
                    logger.info(f"Added {len(papers)} papers for {category_code}")
                else:
                    logger.info(f"No recent papers found for {category_code}")
                
                # Small delay between category requests
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Failed to fetch papers for {category_code}: {str(e)}")
                continue
        
        total_papers = sum(len(papers) for papers in all_papers.values())
        logger.info(f"Total papers collected: {total_papers} across {len(all_papers)} categories")
        
        return all_papers
    
    def get_paper_by_id(self, arxiv_id: str) -> Optional[ArxivPaper]:
        """
        Get a specific paper by arXiv ID
        
        Args:
            arxiv_id: arXiv paper ID (e.g., '2301.12345')
            
        Returns:
            ArxivPaper object or None if not found
        """
        try:
            papers = self.search_papers(f"id:{arxiv_id}", max_results=1)
            return papers[0] if papers else None
        except Exception as e:
            logger.error(f"Failed to get paper {arxiv_id}: {str(e)}")
            return None
    
    def clear_cache(self, older_than_hours: int = 24):
        """
        Clear old cache files
        
        Args:
            older_than_hours: Remove cache files older than this many hours
        """
        try:
            current_time = time.time()
            cutoff_time = current_time - (older_than_hours * 3600)
            
            removed_count = 0
            for cache_file in self.cache_dir.glob("arxiv_*.json"):
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
                    removed_count += 1
            
            logger.info(f"Cleared {removed_count} old cache files")
            
        except Exception as e:
            logger.warning(f"Failed to clear cache: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get client statistics
        
        Returns:
            Dictionary with usage statistics
        """
        cache_files = list(self.cache_dir.glob("arxiv_*.json"))
        cache_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'cache_files': len(cache_files),
            'cache_size_mb': cache_size / (1024 * 1024),
            'supported_categories': len(self.categories.get_all_categories()),
            'cache_dir': str(self.cache_dir)
        }