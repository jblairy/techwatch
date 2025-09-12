```
# Development Context - Technology Watch Tool
## 🧪 Testing Strategy
The technology watch tool is a Python application that automatically monitors 17 technical sources specialized in the PHP ecosystem and modern web development.
### Unit Tests (Domain Layer)
```python
# Pure business logic testing
tests/unit/domain/
├── test_post_entity.py        # Post business rules
├── test_date_range.py         # DateRange validation
└── test_post_service.py       # Filtering/analysis services
```
- **CustomTkinter** - Modern graphical interface (dark theme)
### Integration Tests (Infrastructure Layer)
```python
# Crawler and adapter testing
tests/integration/
├── test_crawler_integration.py  # Real crawler testing
├── test_repository_integration.py # Data persistence
└── test_ddd_integration.py      # Full architecture testing

**Migration**: September 2025 - Complete refactoring to clean architecture
### Manual Testing
```
# CLI testing
python main.py show --source <source_name> --days 7

# GUI testing
src/
│   │   └── post.py         # Post entity with business logic
# Service testing
python veille_service.py --verbose
│   │   └── post_repository.py
└── presentation/          # 🖥️ User Interfaces
## 🚀 Execution Modes
### PHP Ecosystem
### 1. Graphical Interface (Recommended)
- **Launch**: `python gui_main.py`
- **Features**: Modern interface, real-time visualization, integrated controls
- **Target**: End users, daily consultation
5. **Laminas Blog** - Laminas project updates
### 2. Command Line Interface
- **Launch**: `python main.py [command] [options]`
- **Features**: Automation, scripting, server integration
- **Target**: Developers, CI/CD automation
9. **A List Apart** - Web standards and best practices
### 3. Service Mode
- **Launch**: `python veille_service.py`
- **Features**: Background execution, scheduled tasks
- **Target**: Production servers, automated monitoring
13. **Freek Van der Herten** - PHP and Laravel expertise
## 🔧 Configuration and Extensibility
17. **Atlassian Blog** - Team collaboration tools
### Adding New Sources
1. Create a specialized crawler in `src/infrastructure/external/crawlers/`
2. Implement the `BaseCrawler` interface
3. Register in `CrawlerFactory`
4. Add unit tests
5. Update documentation
├── korben_crawler.py      # Korben blog parsing
### Architecture Benefits
- **Separation of concerns**: Each layer has a defined role
- **Testability**: Domain isolation for reliable unit tests
- **Maintainability**: Code organized according to DDD principles
- **Extensibility**: Easy addition of new features
- **Dependency inversion**: Domain doesn't depend on implementations
### 2. Domain Processing (Domain Layer)
---

*This document reflects the current state of the hexagonal DDD architecture implemented in September 2025.*
- ✅ **Technological independence** - Domain decoupled from infrastructure

### DDD Layered Architecture
```
🏛️ Domain
├── Post entity (core business logic)
├── DateRange value object (temporal rules)
├── PostRepository interface (abstract contract)
└── PostService (domain services)

🚀 Application (Orchestration)
├── Use Cases (LoadVeilleDataUseCase)
├── DTOs (PostDTO, VeilleResultDTO)
└── Application Services (VeilleService)

🔧 Infrastructure (Technical)
├── Crawlers (17 external sources)
├── Repositories (JSON, future: DB)
├── Adapters (HTTP, Parsing, etc.)
└── Factories (Dependency injection)

