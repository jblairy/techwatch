# ⚠️ Experimental Project Notice

> **This project is currently experimental.**
> Features and architecture may change at any time. Use with caution.

# 🔍 Technology Watch Tool

Modern technology watch tool respecting Hexagonal Architecture and Domain Driven Design (DDD) principles to track news from various technical sources.

## 🏗️ Architecture

The project uses **Hexagonal Architecture DDD** for clear separation of responsibilities:
Cornhusk-Unmixable-Smooth-Motto-Sandfish-Repaying7
```
src/
├── domain/                    # 💎 Business core - Pure logic
│   ├── entities/             # Business entities (Post)
│   ├── value_objects/        # Value objects (DateRange, Source)
│   ├── repositories/         # Repository interfaces
│   └── services/            # Domain services
├── application/              # 🎯 Orchestration and use cases
│   ├── use_cases/           # LoadWatch, SaveWatch, AnalyzeWatch
│   ├── dto/                 # Data transfer objects
│   └── services/            # Application services
├── infrastructure/          # 🔧 Technical implementations
│   ├── repositories/        # JSON persistence
│   ├── adapters/           # HTTP, HTML parsing, etc.
│   ├── factories/          # Instance creation
│   ├── services/           # Technical services
│   └── external/           # External crawlers
└── presentation/           # 🖥️ User interfaces
    ├── cli/               # Command line interface
    ├── gui/              # Graphical interface (CustomTkinter)
    └── web/              # Web interface (coming soon)
```

## 🚀 Features

- **🗓️ Flexible date ranges**: Multi-day search with immutable value objects
- **🏛️ Hexagonal Architecture DDD**: Clear separation domain/application/infrastructure
- **📊 Multiple sources**: Support for 17 PHP/Symfony technical sources
- **🎯 Advanced filtering**: By source, date, with domain services
- **🔍 Fallback verification**: Automatic detection of parsing issues
- **💾 JSON persistence**: Save only in structured JSON format with metadata
- **🖥️ Multiple interfaces**: Modern CLI and CustomTkinter GUI
- **🧪 Complete tests**: Coverage of all architecture layers
- **📝 Detailed logging**: Multi-level tracking with different formats

## 📦 Installation

```bash
# Clone the repository
git clone <repository-url>
cd techwatch

# Use the automatic installation script (Docker required)
chmod +x scripts/install.sh
./scripts/install.sh
```

**The installation script will:**
- Build the Docker image and launch the GUI in a container
- Install the launcher script in `~/.local/bin/start_techwatch_gui.sh` (added to PATH if needed)
- Install the icon in `~/.local/share/icons/techwatch.png`
- Install the desktop shortcut in `~/.local/share/applications/techwatch.desktop` (with automatic detection of the project directory)
- Update the desktop application database

**Manual installation is not supported. No system-wide files are modified. All changes are limited to the current user.**

## 🎯 Usage

### Modern Graphical Interface (Recommended)
```bash
# Launch the GUI via the desktop shortcut (Techwatch in your menu)
# Or directly (with project directory detection):
TECHWATCH_PROJECT_DIR=$HOME/techwatch start_techwatch_gui.sh
```

**Note:** The desktop shortcut automatically sets the TECHWATCH_PROJECT_DIR environment variable to your project folder. If you move your techwatch folder, update the shortcut accordingly or launch the script with the correct TECHWATCH_PROJECT_DIR value.

### Command Line Interface
```bash
# Show latest data
python main.py show
# Filter by period
python main.py show --days 7
# Filter by source
python main.py show --source <source_name>
# Analyze data
python main.py analyze
```

### Console Service (Crawling)
```bash
# Crawl and generate JSON files
python techwatch_service.py --days 7               # Crawl 7 days
python techwatch_service.py --sources <source_name>      # Specific source
```

## Automated Periodic Update (Cron)

Techwatch can be configured to automatically update its database at regular intervals using a Docker cron job. This feature is managed by the install script and the Makefile.

### Usage
- To install automatic updates every N minutes:
  ```
  make install.autoupdate MINUTES=5
  ```
  or
  ```
  bash scripts/install.sh --autoupdate 5
  ```
