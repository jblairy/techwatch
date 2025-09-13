#!/bin/bash
# Clean install script for Techwatch desktop app
set -e

# --- Options ---
REBUILD=0
AUTO_UPDATE_MINUTES=""
ARGS=("$@")
for ((i=0; i<$#; i++)); do
    arg="${ARGS[$i]}"
    if [[ "$arg" == "--rebuild" || "$arg" == "-r" ]]; then
        REBUILD=1
    elif [[ "$arg" == "--autoupdate" ]]; then
        next_index=$((i+1))
        if [[ $next_index -lt $# ]]; then
            value="${ARGS[$next_index]}"
            if [[ "$value" =~ ^[1-9][0-9]*$ ]]; then
                AUTO_UPDATE_MINUTES="$value"
            else
                echo "Error: --autoupdate requires a positive integer value (minutes)." >&2
                exit 3
            fi
        else
            echo "Error: --autoupdate flag requires a value (minutes)." >&2
            exit 3
        fi
    fi
    # Add other options here if needed
done

# --- Create all needed directories ---
mkdir -p "$HOME/.local/bin"
mkdir -p "$HOME/.local/share/icons"
mkdir -p "$HOME/.local/share/applications"

# --- Docker image build ---
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install it before continuing."
    exit 1
fi
if [[ $REBUILD -eq 1 ]]; then
    echo "--rebuild option detected: forcing rebuild of Docker image techwatch-gui..."
    docker build --no-cache -t techwatch-gui .
else
    if ! docker image inspect techwatch-gui &> /dev/null; then
        echo "Building Docker image techwatch-gui..."
        docker build -t techwatch-gui .
    else
        echo "Docker image techwatch-gui already present."
    fi
fi

# --- X11 preparation ---
if [ -z "$DISPLAY" ]; then
    echo "The DISPLAY variable is not set. Unable to display the graphical application."
    exit 2
fi
xhost +local:docker &> /dev/null || true

# --- Install resources ---
# Launcher script
cp ./scripts/start_techwatch_gui.sh "$HOME/.local/bin/start_techwatch_gui.sh"
chmod +x "$HOME/.local/bin/start_techwatch_gui.sh"

# Icon
cp ./assets/techwatch.png "$HOME/.local/share/icons/techwatch.png"

# Desktop file
cp ./assets/techwatch.desktop "$HOME/.local/share/applications/techwatch.desktop"
chmod +x "$HOME/.local/share/applications/techwatch.desktop"

# --- Update desktop application database ---
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$HOME/.local/share/applications"
fi

# --- User PATH verification ---
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    echo "export PATH=\"$HOME/.local/bin:$PATH\"" >> "$HOME/.bashrc"
    echo "The ~/.local/bin folder has been added to PATH in ~/.bashrc. Please open a new terminal or restart your session to use it."
fi

# --- Docker container management ---
if docker ps -a --format '{{.Names}}' | grep -w techwatch-gui-app &> /dev/null; then
    echo "A techwatch-gui-app container already exists. Removing..."
    docker rm -f techwatch-gui-app
fi

docker run -d --rm \
    --name techwatch-gui-app \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $PWD:/app \
    techwatch-gui

# --- Remove previous cron jobs ---
CRON_FILE="/etc/cron.d/techwatch-gui"
if [ -f "$CRON_FILE" ]; then
    sudo rm -f "$CRON_FILE"
fi
CRON_MARKER="# TECHWATCH_CRON"
(crontab -l 2>/dev/null | grep -v "$CRON_MARKER") | crontab -
# --- Install cron job in /etc/cron.d for periodic GUI launch ---
if [[ -n "$AUTO_UPDATE_MINUTES" ]]; then
    CRON_FILE="/etc/cron.d/techwatch-gui"
    CRON_MARKER="# TECHWATCH_CRON"
    CRON_CMD="*/$AUTO_UPDATE_MINUTES * * * * $USER DISPLAY=$DISPLAY PROJECT_DIR=$HOME/techwatch docker run --rm --name techwatch-gui-app -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v $HOME/techwatch:/app techwatch-gui python gui_main.py $CRON_MARKER"
    echo "$CRON_CMD" | sudo tee "$CRON_FILE" > /dev/null
    sudo chmod 644 "$CRON_FILE"
    echo "Cron job installed in /etc/cron.d/techwatch-gui: Techwatch GUI will launch every $AUTO_UPDATE_MINUTES minute(s)."
else
    echo "No autoupdate cron job installed (use --autoupdate <minutes> to enable)."
fi

echo "Installation complete. The GUI container is ready. Launch the application via the menu or the start_techwatch_gui.sh script."
