#!/usr/bin/env bash
set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_SRC="$PROJECT_DIR/hpone/completion/hpone-completion.bash"
COMPLETION_TARGET="$HOME/.hpone-completion.bash"
BIN_TARGET="/usr/local/bin/hpone"
REQUIREMENTS="$PROJECT_DIR/requirements.txt"

check_dependencies() {
    echo "[*] Checking dependencies..."

    # Python3
    if ! command -v python3 >/dev/null 2>&1; then
        echo "❌ Python3 not found. Install it first (apt/pacman/dnf)."
        read -p "👉 Do you want to install it now? (y/n): " yn
        case $yn in
            [Yy]*) sudo apt install -y python3 ;;
            *) echo "❌ Failed: Python3 is required."; exit 1 ;;
        esac
        # exit 1
    fi

    # Pip3
    if ! command -v pip3 >/dev/null 2>&1; then
        echo "❌ pip3 not found. Install python3-pip first."
        read -p "👉 Do you want to install it now? (y/n): " yn
        case $yn in
            [Yy]*) sudo apt install -y python3-pip ;;
            *) echo "❌ Failed: pip3 is required."; exit 1 ;;
        esac
        # exit 1
    fi

    # Install Python libs
    if [ -f "$REQUIREMENTS" ]; then
        echo "[*] Installing Python requirements..."
        pip3 install -r "$REQUIREMENTS"
    fi

    # Docker
    if ! command -v docker >/dev/null 2>&1; then
        echo "❌ Docker not found. Install docker first."
        read -p "👉 Do you want to install it now? (y/n): " yn
        case $yn in
            [Yy]*)
                sudo apt install -y docker.io
                sudo usermod -aG docker $USER
                ;;
            *) echo "❌ Failed: Docker is required."; exit 1 ;;
        esac
        # exit 1
    fi

    # docker-compose (old) or docker compose (new)
    if command -v docker-compose >/dev/null 2>&1; then
        echo "[*] docker-compose found."
    elif docker compose version >/dev/null 2>&1; then
        echo "[*] docker compose (plugin) found."
    else
        echo "❌ docker-compose or docker compose not found."
        read -p "👉 Do you want to install docker compose now? (y/n): " yn
        case $yn in
            [Yy]*)
                DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}
                mkdir -p $DOCKER_CONFIG/cli-plugins
                curl -SL https://github.com/docker/compose/releases/download/v2.29.0/docker-compose-linux-x86_64 \
                    -o $DOCKER_CONFIG/cli-plugins/docker-compose
                chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose
                ;;
            *) echo "❌ Failed: docker compose is required."; exit 1 ;;
        esac
    fi
}

install_hpone() {
    check_dependencies

    echo "[*] Installing hpone command..."
    chmod +x "$PROJECT_DIR/app.py"
    sudo ln -sf "$PROJECT_DIR/app.py" "$BIN_TARGET"
    echo "  -> Installed hpone -> $BIN_TARGET"

    if [ -f "$COMPLETION_SRC" ]; then
        echo "[*] Installing bash completion..."

        # Fix line endings if needed
        if command -v dos2unix >/dev/null 2>&1; then
            dos2unix "$COMPLETION_SRC" 2>/dev/null || true
        else
            # Fallback: use sed to remove carriage returns
            sed -i 's/\r$//' "$COMPLETION_SRC" 2>/dev/null || true
        fi

        # Don't copy, use the original version directly
        if ! grep -q "source $COMPLETION_SRC" "$HOME/.bashrc"; then
            echo "source $COMPLETION_SRC" >> "$HOME/.bashrc"
            echo "  -> Added completion to ~/.bashrc"
        fi
    fi

    echo "✅ hpone installed. Restart shell to apply completion."
}

uninstall_hpone() {
    echo "[*] Uninstalling hpone..."
    if [ -L "$BIN_TARGET" ]; then
        sudo rm -f "$BIN_TARGET"
        echo "  -> Removed symlink $BIN_TARGET"
    fi

    if [ -f "$COMPLETION_TARGET" ]; then
        rm -f "$COMPLETION_TARGET"
        echo "  -> Removed completion file $COMPLETION_TARGET"
    fi

    if grep -q "source $COMPLETION_TARGET" "$HOME/.bashrc"; then
        sed -i "\|source $COMPLETION_TARGET|d" "$HOME/.bashrc"
        echo "  -> Removed completion entry from ~/.bashrc"
    fi

    echo "✅ hpone uninstalled."
}

case "$1" in
    install)
        install_hpone
        ;;
    uninstall)
        uninstall_hpone
        ;;
    *)
        echo "Usage: $0 [install|uninstall]"
        ;;
esac