- This creates a cron job in `/etc/cron.d/techwatch-gui` that runs the database update via the `techwatch_service.py` service every N minutes.
- To uninstall and remove the cron job:
  ```
  make uninstall
  ```
  or
  ```
  bash scripts/uninstall.sh
  ```

### Notes
- If the `--autoupdate` option is not provided, no cron job is installed.
- The cron job does not require any graphical environment (no DISPLAY/X11/Wayland).
- It runs in the background and ensures automated technology monitoring.
- The frequency is fully configurable via the MINUTES variable or the flag value.
- The cron job is robust and automatically removed during uninstallation.

## 💾 Save System

The system uses **exclusively JSON format** for data persistence:

- **Single format**: Save only in structured JSON
- **Complete metadata**: Session information, sources, dates
- **Space optimization**: No more format duplicates
- **Improved performance**: Fewer write operations
- **File structure**:
  ```json
  {
    "metadata": {
      "generated_at": "2025-09-08T10:13:01",
      "total_articles": 42,
      "sources": ["Korben Blog"],
      "format_version": "2.0",
      "date_range": {...}
    },
    "articles": [...]
  }
  ```

## 🏛️ Applied DDD Principles

### Domain (Domain Layer)
- **Entities**: `Post` with business logic (equality, validation)
- **Value Objects**: Immutable `DateRange` with business methods
- **Domain services**: `PostFilteringService`, `PostAnalysisService`
- **Repositories**: Abstract interfaces defining contracts

### Application (Application Layer)
- **Use cases**: `LoadWatchDataUseCase`, `SaveWatchDataUseCase`, `AnalyzeWatchDataUseCase`
- **DTOs**: `PostDTO`, `WatchResultDTO` for data transfers
- **Application services**: Business logic orchestration

### Infrastructure (Infrastructure Layer)
- **Concrete repositories**: `JsonPostRepository` for persistence
- **Adapters**: `RequestsHttpClient`, `BeautifulSoupParser`
- **Technical services**: `SaveService` (JSON only)
- **Factories**: `CrawlerFactory` for dependency injection

### Presentation (Presentation Layer)
- **CLI**: `WatchCLI` with structured commands
- **GUI**: Modern and clean graphical interface
- **Renderers**: `ConsoleRenderer` for display

## 🧪 Tests

```bash
# Run all hexagonal architecture tests
python -m pytest tests/ -v

# Or with unittest
python -m unittest tests.test_techwatch -v

# Layer-specific tests
python -m unittest tests.test_techwatch.TestPost -v              # Domain
python -m unittest tests.test_techwatch.TestLoadWatchDataUseCase -v  # Application
python -m unittest tests.test_techwatch.TestJsonPostRepository -v     # Infrastructure
```

---

## 📁 File Structure

```
var/
├── logs/                    # Logging files
│   ├── gui_main.log        # GUI logs
│   └── techwatch_service.log  # Crawling service logs
└── saves/                  # JSON saves only
    └── techwatch_db.json
```

## 🔄 Recent Developments

- **September 2025**: Save system simplification (JSON only)
- **Clean interface**: Removal of redundant features
- **Optimization**: Performance and disk space improvements
- **Hexagonal architecture**: Complete DDD migration

## 🤝 Contribution

To contribute to the project:

1. Respect hexagonal architecture DDD
2. Maintain test coverage
3. Document new features
4. Follow naming conventions

## ���� License

This project is under MIT license.

---

## 🐳 Docker & Automated Installation

You can use the automated installation script to build and launch the application in a Docker container, and install desktop/user integrations:

```bash
bash scripts/install.sh
```

### Force Docker Image Rebuild

If you want to force a rebuild of the Docker image (for example, after updating the code or dependencies), use the `--rebuild` or `-r` flag:

```bash
bash scripts/install.sh --rebuild
```

This will rebuild the `techwatch-gui` Docker image even if it already exists, ensuring your changes are included.

- The script will also install the desktop shortcut and user integrations automatically.
- The GUI will be launched in a container and should appear on your desktop if X11 is configured.

**Note:** If you encounter display issues, make sure your X11 permissions are set and Docker is running with access to your display.

---

**Hexagonal Architecture DDD - Clear separation of responsibilities for optimal maintenance** 🏗️
