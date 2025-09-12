from datetime import datetime, date
from typing import List, Optional
import logging
import xml.etree.ElementTree as ET

from src.infrastructure.adapters.base_crawler import BaseCrawler
from src.domain.entities.post import Post
from src.domain.value_objects.date_range import DateRange

logger = logging.getLogger(__name__)

class KorbenCrawler(BaseCrawler):
    """Crawler for Korben Blog via RSS feed (no external library)"""

    RSS_URL = "https://korben.info/feed"

    @property
    def source_name(self) -> str:
        return "Korben Blog"

    def fetch_posts_in_range(self, date_range: DateRange) -> List[Post]:
        """Fetches Korben posts within a date range via RSS"""
        try:
            response = self.http_client.get(self.RSS_URL)
            root = ET.fromstring(response.text)
            items = root.findall(".//item")
            logger.info(f"Searching in period: {date_range}")
            logger.info(f"Number of RSS articles found: {len(items)}")
            range_posts = []
            for i, item in enumerate(items):
                post = self._parse_rss_item(item)
                if not post:
                    logger.debug(f"Korben: Article {i+1} ignored (parsing error or missing date)")
                    continue
                if not post.date:
                    logger.debug(f"Korben: Article '{post.title}' ignored (date not parsed)")
                    continue
                if not date_range.contains(post.date):
                    logger.debug(f"Korben: Article '{post.title}' ({post.date}) ignored (out of range)")
                    continue
                range_posts.append(post)
                logger.info(f"Article found in range: {post.title} ({post.date})")
            return range_posts
        except Exception as e:
            logger.error(f"Error during Korben RSS crawling: {e}")
            return []

    def _parse_rss_item(self, item) -> Optional[Post]:
        """Parse an RSS item from Korben"""
        try:
            title_element = item.find("title")
            if title_element is None or not title_element.text:
                return None
            title = title_element.text.strip()
            link_element = item.find("link")
            if link_element is None or not link_element.text:
                return None
            url = link_element.text.strip()
            pub_date_element = item.find("pubDate")
            if pub_date_element is None or not pub_date_element.text:
                return None
            post_date = self._parse_rss_date(pub_date_element.text.strip())
            if not post_date:
                return None
            return Post(
                title=title,
                url=url,
                date=post_date,
                source=self.source_name
            )
        except Exception as e:
            logger.warning(f"Error parsing Korben RSS item: {e}")
            return None

    def _parse_rss_date(self, date_text: str) -> Optional[date]:
        """Parse RSS date in RFC 2822 format"""
        try:
            formats = [
                "%a, %d %b %Y %H:%M:%S %z",    # "Thu, 05 Sep 2025 10:14:03 +0000"
                "%a, %d %b %Y %H:%M:%S",       # "Thu, 05 Sep 2025 10:14:03"
                "%d %b %Y %H:%M:%S %z",        # "05 Sep 2025 10:14:03 +0000"
                "%d %b %Y %H:%M:%S",           # "05 Sep 2025 10:14:03"
                "%Y-%m-%d",                    # "2025-09-05" (fallback)
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_text, fmt).date()
                except ValueError:
                    continue
            logger.debug(f"Unrecognized Korben RSS date format: {date_text}")
            return None
        except Exception as e:
            logger.debug(f"Error parsing Korben RSS date: {e}")
            return None
