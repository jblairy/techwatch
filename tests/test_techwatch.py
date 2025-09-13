"""
Unit tests for the technology watch tool - DDD Architecture Compatible
Legacy file maintained for backward compatibility
"""
import unittest
from unittest.mock import Mock, patch
from datetime import date

# Import new DDD classes
from src.domain.entities.post import Post
from src.domain.value_objects.date_range import DateRange
from src.application.services.techwatch_service import TechWatchService
from src.presentation.cli.console_renderer import ConsoleRenderer


class TestPost(unittest.TestCase):
    """Tests for Post entity (DDD Architecture)"""

    def test_post_creation(self):
        post = Post(title="Test", url="http://example.com")
        self.assertEqual(post.title, "Test")
        self.assertEqual(post.url, "http://example.com")
        self.assertIsNone(post.date)
        self.assertIsNone(post.source)

    def test_post_with_all_fields(self):
        post = Post(
            title="Test Post",
            url="http://example.com",
            date=date(2025, 9, 8),
            source="Test Source"
        )
        self.assertEqual(post.title, "Test Post")
        self.assertEqual(post.url, "http://example.com")
        self.assertEqual(post.date, date(2025, 9, 8))
        self.assertEqual(post.source, "Test Source")

    def test_post_to_dict(self):
        """Test Post to dictionary conversion"""
        post = Post(
            title="Test Post",
            url="http://example.com",
            date=date(2025, 9, 8),
            source="Test Source"
        )
        result = post.to_dict()
        self.assertEqual(result['title'], "Test Post")
        self.assertEqual(result['date'], "2025-09-08")

    def test_post_equality(self):
        """Test Post equality based on title and URL"""
        post1 = Post(title="Test", url="http://example.com")
        post2 = Post(title="Test", url="http://example.com")
        post3 = Post(title="Different", url="http://example.com")

        self.assertEqual(post1, post2)
        self.assertNotEqual(post1, post3)

    def test_post_hash(self):
        """Test Post hash functionality"""
        post1 = Post(title="Test", url="http://example.com")
        post2 = Post(title="Test", url="http://example.com")

        self.assertEqual(hash(post1), hash(post2))


class TestDateRange(unittest.TestCase):
    """Tests for DateRange value object (DDD Architecture)"""

    def test_date_range_creation(self):
        start = date(2025, 9, 1)
        end = date(2025, 9, 8)
        date_range = DateRange(start_date=start, end_date=end)

        self.assertEqual(date_range.start_date, start)
        self.assertEqual(date_range.end_date, end)

    def test_date_range_validation(self):
        """Test that start date must be before or equal to end date"""
        start = date(2025, 9, 8)
        end = date(2025, 9, 1)

        with self.assertRaises(ValueError):
            DateRange(start_date=start, end_date=end)

    def test_from_days_back(self):
        """Test DateRange creation from days back"""
        with patch('src.domain.value_objects.date_range.date') as mock_date:
            mock_date.today.return_value = date(2025, 9, 8)

            # Test today only
            date_range = DateRange.from_days_back(0)
            self.assertEqual(date_range.start_date, date(2025, 9, 8))
            self.assertEqual(date_range.end_date, date(2025, 9, 8))

            # Test 7 days back
            date_range = DateRange.from_days_back(7)
            self.assertEqual(date_range.start_date, date(2025, 9, 1))
            self.assertEqual(date_range.end_date, date(2025, 9, 8))

    def test_contains(self):
        """Test if a date is within the range"""
        date_range = DateRange(
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 8)
        )

        self.assertTrue(date_range.contains(date(2025, 9, 5)))
        self.assertTrue(date_range.contains(date(2025, 9, 1)))
        self.assertTrue(date_range.contains(date(2025, 9, 8)))
        self.assertFalse(date_range.contains(date(2025, 8, 31)))
        self.assertFalse(date_range.contains(date(2025, 9, 9)))

    def test_duration_days(self):
        """Test duration calculation"""
        date_range = DateRange(
            start_date=date(2025, 9, 1),
            end_date=date(2025, 9, 8)
        )
        self.assertEqual(date_range.duration_days(), 8)


class TestTechWatchService(unittest.TestCase):
    """Tests for TechWatchService (Application Layer)"""

    def setUp(self):
        self.mock_crawlers = [Mock(), Mock()]
        self.mock_renderer = Mock()
        self.service = TechWatchService(
            crawlers=self.mock_crawlers,
            renderer=self.mock_renderer
        )

    def test_fetch_posts_in_range(self):
        """Test fetching posts within a date range"""
        # Setup mock data
        mock_posts1 = [Post(title="Post 1", url="http://example1.com")]
        mock_posts2 = [Post(title="Post 2", url="http://example2.com")]

        self.mock_crawlers[0].fetch_posts_in_range.return_value = mock_posts1
        self.mock_crawlers[0].source_name = "Source 1"
        self.mock_crawlers[1].fetch_posts_in_range.return_value = mock_posts2
        self.mock_crawlers[1].source_name = "Source 2"

        date_range = DateRange.from_days_back(7)
        result = self.service.fetch_posts_in_range(date_range)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].title, "Post 1")
        self.assertEqual(result[1].title, "Post 2")

    def test_fetch_posts_with_source_filter(self):
        """Test fetching posts with source filtering"""
        mock_posts = [Post(title="Post 1", url="http://example1.com")]

        self.mock_crawlers[0].fetch_posts_in_range.return_value = mock_posts
        self.mock_crawlers[0].source_name = "Source 1"
        self.mock_crawlers[1].fetch_posts_in_range.return_value = []
        self.mock_crawlers[1].source_name = "Source 2"

        date_range = DateRange.from_days_back(7)
        result = self.service.fetch_posts_in_range(date_range, sources=["Source 1"])

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Post 1")


class TestConsoleRenderer(unittest.TestCase):
    """Tests for ConsoleRenderer (Presentation Layer)"""

    def setUp(self):
        self.renderer = ConsoleRenderer()

    @patch('builtins.print')
    def test_render_posts_with_results(self, mock_print):
        """Test rendering posts when results are found"""
        posts = [
            Post(title="Test Post", url="http://example.com", date=date(2025, 9, 8)),
        ]
        date_range = DateRange.from_days_back(0)

        self.renderer.render_posts("Test Source", posts, date_range)

        # Verify print was called
        self.assertTrue(mock_print.called)

    @patch('builtins.print')
    def test_render_posts_no_results(self, mock_print):
        """Test rendering when no posts are found"""
        posts = []
        date_range = DateRange.from_days_back(0)

        self.renderer.render_posts("Test Source", posts, date_range)

        # Verify "No articles found" message
        mock_print.assert_any_call("❌ No articles found in this period.")

    @patch('builtins.print')
    def test_render_fallback_alert(self, mock_print):
        """Test rendering fallback alerts"""
        alert_message = "Test alert message"

        self.renderer.render_fallback_alert(alert_message)

        mock_print.assert_called_with(f"\n{alert_message}")


# Compatibility tests for legacy architecture (if needed)
class TestLegacyCompatibility(unittest.TestCase):
    """Compatibility tests with legacy architecture"""

    def test_post_entity_compatibility(self):
        """Test that Post entity is compatible with legacy usage"""
        post = Post("Test", "http://example.com")

        # Verify that basic attributes are present
        self.assertTrue(hasattr(post, 'title'))
        self.assertTrue(hasattr(post, 'url'))
        self.assertTrue(hasattr(post, 'date'))
        self.assertTrue(hasattr(post, 'source'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
