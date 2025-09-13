"""
JSON Persistence Adapter - Infrastructure
Hexagonal Architecture DDD

This repository now manages a single database file (techwatch_db.json) for all technology watch articles.
All new articles are appended to this file, and duplicates are avoided by URL.
This design ensures robust, maintainable, and scalable persistence, and is ready for future migration to a real database if needed.
"""
import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Tuple
from pathlib import Path
import logging

from ...domain.entities.post import Post
from ...domain.repositories.post_repository import PostRepository

logger = logging.getLogger(__name__)

class JsonPostRepository(PostRepository):
    """
    Concrete repository implementation for a single JSON file persistence.

    This class manages a unique database file (techwatch_db.json).
    All articles are stored in this file, and all read/write operations are centralized.
    """

    def __init__(self, db_path: str = "var/saves/techwatch_db.json"):
        """
        Initialize the repository with the path to the database file.
        Creates the parent directory if it does not exist.
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, posts: List[Post], metadata: Dict[str, Any] = None) -> bool:
        """
        Append new posts to the database, avoiding duplicates by URL.
        Metadata is updated with each save (last metadata wins).
        Returns True on success, False otherwise.
        """
        try:
            # Load existing database
            if self.db_path.exists():
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                existing_articles = data.get('articles', [])
            else:
                existing_articles = []

            # Build set of existing URLs to avoid duplicates
            existing_urls = set(a.get('url') for a in existing_articles)
            new_articles = [self._post_to_dict(post) for post in posts if post.url not in existing_urls]

            # Merge articles
            all_articles = existing_articles + new_articles

            # Generate or update metadata
            if metadata is None:
                metadata = self._generate_metadata(posts)
            # Note: only the latest metadata is kept

            # Save to database
            db_data = {
                "metadata": metadata,
                "articles": all_articles
            }
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(db_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Database updated: {len(new_articles)} new posts, total {len(all_articles)} posts.")
            return True
        except Exception as e:
            logger.error(f"Error saving posts to database: {e}")
            return False

    def load_latest(self) -> Tuple[List[Post], Dict[str, Any]]:
        """
        Load all posts and metadata from the database file.
        Returns a tuple (posts, metadata).
        """
        try:
            if not self.db_path.exists():
                logger.warning("Database file not found")
                return [], {}
            with open(self.db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            metadata = data.get('metadata', {})
            articles_data = data.get('articles', [])
            posts = []
            for article_data in articles_data:
                try:
                    post = self._dict_to_post(article_data)
                    posts.append(post)
                except Exception as e:
                    logger.warning(f"Error converting article to post: {e}")
                    continue
            logger.info(f"Loaded {len(posts)} posts from database")
            return posts, metadata
        except Exception as e:
            logger.error(f"Error loading posts from database: {e}")
            return [], {}

    def _generate_metadata(self, posts: List[Post]) -> Dict[str, Any]:
        """
        Generate metadata for a list of posts.
        Includes sources, date range, and format version.
        """
        sources = list(set(post.source for post in posts))
        dates = [post.date for post in posts if post.date]

        metadata = {
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(posts),
            "sources": sources,
            "format_version": "2.0"
        }

        if dates:
            metadata["date_range"] = {
                "earliest": min(dates).isoformat(),
                "latest": max(dates).isoformat(),
                "days_range": (max(dates) - min(dates)).days + 1
            }

        return metadata

    def _post_to_dict(self, post: Post) -> Dict[str, Any]:
        """
        Convert a Post entity to a dictionary for JSON serialization.
        """
        return {
            "title": post.title,
            "url": post.url,
            "date": post.date.isoformat() if post.date else None,
            "source": post.source
        }

    def _dict_to_post(self, data: Dict[str, Any]) -> Post:
        """
        Convert a dictionary to a Post entity.
        Handles ISO and common date formats.
        """
        post_date = None
        if data.get('date'):
            try:
                post_date = datetime.fromisoformat(data['date']).date()
            except (ValueError, TypeError):
                try:
                    post_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    post_date = None

        return Post(
            title=data.get('title', ''),
            url=data.get('url', ''),
            date=post_date,
            source=data.get('source', '')
        )

    # Deprecated methods for legacy tests (raise NotImplementedError)
    def delete_save(self, *args, **kwargs):
        """Deprecated: multi-file save deletion is not supported anymore."""
        raise NotImplementedError("delete_save is deprecated. Only techwatch_db.json is supported.")

    def list_available_saves(self, *args, **kwargs):
        """Deprecated: multi-file listing is not supported anymore."""
        raise NotImplementedError("list_available_saves is deprecated. Only techwatch_db.json is supported.")

    def load_by_id(self, *args, **kwargs):
        """Deprecated: loading by ID is not supported anymore."""
        raise NotImplementedError("load_by_id is deprecated. Only techwatch_db.json is supported.")

    def load_from_file(self, *args, **kwargs):
        """Deprecated: loading from file is not supported anymore."""
        raise NotImplementedError("load_from_file is deprecated. Only techwatch_db.json is supported.")

