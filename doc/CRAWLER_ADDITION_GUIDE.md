def test_parse_posts_empty_content(self):
        """Test with empty content"""
        date_range = DateRange.today_only()
        posts = self.crawler.fetch_posts_in_range(date_range)
        self.assertEqual(len(posts), 0)

    @patch('requests.get')
    def test_fetch_posts_integration(self, mock_get):
        """Complete integration test"""
        mock_response = Mock()
        mock_response.text = "<xml>valid rss content</xml>"
        mock_get.return_value = mock_response

        date_range = DateRange.today_only()

        posts = self.crawler.fetch_posts_in_range(date_range)

        self.assertIsInstance(posts, list)
# Adding New Crawlers Guide - Hexagonal DDD Architecture

> **📝 DOCUMENTATION LANGUAGE POLICY**  
> This document must be written exclusively in English to ensure consistency and accessibility for all contributors and users.

## 🎯 Objective

This guide explains how to add new technical sources (crawlers) to the technology watch tool, following the hexagonal DDD architecture principles. It is up-to-date with the latest dynamic factory and import system (September 2025).

## 🏗️ Architecture Context

### Crawler Interface & Template
All crawlers must inherit from `BaseCrawler` (see `src/infrastructure/adapters/base_crawler.py`).
- You must implement the `source_name` property and the `fetch_posts_in_range(date_range: DateRange) -> List[Post]` method.
- Use the template file `template_crawler.py` in the crawlers directory for quick creation.
- See the docstring in `BaseCrawler` for a copy-paste example and contract details.

### Hexagonal DDD Layers
```
Infrastructure Layer (Adapters & External)
├── external/crawlers/          # 🕷️ Source-specific crawlers
├── adapters/crawler_adapter.py # 🔌 Technical adaptation
├── factories/crawler_factory.py# 🏭 Crawler creation (dynamic)
└── services/                   # 🛠️ Technical services
```

### Design Principles
- **Single Responsibility**: One crawler per source
- **Dependency Injection**: Crawlers receive dependencies via constructor (if needed)
- **Interface Segregation**: All crawlers implement `BaseCrawler`
- **Open/Closed**: New crawlers extend functionality without modifying existing code
- **Dynamic Discovery**: Crawlers are auto-discovered by filename and class name, no factory modification required

## 📋 Step-by-Step Process

### Step 1: Analysis and Planning 🔍

**1.1 Source Analysis**
```bash
# Manual source examination
curl -s "https://new-source.com" | head -200
curl -s "https://new-source.com/feed" | xmllint --format -
```

**1.2 Identify Content Structure**
- Article container elements
- Title extraction method
- URL extraction method
- Date format and location
- RSS/Atom feed availability

**1.3 Choose Parsing Strategy**
- **RSS/Atom**: Use Python standard library (`xml.etree.ElementTree`) for parsing (no external dependencies)
- **HTML**: Use `BeautifulSoup` (already included in project)
- **JSON API**: Use `requests` with JSON parsing

### Step 2: Create the Crawler 🕷️

**2.1 Create the crawler file**
```bash
# Create in the external/crawlers directory
cp src/infrastructure/external/crawlers/reddit_php_rss.py src/infrastructure/external/crawlers/new_source_crawler.py
# Or touch src/infrastructure/external/crawlers/new_source_crawler.py
```

**2.2 Implement the BaseCrawler interface**
- The crawler class name must end with `Crawler` and match the filename (PascalCase).
- Use **absolute imports** (e.g. `from src.domain.entities.post import Post`).
- Implement at least:
  - `source_name` property
  - `fetch_posts_in_range(self, date_range: DateRange) -> List[Post]`
- For RSS, use only the Python standard library for parsing (see `korben_crawler.py` or `reddit_php_rss.py` for examples).

