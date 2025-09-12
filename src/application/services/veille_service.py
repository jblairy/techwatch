"""
Technology Watch Service - Application Layer
Hexagonal Architecture DDD
"""
import logging
from typing import List, Optional

from ...domain.entities.post import Post
from ...domain.value_objects.date_range import DateRange

logger = logging.getLogger(__name__)


class TechWatchService:
    """Main service orchestrating technology watch - Application Layer"""

    def __init__(self, crawlers: List, renderer):
        self.crawlers = crawlers
        self.renderer = renderer
        # Delayed import to avoid circular imports
        from ...infrastructure.services.fallback_service import FallbackVerificationService
        self.fallback_service = FallbackVerificationService()

    def run(self, days_back: int = 0) -> None:
        """Execute technology watch on all crawlers with a date range

        Args:
            days_back: Number of days to go back (0 = only today)
        """
        date_range = DateRange.from_days_back(days_back)
        logger.info(f"Starting technology watch for period: {date_range}")

        for crawler in self.crawlers:
            try:
                posts = crawler.fetch_posts_in_range(date_range)
                self.renderer.render_posts(crawler.source_name, posts, date_range)
                # Affichage d'une alerte visuelle si aucun post n'est trouvé
                if hasattr(self.renderer, 'render_alert') and len(posts) == 0:
                    self.renderer.render_alert(crawler.source_name)
                # Fallback verification if no posts found
                fallback_result = self.fallback_service.check_for_missed_posts(crawler, date_range, posts)
                if fallback_result.get('has_alert', False):
                    self.renderer.render_fallback_alert(fallback_result['message'])
            except Exception as e:
                logger.error(f"Error crawling {crawler.source_name}: {e}")
                print(f"❌ Error crawling {crawler.source_name}: {e}")

    def fetch_posts_in_range(self, date_range: DateRange, sources: Optional[List[str]] = None) -> List[Post]:
        """Fetch all posts within a given date range

        Args:
            date_range: Date range to search in
            sources: Optional list of source names to filter

        Returns:
            List of posts found in the range
        """
        all_posts = []

        for crawler in self.crawlers:
            # Filter by sources if specified
            if sources and crawler.source_name not in sources:
                continue

            try:
                posts = crawler.fetch_posts_in_range(date_range)
                all_posts.extend(posts)
                logger.info(f"{crawler.source_name}: {len(posts)} posts found")

            except Exception as e:
                logger.error(f"Error crawling {crawler.source_name}: {e}")

        logger.info(f"Total posts found: {len(all_posts)}")
        return all_posts
