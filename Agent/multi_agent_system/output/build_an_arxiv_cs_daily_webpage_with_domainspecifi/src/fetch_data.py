import feedparser
import requests
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

ARXIV_API_URL = 'http://export.arxiv.org/api/query?search_query=cat:{}&sortBy=submittedDate&sortOrder=descending&max_results=20'

CATEGORY_MAP = {
    'cs.AI': 'Artificial Intelligence',
    'cs.CV': 'Computer Vision',
    'cs.CL': 'Computation and Language',
    'cs.LG': 'Machine Learning'
}

def fetch_papers(category='cs.AI'):
    url = ARXIV_API_URL.format(category)
    response = requests.get(url)
    feed = feedparser.parse(response.content)
    papers = []
    for entry in feed.entries:
        # Extract arXiv ID from the link
        arxiv_id = entry.id.split('/abs/')[-1]
        
        # Extract categories
        categories = [tag.term for tag in entry.tags if tag.scheme == 'http://arxiv.org/schemas/atom']
        
        # Format authors
        authors = [author.name for author in entry.authors]
        
        papers.append({
            'id': arxiv_id,
            'title': entry.title,
            'summary': entry.summary,
            'published': entry.published,
            'authors': authors,
            'categories': categories,
            'link': entry.link,
            'pdf_link': entry.links[1].href if len(entry.links) > 1 else entry.link.replace('/abs/', '/pdf/') + '.pdf'
        })
    return papers

def get_paper_details(paper_id):
    # For simplicity, we'll fetch again. In production, you might want to cache this.
    # Construct search query for specific ID
    url = f'http://export.arxiv.org/api/query?id_list={paper_id}'
    response = requests.get(url)
    feed = feedparser.parse(response.content)
    
    if not feed.entries:
        return None
        
    entry = feed.entries[0]
    
    # Extract categories
    categories = [tag.term for tag in entry.tags if tag.scheme == 'http://arxiv.org/schemas/atom']
    
    # Format authors
    authors = [author.name for author in entry.authors]
    
    return {
        'id': paper_id,
        'title': entry.title,
        'summary': entry.summary,
        'published': entry.published,
        'authors': authors,
        'categories': categories,
        'link': entry.link,
        'pdf_link': entry.links[1].href if len(entry.links) > 1 else entry.link.replace('/abs/', '/pdf/') + '.pdf',
        'bibtex': f"""@article{{{paper_id.replace('/', '_')},
  title={{{entry.title}}},
  author={{{' and '.join(authors)}}},
  journal={{arXiv preprint arXiv:{paper_id}}},
  year={{{entry.published[:4]}}}
}}""",
        'apa': f"{', '.join(authors)} ({entry.published[:4]}). {entry.title}. arXiv preprint arXiv:{paper_id}.",
        'mla': f"{', '.join(authors)}. \"{entry.title}.\" arXiv preprint arXiv:{paper_id} ({entry.published[:4]})."
    }
