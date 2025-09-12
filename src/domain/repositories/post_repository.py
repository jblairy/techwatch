"""
Repository Interfaces - Business Domain
Hexagonal Architecture DDD
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Dict, Any
from datetime import date

from ..entities.post import Post
from ..value_objects.date_range import DateRange


class PostRepository(ABC):
    """
    Repository interface for posts.

    Defines the contract for post persistence without depending
    on concrete implementation (file, database, etc.)
    """

    @abstractmethod
    def save(self, posts: List[Post], metadata: Dict[str, Any] = None) -> bool:
        """Save a list of posts and return success status"""
        pass

    @abstractmethod
    def load_latest(self) -> Tuple[List[Post], Dict[str, Any]]:
        """Load the most recent posts with their metadata"""
        pass

    @abstractmethod
    def load_from_file(self, filename: str) -> Tuple[List[Post], Dict[str, Any]]:
        """Load posts from a specific file"""
        pass

    @abstractmethod
    def load_by_id(self, save_id: str) -> Tuple[List[Post], Dict[str, Any]]:
        """Load posts by save identifier"""
        pass

    @abstractmethod
    def delete_save(self, save_id: str) -> bool:
        """Delete a saved file by identifier"""
        pass

    @abstractmethod
    def list_available_saves(self) -> List[str]:
        """List all available save files"""
        pass


class CrawlerRepository(ABC):
    """
    Repository interface for crawler management.
    """

    @abstractmethod
    def get_all_active_crawlers(self) -> List[str]:
        """Get list of all active crawlers"""
        pass

    @abstractmethod
    def is_crawler_enabled(self, crawler_name: str) -> bool:
        """Check if a crawler is enabled"""
        pass
