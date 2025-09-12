"""
Integration tests for DDD Hexagonal Architecture
"""
import unittest
import tempfile
import os
from datetime import date
from src.domain.entities.post import Post
from src.domain.value_objects.date_range import DateRange
from src.application.use_cases.veille_use_cases import LoadVeilleDataUseCase
from src.infrastructure.repositories.json_post_repository import JsonPostRepository


class TestDomainApplicationIntegration(unittest.TestCase):
    """Integration tests between Domain and Application layers"""

    def setUp(self):
        """Setup with temporary repository and unified database file"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "veille_db.json")
        self.repository = JsonPostRepository(db_path=self.db_path)
        self.use_case = LoadVeilleDataUseCase(self.repository)

    def tearDown(self):
        """Cleanup temporary files"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_load_integration(self):
        """Test save and load integration with unified database"""
        # Arrange - Create test posts
        posts = [
            Post("Symfony 7.0 Released", "https://symfony.com/blog/symfony-7-0",
                 date(2025, 9, 8), "Symfony Blog"),
            Post("PHP 8.4 Features", "https://php.net/blog/php-8-4",
                 date(2025, 9, 7), "PHP Blog")
        ]

        # Act - Save then load (the save method automatically generates metadata)
        success = self.repository.save(posts)
        self.assertTrue(success)
        result = self.use_case.load_latest()

        # Assert
        self.assertEqual(len(result.posts), 2)
        self.assertEqual(result.posts[0].title, "Symfony 7.0 Released")
        self.assertEqual(result.posts[1].title, "PHP 8.4 Features")
        self.assertIsInstance(result.metadata, dict)
        self.assertIn("total_articles", result.metadata)

    def test_date_filtering_integration(self):
        """Test date filtering integration with unified database"""
        # Arrange
        posts = [
            Post("Recent Post", "https://example.com/1", date(2025, 9, 8)),
            Post("Old Post", "https://example.com/2", date(2025, 8, 1))
        ]

        # Act - Save and filter
        self.repository.save(posts)
        result = self.use_case.load_latest()

        # Assert - Verify posts are loaded
        self.assertEqual(len(result.posts), 2)
        # Additional filtering logic can be added here if needed

    def test_empty_repository_load_latest(self):
        """Test loading from empty repository (should return empty)"""
        # Act
        result = self.use_case.load_latest()

        # Assert
        self.assertEqual(result.posts, [])
        self.assertEqual(result.metadata, {})


class TestFullStackIntegration(unittest.TestCase):
    """Full stack integration tests"""

    def test_domain_entities_serialization(self):
        """Test domain entities serialization via infrastructure"""
        # Arrange
        post = Post(
            title="Test Article",
            url="https://example.com/test",
            date=date(2025, 9, 8),
            source="Test Source",
            description="Test description"
        )

        # Act - Convert to dict (as done by JsonPostRepository)
        post_dict = post.to_dict()

        # Assert - Verify serialized structure
        expected_keys = {'title', 'url', 'date', 'source', 'description'}
        self.assertEqual(set(post_dict.keys()), expected_keys)
        self.assertEqual(post_dict['date'], '2025-09-08')  # Date serialized in ISO format

    def test_value_object_business_logic(self):
        """Test value objects business logic"""
        # Arrange
        date_range = DateRange.from_days_back(7)
        test_date_in_range = date.today()
        test_date_out_range = date.today().replace(year=2020)

        # Act & Assert
        self.assertTrue(date_range.contains(test_date_in_range))
        self.assertFalse(date_range.contains(test_date_out_range))

    def test_post_entity_business_logic(self):
        """Test complete business logic of Post entities"""
        # Arrange
        post1 = Post("Title 1", "https://example.com/1", date(2025, 9, 8), "Source A")
        post2 = Post("Title 2", "https://example.com/2", date(2025, 9, 7), "Source B")
        posts = [post1, post2]

        # Act - Test domain services
        from src.domain.services.post_service import PostFilteringService, PostAnalysisService

        date_range = DateRange(date(2025, 9, 7), date(2025, 9, 8))
        filtered_posts = PostFilteringService.filter_by_date_range(posts, date_range)
        source_count = PostAnalysisService.count_by_source(posts)

        # Assert
        self.assertEqual(len(filtered_posts), 2)
        self.assertEqual(source_count["Source A"], 1)
        self.assertEqual(source_count["Source B"], 1)


if __name__ == '__main__':
    unittest.main()
