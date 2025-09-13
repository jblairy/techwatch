#!/bin/bash
# Uninstall script for Techwatch application (user level only)
set -e

# 1. Stop and remove Docker container
if docker ps -a --format '{{.Names}}' | grep -w techwatch-gui-app &> /dev/null; then
    echo "Removing Docker container techwatch-gui-app..."
    docker rm -f techwatch-gui-app || true
fi

# 2. Remove Docker image
if docker image inspect techwatch-gui &> /dev/null; then
    echo "Removing Docker image techwatch-gui..."
    docker rmi techwatch-gui || true
fi

# 3. Remove desktop integration at user level
DESKTOP_TARGET="$HOME/.local/share/applications"
ICON_TARGET="$HOME/.local/share/icons"
BIN_TARGET="$HOME/.local/bin"

if [ -f "$DESKTOP_TARGET/techwatch.desktop" ]; then
    echo "Removing desktop shortcut..."
    rm -f "$DESKTOP_TARGET/techwatch.desktop"
fi
if [ -f "$ICON_TARGET/techwatch.png" ]; then
    echo "Removing icon..."
    rm -f "$ICON_TARGET/techwatch.png"
fi
if [ -f "$BIN_TARGET/start_techwatch_gui.sh" ]; then
    echo "Removing launcher script..."
    rm -f "$BIN_TARGET/start_techwatch_gui.sh"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$DESKTOP_TARGET"
fi

# 4. Optionally remove logs and saves (if in project folder)
if [ -d "var/logs" ]; then
    echo "Removing logs..."
    sudo rm -rf var/logs
fi
if [ -d "var/saves" ]; then
    echo "Removing saves..."
    sudo rm -rf var/saves
fi

# --- Remove Techwatch crontab entry ---
CRON_MARKER="# TECHWATCH_CRON"
(crontab -l 2>/dev/null | grep -v "$CRON_MARKER") | crontab -
echo "Techwatch crontab entry removed."

# --- Remove cron job from /etc/cron.d ---
CRON_FILE="/etc/cron.d/techwatch-gui"
if [ -f "$CRON_FILE" ]; then
    sudo rm -f "$CRON_FILE"
    echo "Cron job /etc/cron.d/techwatch-gui removed."
fi

echo "Techwatch application uninstallation complete."