🎨 Presentation (Interfaces)
├── CLI (modern console)
├── GUI (existing CustomTkinter)
└── Web (future: FastAPI/Flask)
```

### Automatic Save System
**Implementation**: Multi-format save service
- ✅ **SaveService** - Automatic JSON, CSV, HTML saving
- ✅ **saves/** folder - Organized timestamped exports
- ✅ **GUI integration** - Transparent saving after each watch session

### Centralized Logging Architecture
**Problem solved**: Scattered logs and uncaptured errors
- ✅ **logs/** folder - Centralization of all log files
- ✅ **Multi-level logging** - gui_main.log, gui_events.log, console.log
- ✅ **Global exception capture** - sys.excepthook + Tkinter callbacks
- ✅ **Complete traceability** - Stack traces with exc_info=True

### Desktop Notification System
**Stack**: Plyer (compatible with Python 3.13)
- ✅ **Native notifications** - Linux system integration
- ✅ **New article detection** - Hash-based change detection
- ✅ **User feedback** - Hourly notifications

### System Service Automation
**Implementation**: Dual systemd services
- ✅ **Console service** - Automatic background watch (hourly)
- ✅ **User service** - Automatic GUI launch with session
- ✅ **Menu icon** - Ubuntu desktop integration (.desktop file)
- ✅ **Installation scripts** - Automated install.sh + uninstall.sh

### Optimized Multi-Thread Architecture
**Improvement**: Efficient thread-safe communication
- ✅ **SavingGuiRenderer** - Dual-purpose renderer (display + saving)
- ✅ **Non-blocking queue** - Separate messages for UI and persistence
- ✅ **Periodic thread** - Automatic watch without blocking interface
- ✅ **Robust state management** - State-driven buttons + automatic cleanup

## 🔧 Development Tools

### Python 3.13 Virtual Environment
```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Dependencies Management
- **requests** - HTTP client for crawling
- **beautifulsoup4** - HTML parsing
- **customtkinter** - Modern graphical interface
- **plyer** - Cross-platform desktop notifications

### Deployment Structure
```
scripts/               # Launch scripts
├── start_veille.sh      # Graphical interface
└── start_veille_console.sh # Console version

config/                # Service configuration
├── veille.service       # System service
└── veille-user.service  # User service

assets/                # Resources
└── veille-tech.desktop  # Application file

var/                   # Runtime data
├── logs/                # Centralized logs
│   ├── gui_main.log         # Main interface logs
│   ├── gui_events.log       # Interface events
│   └── veille_service.log   # Console DDD logs
└── saves/               # Automatic saves
    ├── *.json              # Structured format
    ├── *.csv               # Spreadsheet format
    └── *.html              # Web format
```

## 📊 Performance Metrics

### Execution Frequency
- **Automatic watch**: Every hour (system service)
- **Manual launch**: On demand via interface
- **Saving**: After each watch session
- **Notifications**: Only if new articles detected

## 🛠️ Maintenance Process

### Adding New Sources (DDD Architecture)
1. **Infrastructure Layer**: Create crawler in `src/infrastructure/external/crawlers/[source].py`
2. **Inherit**: `BaseCrawler` with implementation of `fetch_posts_in_range()`
3. **Factory**: Add method in `CrawlerFactory`
4. **Tests**: Create unit tests for the new crawler
5. **Presentation**: Update interface (ComboBox sources)

### DDD Test Architecture
```
tests/
├── unit/              # Unit tests per layer
│   ├── domain/        # Entity, value object, service tests
│   ├── application/   # Use case, DTO tests
│   └── infrastructure/ # Crawler, repository tests
├── integration/       # Inter-layer integration tests
└── acceptance/        # End-to-end functional tests
```

### Debugging and Monitoring
- **Real-time logs**: `tail -f var/logs/veille_service.log`
- **Error search**: `grep -i error var/logs/*.log`
- **Service status**: `systemctl status veille.service`
- **Save verification**: Check contents of `var/saves/`

### DDD Best Practices
- **Domain first**: Start with entities and business rules
- **Pure functions**: Domain services without side effects
- **Interface segregation**: Specific contracts per responsibility
- **Dependency injection**: Inversion of control for testability
- **Ubiquitous language**: Shared business vocabulary in code

# 🧠 AI Agent Development Guidance

## Project Architecture
- Hexagonal (clean) architecture: domain, application, infrastructure, presentation layers
- Dependency injection for repositories/services
- Unified data source: all articles in `var/saves/veille_db.json`
- Modern GUI (CustomTkinter), CLI, and service modes

## Best Practices
- Always document changes and encountered issues in English
- Update documentation in sync with code changes
- Validate all code changes with error checking tools
- Use realistic data for tests
- Never delete or modify existing issues in experience feedback files

## Feature Development Steps
1. Identify the relevant layer for your feature
2. Use dependency injection for new services/repositories
3. Add unit/integration tests
4. Document the feature and any encountered issues
5. Prefer maintainable, extensible code (type hints, docstrings)

## Extensibility
- Add new crawlers via adapter pattern (see CRAWLER_ADDITION_GUIDE.md)
- Use robust HTML parsing and date handling
- GUI: use radio buttons/combo boxes for filters, log user actions

## Known Issues & Solutions
- See `ENCOUNTERED_ISSUES.md` for technical problems and lessons learned

---

