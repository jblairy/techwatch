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
python techwatch_service.py --verbose
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
- **Launch**: `python techwatch_service.py`
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
├── Use Cases (LoadDataUseCase)
├── DTOs (PostDTO, ResultDTO)
└── Application Services (TechwatchService)

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
├── install.sh      # Install script
└── start_techwatch_gui.sh # Script that run GUI
└── uninstall.sh # Uninstall script

assets/                # Resources
└── techwatch.desktop  # Application file

var/                   # Runtime data
├── logs/                # Centralized logs
│   ├── gui_main.log         # Main interface logs
│   ├── gui_events.log       # Interface events
│   └── techwatch_service.log   # Console DDD logs
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
- **Real-time logs**: `tail -f var/logs/techwatch_service.log`
- **Error search**: `grep -i error var/logs/*.log`
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
- Unified data source: all articles in `var/saves/techwatch_db.json`
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

# Wayland and X11 Compatibility Issues (GUI Docker)

## Context
The Techwatch GUI is launched in a Docker container and relies on X11 for graphical display. Modern Linux systems may use either X11 (Xorg) or Wayland as their display server protocol.

## Problem Description
### X11 (Xorg)
- The GUI container accesses the host's X11 server via the DISPLAY variable and the /tmp/.X11-unix socket.
- This setup works natively on X11 systems, allowing graphical applications in Docker to display windows on the host.

### Wayland
- Wayland is a newer protocol, replacing X11 in many distributions (e.g., GNOME, KDE).
- Applications expecting X11 must use XWayland, a compatibility layer that emulates X11 on top of Wayland.
- When launching via a .desktop file, environment variables (DISPLAY, XAUTHORITY, DBUS_SESSION_BUS_ADDRESS, etc.) may not be correctly inherited, causing the GUI to fail to display or notifications to not appear.
- Wayland increases isolation for security, which can block Docker containers from accessing the graphical session or DBUS notifications.

## Symptoms
- GUI does not appear when launched via .desktop, but works from a terminal.
- notify-send notifications do not show up via .desktop, but work in a terminal.
- Environment variables are not expanded or are missing in the .desktop context.

## Solution
- Use a .desktop Exec line that launches the script via bash -c, ensuring all environment variables are expanded and inherited from the user session:
  ```
  Exec=bash -c 'TECHWATCH_PROJECT_DIR="$HOME/techwatch" XAUTHORITY="$XAUTHORITY" WAYLAND_DISPLAY="$WAYLAND_DISPLAY" DISPLAY="$DISPLAY" DBUS_SESSION_BUS_ADDRESS="$DBUS_SESSION_BUS_ADDRESS" $HOME/techwatch/scripts/start_techwatch_gui.sh'
  ```
- This ensures the Docker container receives the correct graphical and DBUS context, making the GUI and notifications work under both X11 and Wayland (with XWayland).

## References
- https://wayland.freedesktop.org/
- https://wiki.archlinux.org/title/Wayland
- https://linuxfr.org/news/wayland-le-remplacant-de-xorg

---

*This section documents the compatibility issues and solutions for running the Techwatch GUI Docker container under X11 and Wayland environments. Last updated: September 2025.*

## Cron Job Architecture & Auto-Update Feature

### Concept
Techwatch can be configured to automatically update its database via a Docker cron job. The cron job does not launch the GUI, but runs the `techwatch_service.py` service at regular intervals to ensure continuous technology monitoring.

### How it works
- The install script accepts the `--autoupdate <minutes>` flag to enable periodic updates.
- If this flag is provided, a cron job is created in `/etc/cron.d/techwatch-gui` to run the database update every N minutes:
  ```
  cd $HOME/techwatch && docker run --rm --name techwatch-service -v $HOME/techwatch:/app techwatch-gui python techwatch_service.py
  ```
- The uninstall script automatically removes this cron job.

- Il fonctionne en arrière-plan et n'affiche pas d'interface utilisateur.
- Aucun cron job n'est installé si le flag est omis.
- Le cron job est robuste et automatiquement supprimé lors de la désinstallation.

---

