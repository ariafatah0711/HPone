#!/usr/bin/env bash
set -e

APP_NAME="hpone"
VERSION="2.2.0"
BUILD_DIR="/tmp/${APP_NAME}_pkg"
INSTALL_DIR="${BUILD_DIR}/opt/${APP_NAME}"
BIN_DIR="${BUILD_DIR}/usr/bin"
BASH_COMPLETION_DIR="${BUILD_DIR}/usr/share/bash-completion/completions"
DEBIAN_DIR="${BUILD_DIR}/DEBIAN"
PKG_NAME="${APP_NAME}_${VERSION}_all.deb"
REPO_URL="https://github.com/ariafatah0711/HPone.git"

echo "[*] Cleanup old build..."
rm -rf "$BUILD_DIR"
mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$BASH_COMPLETION_DIR" "$DEBIAN_DIR"

echo "[*] Clone source code (without git history)..."
git clone --depth=1 "$REPO_URL" "$INSTALL_DIR"
rm -rf "$INSTALL_DIR/.git"

echo "[*] Create control file..."
cat > "$DEBIAN_DIR/control" <<EOF
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-pip, docker.io, curl
Maintainer: Aria Fatah <ariafatah07@gmail.com>
Description: HPone - Honeypot Manager
 Simple honeypot management tool in Python with bash completion support.
EOF

echo "[*] Create launcher script..."
cat > "$BIN_DIR/$APP_NAME" <<EOF
#!/usr/bin/env bash
exec python3 /opt/$APP_NAME/app.py "\$@"
EOF
chmod +x "$BIN_DIR/$APP_NAME"

echo "[*] Install bash completion..."
if [ -f "$INSTALL_DIR/hpone/completion/hpone-completion.bash" ]; then
    cp "$INSTALL_DIR/hpone/completion/hpone-completion.bash" \
       "$BASH_COMPLETION_DIR/$APP_NAME"
else
    echo "# no completion file found" > "$BASH_COMPLETION_DIR/$APP_NAME"
fi

echo "[*] Create postinst script..."
cat > "$DEBIAN_DIR/postinst" <<EOF
#!/bin/sh
set -e

# Install Python deps
if [ -f /opt/hpone/requirements.txt ]; then
    pip3 install -r /opt/hpone/requirements.txt
fi

# Check docker-compose executable system-wide
if ! command -v docker-compose >/dev/null 2>&1 && [ ! -f /usr/local/lib/docker/cli-plugins/docker-compose ]; then
    echo "Docker Compose tidak ditemukan, menginstall..."
    mkdir -p /usr/local/lib/docker/cli-plugins
    curl -SL https://github.com/docker/compose/releases/download/v2.29.0/docker-compose-linux-x86_64 \
      -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
fi

# Reload bash completion
if command -v complete >/dev/null 2>&1; then
    if [ -f /usr/share/bash-completion/completions/hpone ]; then
        echo "[+] Bash completion installed for hpone"
    fi
fi

echo "[+] Docker & Compose installed (logout/login for docker group changes to apply)"
exit 0
EOF
chmod 755 "$DEBIAN_DIR/postinst"

echo "[*] Create prerm script..."
cat > "$DEBIAN_DIR/prerm" <<EOF
#!/bin/sh
set -e
# Remove bash completion
rm -f /usr/share/bash-completion/completions/$APP_NAME
exit 0
EOF
chmod 755 "$DEBIAN_DIR/prerm"

echo "[*] Create postrm script..."
cat > "$DEBIAN_DIR/postrm" <<EOF
#!/bin/sh
set -e
# Remove app files after uninstall
rm -rf /opt/$APP_NAME
exit 0
EOF
chmod 755 "$DEBIAN_DIR/postrm"

echo "[*] Build .deb package..."
dpkg-deb --build "$BUILD_DIR" "$PKG_NAME"

echo "[*] Done! Package created: $PKG_NAME"
