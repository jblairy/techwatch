#!/bin/bash
# Wrapper to launch the GUI Docker application with X11 from a desktop shortcut

set -e

# Debug: log all relevant environment variables
LOGFILE="$HOME/techwatch/var/logs/gui_startup.log"
mkdir -p "$(dirname "$LOGFILE")"
exec > "$LOGFILE" 2>&1

echo "==== $(date) ===="
echo "User: $(whoami)"
echo "UID: $(id -u)"
echo "GID: $(id -g)"
echo "HOME: $HOME"
echo "PWD: $(pwd)"
echo "DISPLAY: $DISPLAY"
echo "WAYLAND_DISPLAY: $WAYLAND_DISPLAY"
echo "XAUTHORITY: $XAUTHORITY"
echo "DBUS_SESSION_BUS_ADDRESS: $DBUS_SESSION_BUS_ADDRESS"
echo "PATH: $PATH"
echo "Project dir: $TECHWATCH_PROJECT_DIR"
echo "SHELL: $SHELL"

# Test notify-send
if command -v notify-send &> /dev/null; then
    echo "notify-send found, testing notification..."
    notify-send "Techwatch GUI" "Test notification from start_techwatch_gui.sh"
    RET=$?
    echo "notify-send exit code: $RET"
    if [ $RET -ne 0 ]; then
        echo "notify-send failed."
    fi
else
    echo "notify-send not found."
fi

# Detect project directory
if [ -n "$TECHWATCH_PROJECT_DIR" ]; then
    PROJECT_DIR="$TECHWATCH_PROJECT_DIR"
else
    echo "Error: Could not detect the project directory. Please set TECHWATCH_PROJECT_DIR to the root of your techwatch project." >&2
    exit 2
fi

LOGFILE="$PROJECT_DIR/var/logs/gui_startup.log"
mkdir -p "$(dirname "$LOGFILE")"
exec > "$LOGFILE" 2>&1

echo "==== $(date) ===="
echo "User: $(whoami)"
echo "DISPLAY: $DISPLAY"
echo "PATH: $PATH"
echo "Current dir: $(pwd)"
echo "Project dir: $PROJECT_DIR"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed or accessible." >&2
    if command -v zenity &> /dev/null; then
        zenity --error --text="Docker is not installed or accessible."
    fi
    exit 1
fi

# Check DISPLAY
if [ -z "$DISPLAY" ]; then
    export DISPLAY=:0
    echo "DISPLAY was not set, defaulting to :0" >&2
fi

# Allow the container to access X11
xhost +local:docker &> /dev/null

# Build image if missing
if ! docker image inspect techwatch-gui &> /dev/null; then
    echo "Building Docker image techwatch-gui..."
    if command -v notify-send &> /dev/null; then
        notify-send "Techwatch GUI" "Building Docker image techwatch-gui..."
    fi
    docker build -t techwatch-gui "$PROJECT_DIR"
fi

# Remove existing container if needed
if docker ps -a --format '{{.Names}}' | grep -w techwatch-gui-app &> /dev/null; then
    echo "Removing existing container techwatch-gui-app..."
    docker rm -f techwatch-gui-app
fi

# Launch the container in interactive mode
if command -v notify-send &> /dev/null; then
    notify-send "Techwatch GUI" "Launching the GUI application in the Docker container..."
fi
echo "Launching container..."
docker run --rm \
    --name techwatch-gui-app \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v "$PROJECT_DIR:/app" \
    techwatch-gui \
    python gui_main.py

RET=$?
echo "Container exited with code: $RET"
exit $RET
