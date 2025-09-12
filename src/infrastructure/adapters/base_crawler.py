"""
Base class for crawlers - Infrastructure
Hexagonal Architecture DDD
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import logging
import requests
from bs4 import BeautifulSoup

from ...domain.entities.post import Post
from ...domain.value_objects.date_range import DateRange
from .technical_adapters import RequestsHttpClient, BeautifulSoupParser, SystemDateProvider


class BaseCrawler(ABC):
    """
    Abstract base class for all crawlers.

    To add a new crawler:
    - Inherit from BaseCrawler
    - Implement the `source_name` property (return the source name as a string)
    - Implement the `fetch_posts_in_range(date_range: DateRange) -> List[Post]` method
    - Use injected dependencies (http_client, html_parser, date_provider) for HTTP and parsing
    - Return a list of Post entities

    Example:
        class MySourceCrawler(BaseCrawler):
            @property
            def source_name(self) -> str:
                return "My Source"

            def fetch_posts_in_range(self, date_range: DateRange) -> List[Post]:
                # Your crawling logic here
                return []
    """

    def __init__(self, http_client=None, html_parser=None, date_provider=None, timeout: int = 10):
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

        # Injected technical services or created by default
        self.http_client = http_client or RequestsHttpClient(timeout)
        self.html_parser = html_parser or BeautifulSoupParser()
        self.date_provider = date_provider or SystemDateProvider()

    @property
    @abstractmethod
    def source_name(self) -> str:
        """Source name for identification"""
        pass

    @abstractmethod
    def fetch_posts_in_range(self, date_range: DateRange) -> List[Post]:
        """
        Fetch posts within a given date range.

        Args:
            date_range: Date range to crawl

        Returns:
            List of posts found in the range
        """
        pass

    def fetch_recent_posts_for_fallback(self) -> List[Post]:
        """
        Fetch recent posts without date filter for fallback verification.
        Default implementation returns empty list.

        Returns:
            List of recent posts
        """
        return []

    def log_crawling_start(self, date_range: DateRange):
        """Log the start of crawling process"""
        self.logger.info(f"Starting crawling for {self.source_name} - Period: {date_range}")

    def log_posts_found(self, count: int):
        """Log the number of posts found"""
        self.logger.info(f"{self.source_name}: {count} posts found")

    def log_crawling_error(self, error: Exception):
        """Log crawling errors"""
        self.logger.error(f"Error crawling {self.source_name}: {error}")

    def safe_extract_text(self, element, default: str = "") -> str:
        """Safely extract text from an HTML element"""
        if element is None:
            return default
        return element.get_text(strip=True) if hasattr(element, 'get_text') else str(element).strip()

    def build_absolute_url(self, base_url: str, relative_url: str) -> str:
        """Build an absolute URL from base and relative URLs"""
        if relative_url.startswith('http'):
            return relative_url
        from urllib.parse import urljoin
        return urljoin(base_url, relative_url)

    def parse_rss_items(self, response_text: str) -> list:
        """Parse RSS feed and return list of <item> elements."""
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response_text)
        return root.findall('.//item')

    def parse_html_articles(self, response_text: str, tag: str, class_name: str) -> list:
        """Parse HTML and return list of elements matching tag and class."""
        soup = self.html_parser.parse(response_text)
        return soup.find_all(tag, class_=class_name)

    def filter_posts_by_date(self, posts: list, date_range: 'DateRange') -> list:
        """Filter a list of Post objects by date range."""
        return [post for post in posts if post and post.date and date_range.contains(post.date)]