**Example skeleton:**
```python
from datetime import date
from typing import List, Optional
import xml.etree.ElementTree as ET
from src.domain.entities.post import Post
from src.domain.value_objects.date_range import DateRange
from src.infrastructure.adapters.base_crawler import BaseCrawler

class NewSourceCrawler(BaseCrawler):
    """Crawler for New Source (https://new-source.com)"""
    RSS_URL = "https://new-source.com/feed"

    @property
    def source_name(self) -> str:
        return "New Source"

    def fetch_posts_in_range(self, date_range: DateRange) -> List[Post]:
        try:
            response = self.http_client.get(self.RSS_URL)
            root = ET.fromstring(response.text)
            items = root.findall(".//item")
            posts = []
            for item in items:
                post = self._parse_rss_item(item)
                if post and post.date and date_range.contains(post.date):
                    posts.append(post)
            return posts
        except Exception as e:
            self.logger.error(f"Error crawling {self.source_name}: {e}")
            return []

    def _parse_rss_item(self, item) -> Optional[Post]:
        # Implement RSS item parsing (see korben_crawler.py)
        pass
```

### Step 3: Dynamic Registration (No Factory Edit Needed) 🏭

- **No manual registration required!**
- The factory (`crawler_factory.py`) auto-discovers all files ending with `_crawler.py` and instantiates the class ending with `Crawler` in each file.
- To add a new crawler, simply drop the file in `src/infrastructure/external/crawlers/`.
- Make sure your crawler file is not ignored by `.gitignore` if you want it versioned.

### Step 4: Testing 🧪

**4.1 Unit Tests**
- Create a test file in `tests/unit/infrastructure/` (or similar).
- Use `unittest` and `unittest.mock` for HTTP and parsing mocks.
- Example:
```python
import unittest
from unittest.mock import Mock, patch
from datetime import date
from src.domain.entities.post import Post
from src.domain.value_objects.date_range import DateRange
from src.infrastructure.external.crawlers.new_source_crawler import NewSourceCrawler

class TestNewSourceCrawler(unittest.TestCase):
    def setUp(self):
        self.http_client = Mock()
        self.crawler = NewSourceCrawler()
        self.crawler.http_client = self.http_client

    def test_parse_posts_empty_content(self):
        date_range = DateRange.today_only()
        posts = self.crawler.fetch_posts_in_range(date_range)
        self.assertEqual(len(posts), 0)

    @patch('requests.get')
    def test_fetch_posts_integration(self, mock_get):
        mock_response = Mock()
        mock_response.text = "<xml>valid rss content</xml>"
        mock_get.return_value = mock_response
        date_range = DateRange.today_only()
        posts = self.crawler.fetch_posts_in_range(date_range)
        self.assertIsInstance(posts, list)
```

**4.2 Manual Testing**
```bash
python veille_service.py --source new-source --days 1
python main.py show --source new-source
```

### Step 5: Documentation 📚

**5.1 Document specifics**
- Add a complete docstring to your crawler class describing:
  - Content type
  - Update frequency
  - Parsing method
  - Known limitations
  - Special features

## 🔧 Technical Implementation Details

### Dependency Injection Pattern
- If your crawler needs dependencies, set them as attributes (see `BaseCrawler`).

### Domain Entity Creation
- Always return a list of `Post` domain entities from your parsing methods.

### Error Handling
- Use try/except blocks and log errors for robustness.

## ✅ Integration Checklist

- [ ] **Crawler created** in `src/infrastructure/external/crawlers/`
- [ ] **No factory update needed** (dynamic discovery)
- [ ] **Unit tests** created and passing
- [ ] **Manual testing** completed successfully
- [ ] **Documentation** updated (README.md, etc.)
- [ ] **Error handling** implemented
- [ ] **Logging** added for debugging
- [ ] **Date filtering** respects DateRange
- [ ] **Domain entities** properly created

## 🎯 Architecture Benefits

### Separation of Concerns
- **Domain Layer**: Post entities with business rules
- **Application Layer**: Use cases and orchestration  
- **Infrastructure Layer**: Technical crawlers and adapters
- **Presentation Layer**: User interfaces (CLI/GUI)

### Testability
- Unit tests for business logic (domain)
- Integration tests for crawlers (infrastructure)
- Mocking of external dependencies
- Isolated testing per layer

### Maintainability
- New crawlers don't impact existing ones
- Clear interfaces and contracts
- Dependency injection for flexibility
- Can be replaced without impacting business logic

### Extensibility
- Easy addition of new sources
- Support for different content types (RSS/HTML/JSON)
- Pluggable architecture with dynamic factory pattern
- Future-proof for new parsing strategies

---

*This guide reflects the hexagonal DDD architecture implemented in September 2025, with dynamic crawler discovery and no external RSS dependencies.*
