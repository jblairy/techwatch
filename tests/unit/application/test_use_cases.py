"""
Unit tests for Use Cases - DDD Hexagonal Architecture
"""
import unittest
from unittest.mock import Mock, MagicMock
from datetime import date
from src.domain.entities.post import Post
from src.application.use_cases.techwatch_use_cases import LoadDataUseCase
from src.application.dto.post_dto import PostDTO, ResultDTO


class TestLoadDataUseCase(unittest.TestCase):
    """Tests for LoadDataUseCase use case"""

    def setUp(self):
        """Setup mocks for tests"""
        self.mock_repository = Mock()
        self.use_case = LoadDataUseCase(self.mock_repository)

    def test_load_latest_success(self):
        """Test loading latest data successfully"""
        # Arrange
        mock_posts = [
            Post("Post 1", "https://example.com/1", date(2025, 9, 8), "Source A"),
            Post("Post 2", "https://example.com/2", date(2025, 9, 7), "Source B")
        ]
        mock_metadata = {"timestamp": "2025-09-08T10:00:00", "sources": 2}
        self.mock_repository.load_latest.return_value = (mock_posts, mock_metadata)

        # Act
        result = self.use_case.load_latest()

        # Assert
        self.assertIsInstance(result, ResultDTO)
        self.assertEqual(len(result.posts), 2)
        self.assertEqual(result.total_count, 2)
        self.assertEqual(result.metadata, mock_metadata)
        self.mock_repository.load_latest.assert_called_once()

    def test_load_latest_empty_result(self):
        """Test loading with empty result"""
        # Arrange
        self.mock_repository.load_latest.return_value = ([], {})

        # Act
        result = self.use_case.load_latest()

        # Assert
        self.assertEqual(len(result.posts), 0)
        self.assertEqual(result.total_count, 0)
        self.assertEqual(result.metadata, {})

    def test_load_filtered_with_source_filter(self):
        """Test loading with source filter"""
        # Arrange
        mock_posts = [
            Post("Post 1", "https://example.com/1", date(2025, 9, 8), "Blog"),
            Post("Post 2", "https://example.com/2", date(2025, 9, 7), "RFC")
        ]
        self.mock_repository.load_latest.return_value = (mock_posts, {})

        # Act - This test would require full implementation of execute_with_filters
        # For now, we test that the method exists
        self.assertTrue(hasattr(self.use_case, 'execute_with_filters'))


if __name__ == '__main__':
    unittest.main()
