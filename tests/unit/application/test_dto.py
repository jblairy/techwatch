"""
Unit tests for DTOs - DDD Hexagonal Architecture
"""
import unittest
from datetime import date
from src.domain.entities.post import Post
from src.application.dto.post_dto import PostDTO, VeilleResultDTO


class TestPostDTO(unittest.TestCase):
    """Tests for Post DTO"""

    def test_from_entity_complete(self):
        """Test DTO creation from complete entity"""
        post = Post(
            title="Test Post",
            url="https://example.com",
            date=date(2025, 9, 8),
            source="Test Source",
            description="Test description"
        )

        dto = PostDTO.from_domain_entity(post)

        self.assertEqual(dto.title, "Test Post")
        self.assertEqual(dto.url, "https://example.com")
        self.assertEqual(dto.date, "2025-09-08")
        self.assertEqual(dto.source, "Test Source")
        self.assertEqual(dto.description, "Test description")

    def test_from_entity_minimal(self):
        """Test DTO creation from minimal entity"""
        post = Post(title="Minimal Post", url="https://example.com")

        dto = PostDTO.from_domain_entity(post)

        self.assertEqual(dto.title, "Minimal Post")
        self.assertEqual(dto.url, "https://example.com")
        self.assertEqual(dto.date, "")
        self.assertEqual(dto.source, None)
        self.assertEqual(dto.description, None)

    def test_to_entity(self):
        """Test DTO to entity conversion"""
        dto = PostDTO(
            title="DTO Post",
            url="https://example.com",
            date="2025-09-08",
            source="DTO Source"
        )

        entity = dto.to_entity()

        self.assertIsInstance(entity, Post)
        self.assertEqual(entity.title, "DTO Post")
        self.assertEqual(entity.url, "https://example.com")
        self.assertEqual(entity.date, date(2025, 9, 8))
        self.assertEqual(entity.source, "DTO Source")


class TestVeilleResultDTO(unittest.TestCase):
    """Tests for VeilleResult DTO"""

    def test_creation_with_posts(self):
        """Test creation with list of posts"""
        posts = [
            PostDTO(title="Post 1", url="https://example.com/1", date="2025-09-08", source="Source 1"),
            PostDTO(title="Post 2", url="https://example.com/2", date="2025-09-09", source="Source 2")
        ]
        metadata = {"execution_time": "2.5s", "sources_count": 5}

        result = VeilleResultDTO(
            posts=posts,
            metadata=metadata,
            total_count=2
        )

        self.assertEqual(len(result.posts), 2)
        self.assertEqual(result.total_count, 2)
        self.assertEqual(result.metadata["execution_time"], "2.5s")

    def test_creation_empty(self):
        """Test creation with empty result"""
        result = VeilleResultDTO(
            posts=[],
            metadata={},
            total_count=0
        )

        self.assertEqual(len(result.posts), 0)
        self.assertEqual(result.total_count, 0)
        self.assertEqual(result.metadata, {})


if __name__ == '__main__':
    unittest.main()
