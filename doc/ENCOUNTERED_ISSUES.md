- [ ] Technical specifications documented

### Architecture Compliance
- [ ] Domain entities used correctly
- [ ] Dependency injection respected
- [ ] Layer separation maintained
- [ ] Business logic in domain layer
- [ ] Technical details in infrastructure layer
# Encountered Issues and Solutions (Experience Feedback)
---
> **📝 DOCUMENTATION LANGUAGE POLICY**  
*This experience feedback document helps prevent recurring issues and improves development efficiency - Updated September 2025*
> This document must be written exclusively in English to ensure consistency and accessibility for all contributors and users.

> ⚠️ **APPEND-ONLY FILE** ⚠️  
> This file is designed to preserve the complete history of encountered issues.  
> **NEVER DELETE OR MODIFY** existing issues - only add new sections.  
> Objective: Capitalize on experience to help future developments and AI agent.

This document compiles technical issues encountered during crawler development and their solutions. It serves as a reference to anticipate and quickly resolve similar problems.

## 🔧 Technical Issues

### Issue 1: Specific HTML Structure
**Problem**: The Laminas blog uses a complex HTML structure with very specific CSS classes (`col-lg-4 col-sm-6 col-xs-12 mb-3 h-entry`).
**Solution**: Create specialized parsing with BeautifulSoup using `find_all("div", class_="col-lg-4 col-sm-6 col-xs-12 mb-3 h-entry")`.
**Lesson**: Always examine the actual HTML source code of the site before implementing parsing.

### Issue 2: Non-standard Date Format
**Problem**: Laminas uses the format "27 Aug, 2025" in `<small class="text-body-secondary">` instead of usual ISO formats.
**Solution**: Implement `_parse_date_text()` with multiple supported datetime formats:
```python
formats = [
    "%d %b, %Y",   # "27 Aug, 2025"
    "%d %B, %Y",   # "27 August, 2025"
    "%B %d, %Y",   # "August 27, 2025"
    "%Y-%m-%d",    # "2025-08-27"
]
```
**Lesson**: Plan for multiple date formats and use a try/except approach for robustness.

### Issue 3: Link and Title Structure
**Problem**: The title is in an `<h4 class="card-title">` which is a child of an `<a>`, requiring specific DOM navigation.
**Solution**: Use `title_tag.find_parent("a")` to go back to the parent link.
**Lesson**: Understand DOM hierarchy well before extracting data.

### Issue 4: Syntax Errors in main.py
**Problem**: Duplicate line in `source_mapping` dictionary causing a SyntaxError.
**Solution**: Always check Python syntax after edits, especially in dictionaries.
**Lesson**: Use `get_errors` systematically after code modifications.

### Issue 5: README.md Inconsistency
**Problem**: Incorrect source count (12 instead of 13) and missing Laminas in examples.
**Solution**: Systematic update of all counters and lists in documentation.
**Lesson**: Documentation must be updated at the same time as code.

### Issue 6: Testing with Complex HTML Data
**Problem**: Creating unit tests with complex Bootstrap HTML.
**Solution**: Use BeautifulSoup directly in tests with representative HTML snippets.
**Lesson**: Tests should use realistic data, not simplified data.

### Issue 7: Simple HTML Structure but Complex Date Parsing (Rector)
**Problem**: The Rector blog uses a relatively simple HTML structure (`<div class="mb-4">` with `<h2 class="mb-0">`) but has sometimes malformed datetime attributes like `datetime="2025-05-Mon"`.
**Solution**: Create a specialized `_parse_datetime_attr()` method with regex to extract valid parts and fallback on `<time>` element text.
```python
def _parse_datetime_attr(self, datetime_attr: str) -> Optional[date]:
    # Extract a date in YYYY-MM-DD format
    date_match = re.search(r'(\d{4}-\d{1,2}-\d{1,2})', datetime_attr)
    if date_match:
        date_str = date_match.group(1)
        return datetime.strptime(date_str, "%Y-%m-%d").date()
```
**Lesson**: Always plan for non-standard data formats and create robust fallbacks.

### Issue 8: Absolute vs Relative URLs Management
**Problem**: Rector sometimes uses complete absolute URLs and sometimes relative URLs, requiring detection logic.
**Solution**: Check if URL starts with "http" before using `urljoin()`.
```python
if href.startswith("http"):
    url = href
else:
    url = urljoin(self.BASE_URL, href)
```
**Lesson**: Always test URL type before processing to avoid malformed URLs.

### Issue 9: Large Volume of Articles to Process
**Problem**: Rector has 69 articles on its main page, which increases processing time.
**Solution**: Optimize parsing by limiting fallback to max 10 articles and use DEBUG logs for tracking.
**Lesson**: Plan for performance limitations for sites with lots of content.

### Issue 10: Incomplete Integration After AI Agent Bug (Freek.dev)
**Problem**: The previous agent had partially integrated the freek-dev crawler but forgot to add the entry in the `source_names` dictionary in main.py, causing incorrect display.
**Solution**: Systematically follow the complete checklist and verify all integration points:
1. Crawler created ✅
2. Factory updated ✅  
3. main.py - choices ✅
4. main.py - mapping ✅
5. main.py - source_names ❌ (missing)
6. Complete tests ❌ (missing)
**Lesson**: Incomplete integration can cause subtle malfunctions. The checklist must be followed completely.

