#!/usr/bin/env python3
"""
Technology watch console service
Responsible for crawling sources and generating JSON files
VERSION 2.0 - Hexagonal Architecture DDD
"""

import logging
import os
import sys
from datetime import datetime, date, timedelta
from typing import List, Optional
import argparse

# Imports from the new hexagonal architecture
from src.application.use_cases.techwatch_use_cases import SaveDataUseCase, AnalyzeDataUseCase
from src.application.dto.post_dto import PostDTO
from src.infrastructure.repositories.json_post_repository import JsonPostRepository
from src.infrastructure.adapters.crawler_adapter import FileCrawlerRepository

# Legacy imports for transition (to be migrated progressively)
from src.infrastructure.factories.crawler_factory import CrawlerFactory
from src.application.services.techwatch_service import TechWatchService
from src.presentation.cli.console_renderer import ConsoleRenderer
from src.infrastructure.services.save_service import SaveService
from src.domain.entities.post import Post
from src.domain.value_objects.date_range import DateRange

# Optional import of plyer for notifications
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

class TechWatchConsoleService:
    """
    Console service for automatic crawling and unified JSON database update.
    This service now writes all crawled articles to a single file (techwatch_db.json).
    Notifications and statistics are based on this unified source.
    """

    def __init__(self, silent_mode: bool = False):
        self.silent_mode = silent_mode
        self.setup_logging()

        # Initialize necessary components
        self.crawler_factory = CrawlerFactory()
        self.console_renderer = ConsoleRenderer()

        # Get all available crawlers
        all_crawlers = self.crawler_factory.get_all_crawlers()

        # Services
        self.techwatch_service = TechWatchService(crawlers=all_crawlers, renderer=self.console_renderer)
        self.json_repo = JsonPostRepository()

        # Session statistics
        self.session_stats = {
            'sources_crawled': 0,
            'articles_found': 0,
            'sources_success': 0,
            'sources_failed': 0,
            'start_time': None,
            'end_time': None
        }

    def setup_logging(self):
        """Logging configuration for the console service (file only, no console)"""
        os.makedirs('var/logs', exist_ok=True)
        log_file = 'var/logs/techwatch_service.log'
        # Remove all handlers if already set
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file)
            ]
        )

        self.logger = logging.getLogger(__name__)
        self.logger.info("=== Starting technology watch console service ===")

    def run_techwatch(self, days_back: Optional[int] = None, sources: Optional[List[str]] = None) -> bool:
        """
        Launch a complete watch session and update the unified database.

        Args:
            days_back: Number of days to go back in time (None = no filter)
            sources: List of sources to crawl (all if None)

        Returns:
            bool: True if the watch went well
        """
        self.session_stats['start_time'] = datetime.now()

        try:
            if days_back is None:
                # Pas de filtre de période
                start_date = date(1970, 1, 1)  # date min universelle
                end_date = date.today()
                self.logger.info("Aucune période de filtre - tous les articles seront récupérés")
            else:
                self.logger.info(f"Starting watch - {days_back} days back")
                end_date = date.today()
                start_date = end_date - timedelta(days=days_back)
                self.logger.info(f"Period: {start_date} -> {end_date}")
            date_range = DateRange(start_date=start_date, end_date=end_date)

            # Launch crawling
            posts = self.techwatch_service.fetch_posts_in_range(date_range, sources)

            self.session_stats['articles_found'] = len(posts)
            available_sources = self.crawler_factory.get_available_sources()
            self.session_stats['sources_crawled'] = len(available_sources)

            if posts:
                # Save results to the unified database
                success = self.json_repo.save(posts)
                if success:
                    self.logger.info(f"Results saved to techwatch_db.json")
                else:
                    self.logger.error(f"Error saving results to techwatch_db.json")

                # Check for new articles
                new_articles_count = self.check_for_new_articles(posts)

                # Final statistics
                self.log_session_stats()

                # Notification if new articles
                if new_articles_count > 0:
                    self.send_notification(new_articles_count, len(posts))

                return True
            else:
                self.logger.warning("No articles found during this session")
                return False

        except Exception as e:
            self.logger.error(f"Error during watch: {e}", exc_info=True)
            return False
        finally:
            self.session_stats['end_time'] = datetime.now()

    def check_for_new_articles(self, current_posts: List[Post]) -> int:
        """
        Check if there are new articles compared to the unified database.
        Uses a simple hash based on title + URL for detection.
        """
        try:
            # Load all existing articles from techwatch_db.json
            existing_posts, _ = self.json_repo.load_latest()
            existing_hashes = set(f"{post.title}|{post.url}" for post in existing_posts)

            # Count new articles
            new_count = 0
            for post in current_posts:
                post_hash = f"{post.title}|{post.url}"
                if post_hash not in existing_hashes:
                    new_count += 1

            self.logger.info(f"New articles detected: {new_count}/{len(current_posts)}")
            return new_count

        except Exception as e:
            self.logger.error(f"Error detecting new articles: {e}")
            return 0

    def send_notification(self, new_articles: int, total_articles: int):
        """Send desktop notification of results"""
        if not NOTIFICATIONS_AVAILABLE:
            self.logger.info("Notifications not available (plyer not installed)")
            return

        try:
            notification.notify(
                title="🔍 Technology Watch",
                message=f"✅ {new_articles} new articles out of {total_articles} found",
                timeout=10
            )
            self.logger.info(f"Notification sent: {new_articles} new articles")
        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")

    def log_session_stats(self):
        """Log session statistics"""
        if self.session_stats['start_time'] and self.session_stats['end_time']:
            duration = self.session_stats['end_time'] - self.session_stats['start_time']
            duration_str = str(duration).split('.')[0]  # Remove microseconds

            self.logger.info("=== SESSION STATISTICS ===")
            self.logger.info(f"Duration: {duration_str}")
            self.logger.info(f"Sources crawled: {self.session_stats['sources_crawled']}")
            self.logger.info(f"Articles found: {self.session_stats['articles_found']}")

def main():
    """Entry point of the console service"""
    parser = argparse.ArgumentParser(description="Technology watch console service")
    parser.add_argument(
        "--days",
        type=int,
        default=None,
        help="Number of days back to crawl (default: None)"
    )
    parser.add_argument(
        "--sources",
        nargs='+',
        help="Specific sources to crawl (all by default)"
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Silent mode (no console output)"
    )

    args = parser.parse_args()

    # Create service
    service = TechWatchConsoleService(silent_mode=args.silent)

    try:
        # One-time mode uniquement
        success = service.run_techwatch(
            days_back=args.days,
            sources=args.sources
        )

        if success:
            print(f"✅ Watch completed successfully - {service.session_stats['articles_found']} articles found")
            sys.exit(0)
        else:
            print("❌ Watch completed with errors")
            sys.exit(1)

    except KeyboardInterrupt:
        service.logger.info("Stop requested by user")
        print("\n🛑 Service stopped by user")
        sys.exit(0)
    except Exception as e:
        service.logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
