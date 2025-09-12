"""
Save service - Infrastructure
Hexagonal Architecture DDD
"""
import json
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from ...domain.entities.post import Post


class SaveService:
    """
    JSON save service for technology watch data.

    Allows saving watch results only in JSON format
    in the var/saves/ folder.
    """

    def __init__(self, saves_directory: str = "var/saves"):
        self.saves_directory = Path(saves_directory)
        self.saves_directory.mkdir(parents=True, exist_ok=True)

    def save_all_formats(self, posts: List[Post], metadata: Dict[str, Any] = None) -> str:
        """
        Save posts in JSON format only.

        Args:
            posts: List of posts to save
            metadata: Optional metadata

        Returns:
            Save identifier (filename without extension)
        """
        if metadata is None:
            metadata = self._generate_metadata(posts)

        # Generate unique save identifier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_id = f"veille_{timestamp}"

        # Save only in JSON
        self.save_json(posts, metadata, save_id)

        return save_id

    def save_json(self, posts: List[Post], metadata: Dict[str, Any], save_id: str) -> Path:
        """Save in structured JSON format"""
        filepath = self.saves_directory / f"{save_id}.json"

        data = {
            "metadata": metadata,
            "articles": [post.to_dict() for post in posts]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filepath

    def _generate_metadata(self, posts: List[Post]) -> Dict[str, Any]:
        """Generate metadata for a list of posts"""
        sources = list(set(post.source for post in posts if post.source))
        dates = [post.date for post in posts if post.date]

        return {
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(posts),
            "sources": sources,
            "format_version": "2.0",
            "date_range": {
                "earliest": min(dates).isoformat() if dates else None,
                "latest": max(dates).isoformat() if dates else None
            }
        }
