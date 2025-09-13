"""
Domain Services - Pure Business Logic
Hexagonal Architecture DDD
"""
from typing import List, Optional, Dict
from datetime import date
from collections import Counter

from ..entities.post import Post
from ..value_objects.date_range import DateRange


class PostFilteringService:
    """
    Domain service for post filtering.

    Contains pure business logic for filtering without external dependencies.
    """

    @staticmethod
    def filter_by_date_range(posts: List[Post], date_range: DateRange) -> List[Post]:
        """Filter posts by date range"""
        return [
            post for post in posts
            if post.date and date_range.contains(post.date)
        ]

    @staticmethod
    def filter_by_source(posts: List[Post], source_filter: str) -> List[Post]:
        """Filter posts by source"""
        # Special handling for "All sources"
        if not source_filter or source_filter.lower() == "all sources":
            return posts

        return [
            post for post in posts
            if post.source and post.source.lower() == source_filter.lower()
        ]

    @staticmethod
    def remove_duplicates(posts: List[Post]) -> List[Post]:
        """Remove duplicate posts based on title and URL"""
        seen = set()
        unique_posts = []

        for post in posts:
            post_key = (post.title, post.url)
            if post_key not in seen:
                seen.add(post_key)
                unique_posts.append(post)

        return unique_posts

    @staticmethod
    def sort_by_date(posts: List[Post], ascending: bool = False) -> List[Post]:
        """Sort posts by date"""
        return sorted(
            posts,
            key=lambda post: post.date or date.min,
            reverse=not ascending
        )

    @staticmethod
    def group_by_source(posts: List[Post]) -> Dict[str, List[Post]]:
        """Group posts by source"""
        groups = {}
        for post in posts:
            source = post.source or "Unknown source"
            if source not in groups:
                groups[source] = []
            groups[source].append(post)
        return groups


class PostAnalysisService:
    """
    Domain service for post analysis.

    Contains business logic for analyzing and summarizing posts.
    """

    @staticmethod
    def get_sources_summary(posts: List[Post]) -> Dict[str, int]:
        """Get summary of posts by source"""
        sources = [post.source or "Unknown source" for post in posts]
        return dict(Counter(sources))

    @staticmethod
    def get_date_range_from_posts(posts: List[Post]) -> Optional[DateRange]:
        """Extract date range from a list of posts"""
        dates = [post.date for post in posts if post.date]

        if not dates:
            return None

        min_date = min(dates)
        max_date = max(dates)

        return DateRange(start_date=min_date, end_date=max_date)

    @staticmethod
    def count_new_posts(current_posts: List[Post], previous_posts: List[Post]) -> int:
        """Count new posts compared to a previous list"""
        previous_keys = {(post.title, post.url) for post in previous_posts}

        new_count = 0
        for post in current_posts:
            post_key = (post.title, post.url)
            if post_key not in previous_keys:
                new_count += 1

        return new_count

    @staticmethod
    def get_most_active_sources(posts: List[Post], limit: int = 5) -> List[tuple]:
        """Get the most active sources with their post count"""
        sources_summary = PostAnalysisService.get_sources_summary(posts)
        return sorted(
            sources_summary.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

    @staticmethod
    def count_by_source(posts: List[Post]) -> Dict[str, int]:
        """Count posts by source"""
        counter = Counter(post.source for post in posts if post.source)
        return dict(counter)

    @staticmethod
    def count_by_date(posts: List[Post]) -> Dict[date, int]:
        """Count posts by date (datetime.date keys)"""
        counter = Counter(post.date for post in posts if post.date)
        return dict(counter)

    @staticmethod
    def get_latest_posts(posts: List[Post], limit: int = 5) -> List[Post]:
        """Get the most recent posts (by date, descending)"""
        sorted_posts = sorted(
            [p for p in posts if p.date],
            key=lambda post: post.date,
            reverse=True
        )
        return sorted_posts[:limit]
