import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from models import Paper

ARXIV_API_URL = "http://export.arxiv.org/api/query"

SUBJECT_CATEGORIES = {
    "cs.AI": "Artificial Intelligence",
    "cs.CV": "Computer Vision and Pattern Recognition",
    "cs.CL": "Computation and Language",
    "cs.LG": "Machine Learning"
}

def fetch_papers(category: str, days_back: int = 1) -> List[Paper]:
    """Fetch papers from arXiv API for given category within specified time range."""
    try:
        # Calculate date threshold
        start_date = datetime.utcnow() - timedelta(days=days_back)
        search_query = f"cat:{category} AND submittedDate:[{start_date.strftime('%Y%m%d')}000000 TO {datetime.utcnow().strftime('%Y%m%d%H%M%S')}]]"
        
        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": 100,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }
        
        response = requests.get(ARXIV_API_URL, params=params)
        response.raise_for_status()
        
        feed = feedparser.parse(response.content)
        papers = []
        
        for entry in feed.entries:
            # Extract authors
            authors = [author.name for author in entry.authors]
            
            # Extract categories
            categories = [tag.term for tag in entry.tags]
            
            # Create Paper object
            paper = Paper(
                id=entry.id.split('/abs/')[-1],
                title=entry.title,
                summary=entry.summary,
                authors=authors,
                published=datetime(*entry.published_parsed[:6]),
                updated=datetime(*entry.updated_parsed[:6]),
                categories=categories,
                pdf_url=entry.links[1].href if len(entry.links) > 1 else None,
                doi=getattr(entry, 'arxiv_doi', None)
            )
            papers.append(paper)
        
        return papers
    except Exception as e:
        print(f"Error fetching papers: {str(e)}")
        return []

def get_all_categories() -> Dict[str, str]:
    """Return all supported subject categories."""
    return SUBJECT_CATEGORIES

def filter_papers_by_category(papers: List[Paper], category: str) -> List[Paper]:
    """Filter papers by specific category."""
    return [paper for paper in papers if category in paper.categories]

def format_paper_for_template(paper: Paper) -> Dict[str, Any]:
    """Convert Paper object to dictionary for template rendering."""
    return {
        'id': paper.id,
        'title': paper.title,
        'summary': paper.summary,
        'authors': paper.authors,
        'published': paper.published.strftime('%Y-%m-%d'),
        'updated': paper.updated.strftime('%Y-%m-%d'),
        'categories': paper.categories,
        'pdf_url': paper.pdf_url,
        'doi': paper.doi
    }

def generate_bibtex(paper: Paper) -> str:
    """Generate BibTeX citation for a paper."""
    authors = ' and '.join(paper.authors)
    year = paper.published.year
    
    return f"""@article{{{paper.id.replace('/', '_')},
  title={{{paper.title}}},
  author={{{authors}}},
  journal={{arXiv preprint}},
  year={{{year}}},
  url={{https://arxiv.org/abs/{paper.id}}}
}}"""

def generate_apa(paper: Paper) -> str:
    """Generate APA citation for a paper."""
    authors = ', '.join([f'{a.split()[-1]}, {" ".join(a.split()[:-1])}' for a in paper.authors])
    year = paper.published.year
    
    return f"{authors} ({year}). {paper.title}. arXiv preprint. https://arxiv.org/abs/{paper.id}"

def generate_mla(paper: Paper) -> str:
    """Generate MLA citation for a paper."""
    authors = ', '.join(paper.authors)
    
    return f"{authors}. \"{paper.title}.\" arXiv preprint, {paper.published.year}, https://arxiv.org/abs/{paper.id}."
