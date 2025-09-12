#!/bin/bash
# Uninstallation script for the technology watch tool
set -e

echo "🗑️ Uninstalling technology watch tool..."

# Stop and disable services
echo "⏹️ Stopping services..."
sudo systemctl stop veille.service 2>/dev/null || true
sudo systemctl disable veille.service 2>/dev/null || true
systemctl --user stop veille-user.service 2>/dev/null || true
systemctl --user disable veille-user.service 2>/dev/null || true

# Remove system service files
echo "🗂️ Removing service files..."
sudo rm -f /etc/systemd/system/veille.service
rm -f ~/.config/systemd/user/veille-user.service //TODO deprecated ?
sudo systemctl daemon-reload 2>/dev/null || true
systemctl --user daemon-reload 2>/dev/null || true

# Remove desktop application
echo "🖥️ Removing application menu icon..."
rm -f ~/.local/share/applications/veille-tech.desktop
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

# Remove virtual environment
echo "🗂️ Removing virtual environment..."
rm -rf .venv

# Remove generated data (optional - ask user)
read -p "Remove saved data and logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️ Removing data and logs..."
    rm -rf var/saves
    rm -rf var/logs
fi

echo ""
echo "✅ Uninstallation completed!"
echo ""
echo "📋 What was removed:"
echo "  ✅ Virtual environment and dependencies"
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  ✅ Data and configuration files (as requested)"
fi

