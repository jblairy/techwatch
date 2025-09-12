"""
Post Entity - Business Domain
Hexagonal Architecture DDD
"""
from datetime import date
from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class Post:
    """
    Post entity representing a technology watch article.

    This entity is part of the business domain and contains the
    fundamental business logic related to watch articles.
    """
    title: str
    url: str
    date: Optional[date] = None
    source: Optional[str] = None
    description: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert the post to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert date to string for JSON serialization
        if data['date']:
            data['date'] = data['date'].isoformat()
        return data

    def is_recent(self, reference_date: date, days_threshold: int = 7) -> bool:
        """Check if the article is recent compared to a reference date"""
        if not self.date:
            return False
        return (reference_date - self.date).days <= days_threshold

    def matches_source(self, source_filter: str) -> bool:
        """Check if the article matches the source filter"""
        if not source_filter or source_filter.lower() == "all sources":
            return True
        return self.source and self.source.lower() == source_filter.lower()

    def __hash__(self) -> int:
        """Hash based on title and URL to avoid duplicates"""
        return hash((self.title, self.url))

    def __eq__(self, other) -> bool:
        """Equality based on title and URL"""
        if not isinstance(other, Post):
            return False
        return self.title == other.title and self.url == other.url
