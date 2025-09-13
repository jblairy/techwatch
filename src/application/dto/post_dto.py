"""
Data Transfer Objects (DTOs) for the technology watch application - Hexagonal DDD Architecture
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from dataclasses import dataclass

from ...domain.entities.post import Post


@dataclass
class PostDTO:
    """
    Data Transfer Object for Post entity
    Used to transfer post data between layers without exposing domain entities
    """
    title: str
    url: str
    date: str  # ISO format string for serialization
    source: str
    description: Optional[str] = None

    @classmethod
    def from_domain_entity(cls, post: Post) -> 'PostDTO':
        """
        Convert a domain Post entity to a DTO

        Args:
            post: Domain Post entity

        Returns:
            PostDTO: Data transfer object
        """
        return cls(
            title=post.title,
            url=post.url,
            date=post.date.isoformat() if post.date else "",
            source=post.source,
            description=getattr(post, 'description', None)
        )

    @staticmethod
    def to_domain_entity(dto: 'PostDTO') -> Post:
        """
        Convert a DTO back to a domain Post entity

        Args:
            dto: PostDTO to convert

        Returns:
            Post: Domain entity
        """
        # Parse date from ISO string
        post_date = None
        if dto.date:
            try:
                post_date = datetime.fromisoformat(dto.date).date()
            except ValueError:
                # Fallback for other date formats
                post_date = None

        return Post(
            title=dto.title,
            url=dto.url,
            date=post_date,
            source=dto.source
        )

    def to_entity(self) -> Post:
        """
        Convert this DTO instance to a domain Post entity
        Instance method for convenience

        Returns:
            Post: Domain entity
        """
        return PostDTO.to_domain_entity(self)


@dataclass
class WatchResultDTO:
    """
    Data Transfer Object for technology watch results
    Contains posts, metadata, and operation status
    """
    posts: List[PostDTO]
    metadata: Dict[str, Any]
    total_count: int
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        """Check if the operation was successful"""
        return self.error is None

    @property
    def sources(self) -> List[str]:
        """Get unique sources from posts"""
        return list(set(post.source for post in self.posts))

    def get_posts_by_source(self, source: str) -> List[PostDTO]:
        """Get posts filtered by source"""
        return [post for post in self.posts if post.source == source]

    def get_posts_by_date_range(self, start_date: date, end_date: date) -> List[PostDTO]:
        """Get posts filtered by date range"""
        filtered_posts = []
        for post in self.posts:
            if post.date:
                try:
                    post_date = datetime.fromisoformat(post.date).date()
                    if start_date <= post_date <= end_date:
                        filtered_posts.append(post)
                except ValueError:
                    continue
        return filtered_posts


@dataclass
class RequestDTO:
    """
    Data Transfer Object for techwatch data requests
    Used to specify filtering and loading parameters
    """
    file_path: Optional[str] = None
    days_back: int = -1  # -1 for all days
    source_filter: Optional[str] = None
    date_filter: Optional[date] = None

    def has_filters(self) -> bool:
        """Check if any filters are applied"""
        return (
            self.days_back >= 0 or
            self.source_filter is not None or
            self.date_filter is not None
        )


@dataclass
class MetadataDTO:
    """
    Data Transfer Object for metadata
    Contains information about the data collection process
    """
    generated_at: str
    total_articles: int
    sources: List[str]
    format_version: str
    date_range: Dict[str, Any]
    generation_stats: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, metadata: Dict[str, Any]) -> 'MetadataDTO':
        """
        Create MetadataDTO from dictionary

        Args:
            metadata: Dictionary containing metadata

        Returns:
            MetadataDTO: Metadata DTO
        """
        return cls(
            generated_at=metadata.get('generated_at', ''),
            total_articles=metadata.get('total_articles', 0),
            sources=metadata.get('sources', []),
            format_version=metadata.get('format_version', '1.0'),
            date_range=metadata.get('date_range', {}),
            generation_stats=metadata.get('generation_stats')
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert DTO to dictionary

        Returns:
            Dict: Metadata as dictionary
        """
        return {
            'generated_at': self.generated_at,
            'total_articles': self.total_articles,
            'sources': self.sources,
            'format_version': self.format_version,
            'date_range': self.date_range,
            'generation_stats': self.generation_stats
        }


@dataclass
class ResultDTO:
    """
    Data Transfer Object for technology watch results.
    Encapsulates a list of PostDTOs, total count, and metadata.
    Optionally supports an error field for compatibility with legacy tests.
    """
    posts: List[PostDTO]
    total_count: int
    metadata: Dict[str, Any]
    error: Optional[str] = None

    @classmethod
    def from_posts(cls, posts: List[Post], metadata: Optional[Dict[str, Any]] = None, error: Optional[str] = None) -> 'ResultDTO':
        """
        Create a ResultDTO from a list of domain Post entities and optional metadata.
        """
        post_dtos = [PostDTO.from_domain_entity(post) for post in posts]
        return cls(
            posts=post_dtos,
            total_count=len(post_dtos),
            metadata=metadata or {},
            error=error
        )

    def to_entities(self) -> List[Post]:
        """
        Convert DTOs back to domain Post entities.
        """
        return [PostDTO.to_domain_entity(dto) for dto in self.posts]

    @property
    def is_success(self) -> bool:
        """Check if the operation was successful"""
        return self.error is None

    @property
    def sources(self) -> List[str]:
        """Get unique sources from posts"""
        return list(set(post.source for post in self.posts))

    def get_posts_by_source(self, source: str) -> List[PostDTO]:
        """Get posts filtered by source"""
        return [post for post in self.posts if post.source == source]

    def get_posts_by_date_range(self, start_date: date, end_date: date) -> List[PostDTO]:
        """Get posts filtered by date range"""
        filtered_posts = []
        for post in self.posts:
            if post.date:
                try:
                    post_date = datetime.fromisoformat(post.date).date()
                    if start_date <= post_date <= end_date:
                        filtered_posts.append(post)
                except ValueError:
                    continue
        return filtered_posts

