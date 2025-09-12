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
cd veille

# Install dependencies
pip install -r requirements.txt

# Or use the automatic installation script
chmod +x scripts/install.sh
./scripts/install.sh
```

## 🎯 Usage

### Modern Graphical Interface (Recommended)
```bash
# Launch the CustomTkinter GUI
python gui_main.py
```

**Modern interface features:**
- 🎨 **Modern design**: Dark theme with CustomTkinter
- 📊 **Advanced visualization**: Tabs, filters, metadata
- 🔄 **Forced generation**: Button to force new data creation
- 📱 **Responsive design**: Adaptive interface with dynamic columns
- 🔗 **Interactive links**: Direct article opening in browser
- ⚡ **Real-time**: Automatic loading and refresh
- 🗂️ **Clean interface**: Simplified design focused on essentials

### Command Line Interface (Hexagonal Architecture)
```bash
# New DDD entry point
python main_hexagonal.py list                    # List saves
python main_hexagonal.py show                    # Show latest data
python main_hexagonal.py show --days-back 7      # Filter by period
python main_hexagonal.py show --source <source_name>   # Filter by source
python main_hexagonal.py analyze                 # Analyze data
```

### Console Service (Crawling)
```bash
# Crawling service (generates JSON files)
python veille_service.py --days 7               # Crawl 7 days
python veille_service.py --sources <source_name>      # Specific source
python veille_service.py --continuous           # Continuous mode (systemd)
python veille_service.py --silent               # Silent mode
```

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
python -m unittest tests.test_veille -v

# Layer-specific tests
python -m unittest tests.test_veille.TestPost -v              # Domain
python -m unittest tests.test_veille.TestLoadWatchDataUseCase -v  # Application
python -m unittest tests.test_veille.TestJsonPostRepository -v     # Infrastructure
```

---

## 📁 File Structure

```
var/
├── logs/                    # Logging files
│   ├── gui_main.log        # GUI logs
│   └── veille_service.log  # Crawling service logs
└── saves/                  # JSON saves only
    ├── veille_20250908_084702.json
    ├── veille_20250908_094948.json
    └── ...
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

## 📄 License

This project is under MIT license.

---

**Hexagonal Architecture DDD - Clear separation of responsibilities for optimal maintenance** 🏗️
