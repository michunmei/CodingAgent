import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Paper:
    id: str
    title: str
    summary: str
    authors: List[str]
    published: datetime
    updated: datetime
    categories: List[str]
    pdf_url: Optional[str] = None
    doi: Optional[str] = None
