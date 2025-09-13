"""
Unit tests for JSON Post Repository - DDD Hexagonal Architecture
"""
import unittest
from unittest.mock import Mock, patch, mock_open
import json
import tempfile
import shutil
from datetime import date
from pathlib import Path
from src.domain.entities.post import Post
from src.infrastructure.repositories.json_post_repository import JsonPostRepository


class TestJsonPostRepository(unittest.TestCase):
    """Tests for JSON implementation of Post repository"""

    def setUp(self):
        """Test setup with temporary directory and unified database file"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "techwatch_db.json"
        self.repository = JsonPostRepository(db_path=str(self.db_path))

    def tearDown(self):
        """Cleanup temporary files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_posts_success(self):
        """Test successful posts saving to unified database"""
        posts = [
            Post("Test Post", "https://example.com", date(2025, 9, 8), "Test Source")
        ]
        success = self.repository.save(posts)
        self.assertTrue(success)
        self.assertTrue(self.db_path.exists())

    def test_load_latest_file_not_exists(self):
        """Test loading when no file exists (should return empty)"""
        posts, metadata = self.repository.load_latest()
        self.assertEqual(posts, [])
        self.assertEqual(metadata, {})

    def test_load_latest_with_existing_file(self):
        """Test loading from unified database when it exists"""
        posts = [Post("Test Post", "https://example.com", date(2025, 9, 8), "Test Source")]
        self.repository.save(posts)
        loaded_posts, metadata = self.repository.load_latest()
        self.assertEqual(len(loaded_posts), 1)
        self.assertEqual(loaded_posts[0].title, "Test Post")
        self.assertEqual(loaded_posts[0].url, "https://example.com")
        self.assertEqual(loaded_posts[0].source, "Test Source")


if __name__ == '__main__':
    unittest.main()
