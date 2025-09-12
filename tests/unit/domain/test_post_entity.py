"""
Unit tests for Post entity - DDD Hexagonal Architecture
"""
import unittest
from datetime import date
from src.domain.entities.post import Post


class TestPost(unittest.TestCase):
    """Tests for Post entity"""

    def test_post_creation_minimal(self):
        """Test creating a post with minimal fields"""
        post = Post(title="Test Post", url="https://example.com")

        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.url, "https://example.com")
        self.assertIsNone(post.date)
        self.assertIsNone(post.source)
        self.assertIsNone(post.description)

    def test_post_creation_complete(self):
        """Test creating a post with all fields"""
        test_date = date(2025, 9, 8)
        post = Post(
            title="Complete Article",
            url="https://example.com/article",
            date=test_date,
            source="Test Source",
            description="Test description"
        )

        self.assertEqual(post.title, "Complete Article")
        self.assertEqual(post.url, "https://example.com/article")
        self.assertEqual(post.date, test_date)
        self.assertEqual(post.source, "Test Source")
        self.assertEqual(post.description, "Test description")

    def test_to_dict_with_date(self):
        """Test conversion to dictionary with date"""
        test_date = date(2025, 9, 8)
        post = Post(
            title="Test",
            url="https://example.com",
            date=test_date,
            source="Test Source"
        )

        result = post.to_dict()
        expected = {
            'title': 'Test',
            'url': 'https://example.com',
            'date': '2025-09-08',
            'source': 'Test Source',
            'description': None
        }

        self.assertEqual(result, expected)

    def test_to_dict_without_date(self):
        """Test conversion to dictionary without date"""
        post = Post(title="Test", url="https://example.com")

        result = post.to_dict()
        expected = {
            'title': 'Test',
            'url': 'https://example.com',
            'date': None,
            'source': None,
            'description': None
        }

        self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
