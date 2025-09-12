# 🚀 Installation Guide - Hexagonal DDD Architecture

> **📝 DOCUMENTATION LANGUAGE POLICY**  
> This document must be written exclusively in English to ensure consistency and accessibility for all contributors and users.

This guide explains how to install and launch the technology watch tool with its new hexagonal DDD architecture on Linux.

## 📋 Prerequisites

- **Python 3.10+** (tested with Python 3.13)
- **pip** and **venv** installed
- **Git** to clone the repository
- **Linux System** (Ubuntu 20.04+, Debian 11+, or equivalent)

## 🔧 Automated Installation (Recommended)

The installation script automates the entire process:

```bash
# Clone the repository
git clone <repository-url>
cd veille

# Launch automatic installation
chmod +x scripts/install.sh
./scripts/install.sh
```

### What the installation script does:
- ✅ **Virtual environment** Python 3.13 with dependency isolation
- ✅ **Dependencies** Installation of all required libraries
- ✅ **DDD Structure** Creation of `var/saves/` and `var/logs/` directories
- ✅ **Launch scripts** Configuration for CLI and GUI
- ✅ **Systemd services** Configuration for automatic mode
- ✅ **Desktop icon** Integration into applications menu
- ✅ **Validation** Tests of hexagonal architecture

## 🛠️ Manual Installation

### Step 1: Python Environment
```bash
# Check Python version
python3 --version  # Must be 3.10+

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # ⚠️ Use 'source', not direct execution
```

### Step 2: Dependencies Installation
```bash
# Update pip
pip install --upgrade pip

# Install DDD architecture dependencies
pip install -r requirements.txt
```

### Step 3: Data Structure (DDD Architecture)
```bash
# Create data structure according to hexagonal architecture
mkdir -p var/saves      # JSON persistence (Infrastructure Layer)
mkdir -p var/logs       # Application logs
mkdir -p config         # Crawler configuration (Infrastructure)

# Script permissions
chmod +x scripts/*.sh
chmod +x assets/veille-tech.desktop
```

### Step 4: Installation Validation
```bash
# Test hexagonal architecture imports
python -c "
from src.domain.entities.post import Post
from src.application.use_cases.veille_use_cases import LoadVeilleDataUseCase
from src.infrastructure.repositories.json_post_repository import JsonPostRepository
print('✅ Hexagonal DDD architecture validated')
"

# Test unit tests
python -m unittest tests.test_veille.TestPost -v
```

## 🚀 Application Entry Points

The hexagonal DDD architecture offers several entry points according to your needs:

### 1. Modern Graphical Interface (Recommended)
```bash
# Launch CustomTkinter GUI with DDD architecture
python gui_main.py
```
**Features:**
- 🎨 Modern design with dark theme
- 📊 Technology watch metadata visualization
- 🔄 Integrated "Generate new data" button
- 📱 Responsive interface with dynamic columns

### 2. Hexagonal CLI Interface (New)
```bash
# New entry point respecting DDD architecture
python main.py generate --days 7
python main.py show --source <source_name>
python main.py list-sources
```
**Commands:**
- `generate`: Generate new technology watch data
- `show`: Display saved data with filtering
- `list-sources`: List all available sources

### 3. Service Mode (Background)
```bash
# Background service for automation
python veille_service.py --interval 3600 --verbose
```
**Features:**
- 🔄 Automatic execution every hour
- 📝 Detailed logging in `var/logs/`
- 🛡️ Error management and recovery
- 📊 Generation statistics

## 🔧 System Configuration

### Systemd Service (Linux)
```bash
# Copy service configuration
sudo cp config/veille.service /etc/systemd/system/
sudo systemctl daemon-reload

# Enable and start service
sudo systemctl enable veille.service
sudo systemctl start veille.service

# Check status
sudo systemctl status veille.service
```

### Desktop Integration
```bash
# Install desktop icon
cp assets/veille-tech.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

## 🧪 Architecture Testing

### Domain Layer Tests
```bash
# Test business entities
python -m unittest tests.unit.domain.test_post_entity
python -m unittest tests.unit.domain.test_date_range

# Test domain services
python -m unittest tests.unit.domain.test_post_service
```

### Application Layer Tests
```bash
# Test use cases
python -m unittest tests.unit.application.test_veille_use_cases

# Test DTOs
python -m unittest tests.unit.application.test_post_dto
```

### Infrastructure Layer Tests
```bash
# Test crawlers
python -m unittest tests.unit.infrastructure.test_crawlers

# Test repositories
python -m unittest tests.integration.test_json_repository
```

### Complete Integration Tests
```bash
# Full DDD architecture test
python -m unittest tests.integration.test_ddd_integration

# End-to-end functional tests
python tests/run_tests.py
```

## 📊 Performance Verification

### Memory and Performance
```bash
# Monitor resource usage
python -c "
import psutil
import sys
print(f'Python version: {sys.version}')
print(f'Available memory: {psutil.virtual_memory().total // 1024**3} GB')
print(f'CPU cores: {psutil.cpu_count()}')
"

# Performance benchmark
time python main.py generate --days 1 --source <source_name>
```

### Data Generation Test
```bash
# Quick generation test
python main.py generate --days 1 --verbose

# Check generated files
ls -la var/saves/
cat var/logs/veille_service.log | tail -20
```

## 🔍 Troubleshooting

### Common Issues

**Import Error: Module not found**
```bash
# Verify virtual environment activation
which python
pip list | grep customtkinter

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Permission Error**
```bash
# Fix script permissions
chmod +x scripts/*.sh
chmod +x assets/veille-tech.desktop

# Fix directory permissions
chmod 755 var/saves var/logs
```

**Network Connection Issues**
```bash
# Test crawler connectivity
python -c "
import requests
response = requests.get('<source_url>')
print(f'Status: {response.status_code}')
"
```

### Log Analysis
```bash
# View application logs
tail -f var/logs/veille_service.log

# View GUI logs
tail -f var/logs/gui_main.log

# Debug mode
python main.py generate --days 1 --verbose --debug
```

## 🚀 Quick Start

### First Use (5 minutes)
```bash
# 1. Complete installation
./scripts/install.sh

# 2. Generate first data
python main.py generate --days 7

# 3. Launch graphical interface
python gui_main.py

# 4. Consult results
python main.py show
```

### Daily Usage
```bash
# Quick update
python main.py generate --days 1

# Specific source consultation
python main.py show --source <source_name> --days 3

# Launch GUI for detailed view
python gui_main.py
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

---

*Installation guide updated for hexagonal DDD architecture - September 2025*
