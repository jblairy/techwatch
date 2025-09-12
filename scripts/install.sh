#!/bin/bash
# Automatic installation script for the technology watch tool
set -e

echo "🚀 Installing technology watch tool..."

# Check for Python 3.13 presence
if ! command -v python3.13 &> /dev/null; then
    echo "❌ Python 3.13 is not installed. Please install it before continuing."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3.13 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Make scripts executable
echo "🔧 Configuring scripts..."
chmod +x scripts/start_veille.sh
chmod +x scripts/start_veille_console.sh
chmod +x assets/veille-tech.desktop

# Create save directory
mkdir -p var/saves

# Install desktop file for graphical interface
echo "🖥 Installing application menu icon..."
mkdir -p ~/.local/share/applications
cp assets/veille-tech.desktop ~/.local/share/applications/

# Replace placeholders in .desktop and .service files with current install path
INSTALL_DIR="$PWD"
INSTALL_USER="$(whoami)"

# Prepare veille-tech.desktop
sed "s|{INSTALL_DIR}|$INSTALL_DIR|g" assets/veille-tech.desktop > ~/.local/share/applications/veille-tech.desktop
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

# Prepare veille.service
sudo sed "s|{INSTALL_DIR}|$INSTALL_DIR|g; s|{INSTALL_USER}|$INSTALL_USER|g" config/veille.service | sudo tee /etc/systemd/system/veille.service > /dev/null
sudo systemctl daemon-reload
sudo systemctl enable veille.service

# Install user service (GUI)
echo "🎨 Installing user service (GUI)..."
mkdir -p ~/.config/systemd/user
cp config/veille-user.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable veille-user.service

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "📋 Available options:"
echo "1. Manual GUI: source .venv/bin/activate && python gui_main.py"
echo "2. Automatic console service: sudo systemctl start veille.service"
echo "3. Automatic GUI service: systemctl --user start veille-user.service"
echo "4. Application menu icon: Search for 'Technology Watch'"
echo ""
echo "📊 Service status:"
echo "Console: $(sudo systemctl is-enabled veille.service 2>/dev/null || echo 'not configured')"
echo "GUI     : $(systemctl --user is-enabled veille-user.service 2>/dev/null || echo 'not configured')"
echo ""
echo "📁 Installed structure:"
echo "  scripts/     - Launch scripts"
echo "  config/      - Systemd service files"
echo "  assets/      - Icons and desktop files"
echo "  var/saves/   - Automatic backups"