### Issue 11: Date Parsing with Ordinal Suffixes (Freek.dev)
**Problem**: Freek.dev uses date formats with English ordinal suffixes like "Sep 4th 2025", "Sep 1st 2025", "Sep 2nd 2025".
**Solution**: Create a `_parse_date_text()` function with regex to clean suffixes before parsing:
```python
def _parse_date_text(self, date_text: str) -> Optional[date]:
    # Clean ordinal suffixes (1st, 2nd, 3rd, 4th, etc.)
    cleaned_text = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_text)
    
    formats = [
        "%b %d %Y",      # "Sep 4 2025" (after cleaning)
        "%B %d %Y",      # "September 4 2025"
        "%Y-%m-%d",      # "2025-09-04"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(cleaned_text, fmt).date()
        except ValueError:
            continue
```
**Lesson**: Always anticipate non-standard date formats and implement robust cleaning.

### Issue 12: RSS Feed Parsing Complexity (Various Sources)
**Problem**: Different RSS implementations with varying XML structures and namespaces.
**Solution**: Use `feedparser` library with robust error handling and multiple extraction strategies.
**Lesson**: RSS/Atom standards are implemented differently; always have fallback methods.

### Issue 13: Rate Limiting and Anti-Bot Protection
**Problem**: Some sources implement rate limiting or detect automated requests.
**Solution**: Add delays between requests and use realistic User-Agent headers.
```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Technology Watch Tool)'
}
time.sleep(1)  # Respectful delay
```
**Lesson**: Respect website resources and implement ethical scraping practices.

### Issue 14: Dynamic Content Loading (JavaScript)
**Problem**: Some modern sites load content dynamically via JavaScript, making it invisible to simple HTTP requests.
**Solution**: For now, focus on RSS feeds or static HTML. Consider Selenium for future complex cases.
**Lesson**: Not all content is accessible via simple HTTP requests; plan alternative data sources.

### Issue 15: Character Encoding Issues
**Problem**: Some sources use different character encodings, causing garbled text.
**Solution**: Explicitly handle encoding detection and conversion.
```python
response.encoding = response.apparent_encoding
content = response.text
```
**Lesson**: Always handle character encoding properly for international content.

### Issue 16: SSL/TLS Certificate Issues
**Problem**: Some sources have SSL certificate problems causing connection failures.
**Solution**: Implement certificate verification with graceful fallback.
```python
try:
    response = requests.get(url, verify=True)
except requests.exceptions.SSLError:
    response = requests.get(url, verify=False)
```
**Lesson**: Handle SSL issues gracefully while maintaining security awareness.

### Issue 17: Hexagonal Architecture Migration Complexity
**Problem**: Migrating from monolithic to hexagonal DDD architecture while maintaining functionality.
**Solution**: Gradual migration layer by layer, starting with domain entities and moving outward.
**Lesson**: Architectural refactoring requires careful planning and extensive testing.

### Issue 18: Dependency Injection Implementation
**Problem**: Implementing proper dependency injection without a DI framework.
**Solution**: Use factory pattern with constructor injection for clean separation.
```python
class CrawlerFactory:
    def __init__(self):
        self.http_client = RequestsHTTPClient()
        self.html_parser = BeautifulSoupParser()
    
    def create_crawler(self, source: str):
        return SourceCrawler(self.http_client, self.html_parser)
```
**Lesson**: Dependency injection can be implemented effectively without heavy frameworks.

### Issue 19: Testing Hexagonal Architecture
**Problem**: Testing each layer independently while ensuring integration works.
**Solution**: Separate unit tests for domain/application layers and integration tests for infrastructure.
**Lesson**: Hexagonal architecture greatly improves testability when properly implemented.

### Issue 20: Performance Optimization in DDD Context
**Problem**: Ensuring performance doesn't degrade with additional abstraction layers.
**Solution**: Profile carefully and optimize at the right abstraction level.
**Lesson**: Clean architecture and performance are not mutually exclusive when designed properly.

---

## 📋 Integration Checklist (From Experience)

Based on all encountered issues, here's the complete integration checklist:

### Code Integration
- [ ] Crawler file created in correct location
- [ ] BaseCrawler interface properly implemented
- [ ] Factory registration completed
- [ ] main.py updated (choices, mapping, source_names)
- [ ] Error handling implemented
- [ ] Logging added

### Testing
- [ ] Unit tests written and passing
- [ ] Integration tests completed
- [ ] Manual testing performed
- [ ] Edge cases covered
- [ ] Performance acceptable

### Documentation
- [ ] README.md updated
- [ ] Source count corrected
- [ ] Examples updated

## 🧠 AI Agent Development Guidance

This section summarizes best practices and reminders for AI agents and developers working on this project:

- Always document encountered issues and solutions in English for consistency and accessibility.
- Never delete or modify existing issues in this file; only append new ones to preserve experience history.
- Systematically update documentation (README, source lists, counters) in sync with code changes and new features.
- Validate all code changes with error checking tools before merging or deploying.
- Use realistic, representative data for tests (especially HTML parsing).
- When adding features, identify the relevant layer (domain, application, infrastructure, presentation) and use dependency injection for new services or repositories.
- Add unit and integration tests for new logic and document any encountered issues here.
- Favor maintainable, extensible code: clear separation of concerns, type hints, and docstrings.
- For GUI features, use CustomTkinter widgets, prefer radio buttons and combo boxes for filters, and ensure all user actions are logged and errors are handled gracefully.
- Refer to this file and `DEVELOPMENT_CONTEXT.md` for architecture, extensibility, and troubleshooting guidance.

---

**Rappel important** : Toujours ajouter à la fin, jamais modifier les problématiques existantes !
