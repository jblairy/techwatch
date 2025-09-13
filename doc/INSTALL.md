# 🚀 Installation Guide - Hexagonal DDD Architecture

> **📝 DOCUMENTATION LANGUAGE POLICY**  
> This document must be written exclusively in English to ensure consistency and accessibility for all contributors and users.

This guide explains how to install and launch the technology watch tool with its new hexagonal DDD architecture on Linux.

## 📋 Prerequisites

- **Linux System** (Ubuntu 20.04+, Debian 11+, or equivalent)
- **Docker** (required for installation)
- **Git** to clone the repository

## 🔧 Installation (Docker Only)

The installation is fully automated and uses Docker for all dependencies and environment isolation. Manual installation is not supported.

```bash
# Clone the repository
git clone <repository-url>
cd techwatch

# Launch automatic installation
chmod +x scripts/install.sh
./scripts/install.sh
```

### What the installation script does:
- ✅ **Builds the Docker image** and launches the GUI in a container
- ✅ **Installs the launcher script** in `~/.local/bin/start_techwatch_gui.sh` (added to PATH if needed)
- ✅ **Installs the icon** in `~/.local/share/icons/techwatch.png`
- ✅ **Installs the desktop shortcut** in `~/.local/share/applications/techwatch.desktop`
- ✅ **Updates the desktop application database**
- ✅ **Creates `var/saves/` and `var/logs/` directories** for data and logs
- ✅ **No system-wide files are modified. All changes are limited to the current user.**

## 🚀 Application Entry Points

The hexagonal DDD architecture offers several entry points according to your needs:

### 1. Modern Graphical Interface (Recommended)
```bash
# Launch via desktop shortcut (Techwatch in your menu)
# Or directly:
start_techwatch_gui.sh
```
**Features:**
- 🎨 Modern design with dark theme
- 📊 Technology watch metadata visualization
- 🔄 Integrated "Generate new data" button
- 📱 Responsive interface with dynamic columns

### 2. Command Line Interface
```bash
python main.py show                    # Show latest data
python main.py show --days 7           # Filter by period
python main.py show --source <source_name>   # Filter by source
python main.py analyze                 # Analyze data
```

### 3. Console Service (Crawling)
```bash
python techwatch_service.py --days 7               # Crawl 7 days
python techwatch_service.py --sources <source_name>      # Specific source
```

## 🔧 System Configuration (Optional)

### Desktop Integration
```bash
cp assets/techwatch.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

## 🧪 Architecture Testing

### Domain Layer Tests
```bash
python -m unittest tests.unit.domain.test_post_entity
python -m unittest tests.unit.domain.test_date_range
python -m unittest tests.unit.domain.test_post_service
```

### Application Layer Tests
```bash
python -m unittest tests.unit.application.test_use_cases
python -m unittest tests.unit.application.test_post_dto
```

### Infrastructure Layer Tests
```bash
python -m unittest tests.unit.infrastructure.test_crawlers
python -m unittest tests.integration.test_json_repository
```

### Complete Integration Tests
```bash
python -m unittest tests.integration.test_ddd_integration
python tests/run_tests.py
```

## 📊 Performance Verification

### Memory and Performance
```bash
python -c "import psutil, sys; print(f'Python version: {sys.version}'); print(f'Available memory: {psutil.virtual_memory().total // 1024**3} GB'); print(f'CPU cores: {psutil.cpu_count()}')"
time python main.py show --days 1 --source <source_name>
```

### Data Generation Test
```bash
python main.py show --days 1 --verbose
ls -la var/saves/
cat var/logs/techwatch_service.log | tail -20
```

## 🔍 Troubleshooting

### Common Issues

**Import Error: Module not found**
```bash
which python
pip list | grep customtkinter
pip install -r requirements.txt --force-reinstall
```

**Permission Error**
```bash
chmod +x scripts/*.sh
chmod +x assets/techwatch.desktop
chmod 755 var/saves var/logs
```

**Network Connection Issues**
```bash
python -c "import requests; response = requests.get('<source_url>'); print(f'Status: {response.status_code}')"
```

### Log Analysis
```bash
tail -f var/logs/techwatch_service.log
tail -f var/logs/gui_main.log
```

## 🚀 Quick Start

### First Use (5 minutes)
```bash
./scripts/install.sh
start_techwatch_gui.sh
python main.py show
```

### Daily Usage
```bash
python main.py show --days 1
python main.py show --source <source_name> --days 3
start_techwatch_gui.sh
```

## 📈 Architecture Benefits

### Hexagonal DDD
- **Domain isolation**: Pure business logic without technical dependencies
- **Testability**: Unit tests for each layer independently
- **Flexibility**: Easy replacement of technical adapters
- **Maintainability**: Clear separation of responsibilities

### Multiple Interfaces
- **GUI**: For daily consultation and visualization
- **CLI**: For automation and scripting
- **Service**: For background monitoring

### Robustness
- **Error handling**: Graceful degradation for failed sources
- **Logging**: Complete traceability of operations
- **Validation**: Architecture verification at each launch

## Automated Periodic Update (Cron)

Techwatch supports automated periodic database updates via Docker using a cron job. This is managed by the install and uninstall scripts.

### How it works
- The install script accepts a flag `--autoupdate <minutes>` to enable periodic database updates.
- If provided, a cron job is created in `/etc/cron.d/techwatch-gui` to launch the update every N minutes (using `techwatch_service.py`).
- The uninstall script removes this cron job automatically.

### Example commands
- Install with auto-update every 5 minutes:
  ```
  bash scripts/install.sh --autoupdate 5
  ```
  or
  ```
  make install.autoupdate MINUTES=5
  ```
- Uninstall and remove the cron job:
  ```
  bash scripts/uninstall.sh
  ```
  or
  ```
  make uninstall
  ```

### Details
- The cron job does not require any graphical environment (no DISPLAY/X11/Wayland).
- It simply runs the database update via:
  ```
  cd $HOME/techwatch && docker run --rm --name techwatch-service -v $HOME/techwatch:/app techwatch-gui python techwatch_service.py
  ```
- No cron job is installed if the option is not used.
- The cron job is robust and automatically removed during uninstallation.

## 🧹 Uninstallation

To completely remove the application and all user-level integrations, run:

```bash
bash scripts/uninstall.sh
```

This will:
- Stop and remove the Docker container and image
- Remove the desktop shortcut from `~/.local/share/applications/techwatch.desktop`
- Remove the icon from `~/.local/share/icons/techwatch.png`
- Remove the launcher script from `~/.local/bin/start_techwatch_gui.sh`
- Optionally remove logs and saves from `var/logs` and `var/saves` in the project folder
- Optionally remove the local Python virtual environment `.venv`

No system-wide files are affected. All changes are limited to the current user.

---

*Installation guide updated for hexagonal DDD architecture - September 2025*
