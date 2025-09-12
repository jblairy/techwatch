from datetime import datetime, date
from typing import List, Optional
import logging
import re
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

from src.infrastructure.adapters.base_crawler import BaseCrawler
from src.domain.entities.post import Post
from src.domain.value_objects.date_range import DateRange

logger = logging.getLogger(__name__)

class RedditPhpRssCrawler(BaseCrawler):
    """Crawler for r/PHP via RSS feed - anti-bot-proof solution"""

    RSS_URL = "https://www.reddit.com/r/PHP/.rss"

    @property
    def source_name(self) -> str:
        return "r/PHP"

    def fetch_posts_in_range(self, date_range: DateRange) -> List[Post]:
        """Fetches r/PHP posts within a date range via RSS/Atom"""
        try:
            user_agent = 'Mozilla/5.0 (Linux; Technology Watch Tool)'
            # Instancie le client HTTP avec le User-Agent si besoin
            if not hasattr(self.http_client, 'headers') or self.http_client.headers.get('User-Agent') != user_agent:
                from src.infrastructure.adapters.technical_adapters import RequestsHttpClient
                self.http_client = RequestsHttpClient(headers={'User-Agent': user_agent})
            # Appel sans paramètre headers
            response = self.http_client.get(self.RSS_URL)

            # Parse XML RSS/Atom
            root = ET.fromstring(response.text)

            # Détection robuste du format (RSS ou Atom)
            items = root.findall(".//item")
            if not items:
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            logger.info(f"Searching in period: {date_range}")
            logger.info(f"Number of RSS/Atom articles found: {len(items)}")

            if not items:
                logger.warning("Aucun post trouvé dans le flux RSS/Atom de Reddit. Vérifiez le format ou l'accès réseau.")

            range_posts = []

            for i, item in enumerate(items):
                post = self._parse_feed_item(item)
                if not post:
                    logger.debug(f"Reddit: Article {i+1} ignoré (erreur de parsing ou date manquante)")
                    continue
                if not post.date:
                    logger.debug(f"Reddit: Article '{post.title}' ignoré (date non parsée)")
                    continue
                if not date_range.contains(post.date):
                    logger.debug(f"Reddit: Article '{post.title}' ({post.date}) ignoré (hors période)")
                    continue
                range_posts.append(post)
                logger.info(f"Article trouvé dans la période: {post.title} ({post.date})")

            return range_posts
        except Exception as e:
            logger.error(f"Erreur lors du crawling RSS Reddit: {e}")
            return []

    def fetch_recent_posts_for_fallback(self) -> List[Post]:
        """Fetches all recent r/PHP RSS/Atom posts without date filter (for fallback verification)"""
        try:
            user_agent = 'Mozilla/5.0 (Linux; Technology Watch Tool)'
            if not hasattr(self.http_client, 'headers') or self.http_client.headers.get('User-Agent') != user_agent:
                from src.infrastructure.adapters.technical_adapters import RequestsHttpClient
                self.http_client = RequestsHttpClient(headers={'User-Agent': user_agent})

            response = self.http_client.get(self.RSS_URL)
            # Parse XML RSS/Atom
            user_agent = 'Mozilla/5.0 (Linux; Technology Watch Tool)'
            if not hasattr(self.http_client, 'headers') or self.http_client.headers.get('User-Agent') != user_agent:
                from src.infrastructure.adapters.technical_adapters import RequestsHttpClient
                self.http_client = RequestsHttpClient(headers={'User-Agent': user_agent})

            response = self.http_client.get(self.RSS_URL)
            items = root.findall(".//item")
            if not items:
                items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
            logger.debug(f"r/PHP RSS/Atom fallback verification: {len(items)} articles trouvés")

            fallback_posts = []
            for item in items[:15]:  # Limite à 15 articles récents
                post = self._parse_feed_item(item)
                if post and post.date:
                    fallback_posts.append(post)

            return fallback_posts
        except Exception as e:
            logger.error(f"Erreur lors de la vérification fallback RSS/Atom Reddit: {e}")
            return []

    def _parse_feed_item(self, item) -> Optional[Post]:
        """Parse an RSS or Atom item from r/PHP"""
        try:
            # Detect format (RSS or Atom) and parse accordingly
            if item.tag.endswith('}entry'):  # Atom format
                return self._parse_atom_entry(item)
            else:  # RSS format
                return self._parse_rss_item(item)
        except Exception as e:
            logger.warning(f"Error parsing r/PHP feed item: {e}")
            return None

    def _parse_atom_entry(self, entry) -> Optional[Post]:
        """Parse an Atom entry from r/PHP"""
        try:
            # Atom namespace
            atom_ns = "{http://www.w3.org/2005/Atom}"

            # Extract title
            title_element = entry.find(f"{atom_ns}title")
            if title_element is None or not title_element.text:
                return None

            title = title_element.text.strip()

            # Extract URL (look for link with rel="alternate")
            link_element = entry.find(f"{atom_ns}link[@rel='alternate']")
            if link_element is None:
                # Fallback: first link found
                link_element = entry.find(f"{atom_ns}link")

            if link_element is None:
                return None

            url = link_element.get('href', '').strip()
            if not url:
                return None

            # Extract publication date
            updated_element = entry.find(f"{atom_ns}updated")
            if updated_element is None:
                published_element = entry.find(f"{atom_ns}published")
                if published_element is None:
                    return None
                date_text = published_element.text.strip()
            else:
                date_text = updated_element.text.strip()

            post_date = self._parse_atom_date(date_text)
            if not post_date:
                return None

            return Post(
                title=title,
                url=url,
                date=post_date,
                source=self.source_name
            )
        except Exception as e:
            logger.warning(f"Error parsing r/PHP Atom entry: {e}")
            return None

    def _parse_rss_item(self, item) -> Optional[Post]:
        """Parse an RSS item from r/PHP"""
        try:
            # Extract title
            title_element = item.find("title")
            if title_element is None or not title_element.text:
                return None

            title = title_element.text.strip()

            # Extract URL
            link_element = item.find("link")
            if link_element is None or not link_element.text:
                return None

            url = link_element.text.strip()

            # Extract publication date
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
            logger.warning(f"Error parsing r/PHP RSS item: {e}")
            return None

    def _parse_atom_date(self, date_text: str) -> Optional[date]:
        """Parse Atom date in RFC 3339 format"""
        try:
            # Standard Atom format: "2025-09-05T10:14:03Z"
            # Also support dates with timezone offset: "2025-09-05T10:14:03+02:00"
            formats = [
                "%Y-%m-%dT%H:%M:%S%z",  # "2025-09-05T10:14:03+0000" or "2025-09-05T10:14:03+02:00"
                "%Y-%m-%dT%H:%M:%SZ",   # "2025-09-05T10:14:03Z" (UTC)
                "%Y-%m-%d %H:%M:%S",    # "2025-09-05 10:14:03" (without timezone)
                "%Y-%m-%d",              # "2025-09-05" (fallback)
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_text, fmt).date()
                except ValueError:
                    continue

            logger.debug(f"Unrecognized Atom date format: {date_text}")
            return None
        except Exception as e:
            logger.debug(f"Error parsing Atom date: {e}")
            return None

    def _parse_rss_date(self, date_text: str) -> Optional[date]:
        """Parse RSS date in RFC 2822 format"""
        try:
            # Standard RSS format: "Thu, 05 Sep 2025 10:14:03 +0000"
            formats = [
                "%a, %d %b %Y %H:%M:%S %z",    # "Thu, 05 Sep 2025 10:14:03 +0000"
                "%a, %d %b %Y %H:%M:%S",       # "Thu, 05 Sep 2025 10:14:03" (without timezone)
                "%d %b %Y %H:%M:%S %z",        # "05 Sep 2025 10:14:03 +0000"
                "%d %b %Y %H:%M:%S",           # "05 Sep 2025 10:14:03"
                "%Y-%m-%d",                    # "2025-09-05" (fallback)
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_text, fmt).date()
                except ValueError:
                    continue

            logger.debug(f"Unrecognized RSS date format: {date_text}")
            return None
        except Exception as e:
            logger.debug(f"Error parsing RSS date: {e}")
            return None
