"""
Use cases for the technology watch application - Hexagonal DDD Architecture
"""
from typing import List, Optional
from datetime import date, datetime
import logging

from ...domain.entities.post import Post
from ...domain.value_objects.date_range import DateRange
from ...domain.repositories.post_repository import PostRepository
from ..dto.post_dto import ResultDTO, PostDTO

logger = logging.getLogger(__name__)


class LoadDataUseCase:
    """
    Use case for loading technology watch data
    Orchestrates the loading and filtering of posts from the repository
    """

    def __init__(self, post_repository: PostRepository):
        self._post_repository = post_repository
        self.logger = logging.getLogger(__name__)

    def load_latest(self) -> ResultDTO:
        """
        Load the latest technology watch data from the unified database.

        Returns:
            ResultDTO: Data transfer object containing posts and metadata
        """
        return self.execute()

    def execute(self, file_path: Optional[str] = None) -> ResultDTO:
        """
        Execute the load use case (always loads from the unified database).

        Returns:
            ResultDTO: Data transfer object containing posts and metadata
        """
        try:
            posts, metadata = self._post_repository.load_latest()

            # Convert domain entities to DTOs
            post_dtos = [PostDTO.from_domain_entity(post) for post in posts]

            return ResultDTO(
                posts=post_dtos,
                total_count=len(post_dtos),
                metadata=metadata or {}
            )

        except Exception as e:
            self.logger.error(f"Error loading techwatch data: {e}")
            return ResultDTO(
                posts=[],
                total_count=0,
                metadata={},
            )

    def execute_with_filters(self, days_back: int = -1, source_filter: Optional[str] = None) -> ResultDTO:
        """
        Execute the load use case with filtering (on the unified database).

        Args:
            days_back: Number of days to look back (-1 for all)
            source_filter: Optional source name to filter by

        Returns:
            ResultDTO: Filtered data transfer object
        """
        try:
            # Load all data first
            result = self.execute()

            if result.error:
                return result

            posts = [PostDTO.to_domain_entity(dto) for dto in result.posts]

            # Apply date filtering if specified
            if days_back >= 0:
                date_range = DateRange.from_days_back(days_back)
                posts = [p for p in posts if p.date and date_range.contains(p.date)]

            # Apply source filtering if specified
            if source_filter:
                posts = [p for p in posts if p.source == source_filter]

            # Convert back to DTOs
            filtered_post_dtos = [PostDTO.from_domain_entity(post) for post in posts]

            return ResultDTO(
                posts=filtered_post_dtos,
                total_count=len(filtered_post_dtos),
                metadata=result.metadata
            )

        except Exception as e:
            self.logger.error(f"Error filtering techwatch data: {e}")
            return ResultDTO(
                posts=[],
                total_count=0,
                metadata={},
            )


class SaveDataUseCase:
    """
    Use case for saving technology watch data
    Orchestrates the persistence of posts to the repository
    """

    def __init__(self, post_repository: PostRepository):
        self._post_repository = post_repository
        self.logger = logging.getLogger(__name__)

    def execute(self, posts: List[Post], metadata: dict = None) -> bool:
        """
        Execute the save use case

        Args:
            posts: List of Post domain entities to save
            metadata: Optional metadata to include

        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            success = self._post_repository.save(posts, metadata or {})
            if success:
                self.logger.info(f"Successfully saved {len(posts)} posts")
            else:
                self.logger.error("Failed to save posts")
            return success

        except Exception as e:
            self.logger.error(f"Error saving techwatch data: {e}")
            return False


class AnalyzeDataUseCase:
    """
    Use case for analyzing technology watch data
    Provides statistics and insights about the collected posts
    """

    def __init__(self, post_repository: PostRepository):
        self._post_repository = post_repository
        self.logger = logging.getLogger(__name__)

    def execute(self, file_path: Optional[str] = None) -> dict:
        """
        Execute the analyze use case

        Args:
            file_path: Optional specific file path to analyze

        Returns:
            dict: Analysis results with statistics
        """
        try:
            if file_path:
                posts, metadata = self._post_repository.load_from_file(file_path)
            else:
                posts, metadata = self._post_repository.load_latest()

            if not posts:
                return {
                    'total_posts': 0,
                    'sources': {},
                    'date_range': None,
                    'error': 'No posts found'
                }

            # Analyze sources
            sources = {}
            for post in posts:
                sources[post.source] = sources.get(post.source, 0) + 1

            # Analyze date range
            dates = [post.date for post in posts if post.date]
            date_range = {
                'earliest': min(dates) if dates else None,
                'latest': max(dates) if dates else None
            }

            return {
                'total_posts': len(posts),
                'sources': sources,
                'date_range': date_range,
                'metadata': metadata
            }

        except Exception as e:
            self.logger.error(f"Error analyzing techwatch data: {e}")
            return {
                'total_posts': 0,
                'sources': {},
                'date_range': None,
                'error': str(e)
            }
