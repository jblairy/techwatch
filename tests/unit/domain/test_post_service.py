"""
Unit tests for Post domain services - DDD Hexagonal Architecture
"""
import unittest
from unittest.mock import Mock
from datetime import date, timedelta
from src.domain.entities.post import Post
from src.domain.value_objects.date_range import DateRange
from src.domain.services.post_service import PostFilteringService, PostAnalysisService


class TestPostFilteringService(unittest.TestCase):
    """Tests for post filtering service"""

    def setUp(self):
        self.service = PostFilteringService()
        self.posts = [
            Post("Post 1", "http://example.com/1", date(2025, 9, 8), "Source A"),
            Post("Post 2", "http://example.com/2", date(2025, 9, 7), "Source B"),
            Post("Post 3", "http://example.com/3", date(2025, 9, 6), "Source A"),
            Post("Post 4", "http://example.com/4", None, "Source C"),  # Without date
        ]

    def test_filter_by_date_range(self):
        """Test filtering by date range"""
        date_range = DateRange(date(2025, 9, 7), date(2025, 9, 8))

        result = self.service.filter_by_date_range(self.posts, date_range)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "Post 1")
        self.assertEqual(result[1].title, "Post 2")

    def test_filter_by_date_range_excludes_none_dates(self):
        """Test that filtering excludes posts without dates"""
        date_range = DateRange(date(2025, 9, 1), date(2025, 9, 10))

        result = self.service.filter_by_date_range(self.posts, date_range)

        # Should not include post without date
        self.assertEqual(len(result), 3)
        for post in result:
            self.assertIsNotNone(post.date)

    def test_filter_by_source(self):
        """Test filtering by source"""
        result = self.service.filter_by_source(self.posts, "Source A")

        self.assertEqual(len(result), 2)
        for post in result:
            self.assertEqual(post.source, "Source A")

    def test_filter_by_source_not_found(self):
        """Test filtering by non-existent source"""
        result = self.service.filter_by_source(self.posts, "Source X")

        self.assertEqual(len(result), 0)


class TestPostAnalysisService(unittest.TestCase):
    """Tests for post analysis service"""

    def setUp(self):
        self.service = PostAnalysisService()
        self.posts = [
            Post("Post 1", "http://example.com/1", date(2025, 9, 8), "Source A"),
            Post("Post 2", "http://example.com/2", date(2025, 9, 7), "Source B"),
            Post("Post 3", "http://example.com/3", date(2025, 9, 6), "Source A"),
            Post("Post 4", "http://example.com/4", None, "Source C"),
        ]

    def test_count_by_source(self):
        """Test counting by source"""
        result = self.service.count_by_source(self.posts)

        expected = {
            "Source A": 2,
            "Source B": 1,
            "Source C": 1
        }
        self.assertEqual(result, expected)

    def test_count_by_date(self):
        """Test counting by date"""
        result = self.service.count_by_date(self.posts)

        expected = {
            date(2025, 9, 8): 1,
            date(2025, 9, 7): 1,
            date(2025, 9, 6): 1
        }
        self.assertEqual(result, expected)

    def test_get_latest_posts(self):
        """Test getting the most recent posts"""
        result = self.service.get_latest_posts(self.posts, limit=2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].date, date(2025, 9, 8))
        self.assertEqual(result[1].date, date(2025, 9, 7))

    def test_get_latest_posts_excludes_none_dates(self):
        """Test that posts without dates are excluded from sorting"""
        result = self.service.get_latest_posts(self.posts, limit=10)

        # Should not include post without date
        self.assertEqual(len(result), 3)
        for post in result:
            self.assertIsNotNone(post.date)


if __name__ == '__main__':
    unittest.main()
