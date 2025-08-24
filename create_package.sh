#!/usr/bin/env bash
# HPone Debian Package Builder
# Creates a professional .deb package for HPone honeypot management tool
# Author: Aria Fatah <ariafatah07@gmail.com>
# Version: 2.3.0

set -euo pipefail  # Enhanced error handling

# Configuration
APP_NAME="hpone"
VERSION="2.3.1"
ARCHITECTURE="all"
MAINTAINER="Aria Fatah <ariafatah07@gmail.com>"
REPO_URL="https://github.com/ariafatah0711/HPone.git"
DOCKER_COMPOSE_VERSION="v2.29.0"

# Build mode configuration
BUILD_MODE="repo"  # Default to repo mode
SOURCE_DIR="./"     # Default local source directory
CUSTOM_REPO_URL="$REPO_URL"  # Default repository URL

# Build directories
BUILD_DIR="/tmp/${APP_NAME}_pkg"
INSTALL_DIR="${BUILD_DIR}/opt/${APP_NAME}"
BIN_DIR="${BUILD_DIR}/usr/bin"
BASH_COMPLETION_DIR="${BUILD_DIR}/usr/share/bash-completion/completions"
DEBIAN_DIR="${BUILD_DIR}/DEBIAN"
DOC_DIR="${BUILD_DIR}/usr/share/doc/${APP_NAME}"
MANDIR="${BUILD_DIR}/usr/share/man/man1"

# Output configuration
PKG_PATH="${PKG_PATH:-../linux/}"
PKG_NAME="${APP_NAME}_${VERSION}_${ARCHITECTURE}.deb"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Error handler
cleanup() {
    if [ $? -ne 0 ]; then
        log_error "Build failed! Cleaning up..."
        rm -rf "$BUILD_DIR"
    fi
}
trap cleanup EXIT

# Validation functions
validate_dependencies() {
    local missing_deps=()
    local required_deps=("git" "dpkg-deb")

    # Add rsync requirement for local builds
    if [ "$BUILD_MODE" = "local" ]; then
        required_deps+=("rsync")
    fi

    for cmd in "${required_deps[@]}"; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            missing_deps+=("$cmd")
        fi
    done

    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        if [[ " ${missing_deps[*]} " =~ " rsync " ]]; then
            log_info "Please install: sudo apt-get install git dpkg-dev rsync"
        else
            log_info "Please install: sudo apt-get install git dpkg-dev"
        fi
        exit 1
    fi
}

validate_build_mode() {
    case "$BUILD_MODE" in
        "local"|"remote"|"repo")
            # Convert 'remote' and 'repo' to 'repo' internally
            if [ "$BUILD_MODE" = "remote" ]; then
                BUILD_MODE="repo"
            fi
            log_info "Build mode: $BUILD_MODE"
            ;;
        *)
            log_error "Invalid build mode: $BUILD_MODE"
            log_info "Valid modes: local, remote, repo"
            exit 1
            ;;
    esac

    if [ "$BUILD_MODE" = "local" ]; then
        # Use environment variable if set, otherwise use default
        SOURCE_DIR="${SOURCE_DIR:-./}"
        if [ ! -d "$SOURCE_DIR" ]; then
            log_error "Source directory does not exist: $SOURCE_DIR"
            exit 1
        fi
        log_info "Source directory: $(realpath "$SOURCE_DIR")"
    else
        # Use custom repo URL if set, otherwise use default
        CUSTOM_REPO_URL="${CUSTOM_REPO_URL:-$REPO_URL}"
        log_info "Repository URL: $CUSTOM_REPO_URL"
    fi
}

validate_version() {
    if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log_error "Invalid version format: $VERSION (expected: x.y.z)"
        exit 1
    fi
}

# Main functions
show_banner() {
    echo -e "${BLUE}"
    echo "==========================================="
    echo "  HPone Debian Package Builder v$VERSION"
    echo "==========================================="
    echo -e "${NC}"
}

show_usage() {
    echo "Usage: $0 [MODE] [OPTIONS]"
    echo ""
    echo "Build modes:"
    echo "  local                Build from local directory (default: ./)"
    echo "  remote               Build from git repository (default)"
    echo "  repo                 Alias for 'remote'"
    echo ""
    echo "Optional environment variables:"
    echo "  SOURCE_DIR           Local source directory when using 'local' mode (default: ./)"
    echo "  CUSTOM_REPO_URL      Custom repository URL when using 'remote' mode"
    echo "  PKG_PATH             Output directory for .deb package (default: ../linux/)"
    echo ""
    echo "Examples:"
    echo "  # Build from current directory"
    echo "  $0 local"
    echo ""
    echo "  # Build from specific local directory"
    echo "  SOURCE_DIR=/path/to/hpone $0 local"
    echo ""
    echo "  # Build from default repository"
    echo "  $0 remote"
    echo "  $0 repo"
    echo "  $0        # defaults to remote"
    echo ""
    echo "  # Build from custom repository"
    echo "  CUSTOM_REPO_URL=https://github.com/user/fork.git $0 remote"
    echo ""
    echo "Options:"
    echo "  -h, --help           Show this help message"
    echo "  -v, --version        Show version information"
}

show_version() {
    echo "HPone Debian Package Builder v$VERSION"
    echo "Copyright $(date +%Y) Aria Fatah"
}

setup_build_environment() {
    log_info "Setting up build environment..."

    # Cleanup old build
    if [ -d "$BUILD_DIR" ]; then
        log_warning "Removing existing build directory"
        rm -rf "$BUILD_DIR"
    fi

    # Create directory structure
    mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$BASH_COMPLETION_DIR" "$DEBIAN_DIR" "$DOC_DIR" "$MANDIR"

    log_success "Build environment ready"
}

clone_source_code() {
    case "$BUILD_MODE" in
        "local")
            log_info "Copying source code from local directory: $SOURCE_DIR"
            copy_local_source
            ;;
        "repo")
            log_info "Cloning source code from repository: $CUSTOM_REPO_URL"
            clone_from_repository
            ;;
        *)
            log_error "Invalid build mode: $BUILD_MODE (expected: local or repo)"
            exit 1
            ;;
    esac
}

copy_local_source() {
    # Resolve absolute path for source directory
    local abs_source_dir
    abs_source_dir=$(realpath "$SOURCE_DIR")

    if [ ! -d "$abs_source_dir" ]; then
        log_error "Source directory does not exist: $abs_source_dir"
        exit 1
    fi

    log_info "Copying from: $abs_source_dir"

    # Copy all files except build artifacts and version control
    rsync -av \
        --exclude='.git' \
        --exclude='.gitignore' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='*.pyo' \
        --exclude='.pytest_cache' \
        --exclude='build/' \
        --exclude='*.egg-info' \
        --exclude='node_modules' \
        --exclude='.vscode' \
        --exclude='.idea' \
        --exclude='*.deb' \
        --exclude='/tmp' \
        --exclude='__tmp__*' \
        --exclude='create_package.sh' \
        --exclude='data' \
        "$abs_source_dir/" "$INSTALL_DIR/"

    # Verify essential files exist
    verify_essential_files

    log_success "Local source code copied successfully"
}

clone_from_repository() {
    log_info "Cloning source code (shallow clone)..."

    if ! git clone --depth=1 "$CUSTOM_REPO_URL" "$INSTALL_DIR"; then
        log_error "Failed to clone repository: $CUSTOM_REPO_URL"
        exit 1
    fi

    # Remove git metadata
    rm -rf "$INSTALL_DIR/.git"

    # Remove package build script from cloned repository
    rm -f "$INSTALL_DIR/create_package.sh"

    # Verify essential files exist
    verify_essential_files

    log_success "Repository source code cloned successfully"
}

verify_essential_files() {
    local essential_files=("app.py" "requirements.txt" "setup.sh")
    for file in "${essential_files[@]}"; do
        if [ ! -f "$INSTALL_DIR/$file" ]; then
            log_error "Essential file missing: $file"
            log_error "Current directory contents:"
            ls -la "$INSTALL_DIR/" || true
            exit 1
        fi
    done

    log_info "All essential files verified"
}

create_control_file() {
    log_info "Creating Debian control file..."

    # Calculate installed size
    local installed_size
    installed_size=$(du -s "$INSTALL_DIR" | cut -f1)

    # Determine source information for description
    local source_info
    if [ "$BUILD_MODE" = "local" ]; then
        source_info="Built from local source: $(realpath "$SOURCE_DIR")"
    else
        source_info="Built from repository: $CUSTOM_REPO_URL"
    fi

    cat > "$DEBIAN_DIR/control" <<EOF
Package: $APP_NAME
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCHITECTURE
Installed-Size: $installed_size
Depends: python3 (>= 3.6), python3-pip, docker.io (>= 20.10), curl
Recommends: git
Suggests: docker-compose
Maintainer: $MAINTAINER
Homepage: https://github.com/ariafatah0711/HPone
Vcs-Git: $REPO_URL
Vcs-Browser: https://github.com/ariafatah0711/HPone
Description: Professional honeypot management tool
 HPone is a comprehensive Docker-based honeypot management system that
 simplifies the deployment and monitoring of security honeypots. Features
 include auto-import functionality, real-time logging, bash completion,
 and support for multiple honeypot types including Cowrie, Conpot, and more.
 .
 Key features:
  * Auto-import of honeypot templates
  * Real-time ephemeral logging
  * Container lifecycle management
  * Bash auto-completion support
  * Multi-platform honeypot support
 .
 Build Information:
  * $source_info
  * Package built on: $(date '+%Y-%m-%d %H:%M:%S %Z')
EOF

    log_success "Control file created"
}

create_launcher_script() {
    log_info "Creating launcher script..."

    cat > "$BIN_DIR/$APP_NAME" <<'EOF'
#!/usr/bin/env bash
# HPone launcher script
# Automatically generated by package installer

set -e

# Check if Python 3 is available
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: Python 3 is required but not installed." >&2
    echo "Please install Python 3: sudo apt-get install python3" >&2
    exit 1
fi

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo "Warning: Docker is not installed or not in PATH." >&2
    echo "Some features may not work properly." >&2
fi

# Execute HPone
exec python3 /opt/hpone/app.py "$@"
EOF

    chmod +x "$BIN_DIR/$APP_NAME"
    log_success "Launcher script created"
}

install_bash_completion() {
    log_info "Installing bash completion..."

    local completion_source="$INSTALL_DIR/hpone/completion/hpone-completion.bash"

    if [ -f "$completion_source" ]; then
        # Copy and ensure Unix line endings for Linux compatibility
        cp "$completion_source" "$BASH_COMPLETION_DIR/$APP_NAME"

        # Convert Windows line endings to Unix if dos2unix is available
        if command -v dos2unix >/dev/null 2>&1; then
            dos2unix "$BASH_COMPLETION_DIR/$APP_NAME" 2>/dev/null || true
        else
            # Fallback: use sed to convert line endings
            sed -i 's/\r$//' "$BASH_COMPLETION_DIR/$APP_NAME" 2>/dev/null || true
        fi

        log_success "Bash completion installed with proper line endings"
    else
        log_warning "Bash completion file not found, creating placeholder"
        cat > "$BASH_COMPLETION_DIR/$APP_NAME" <<'EOF'
# HPone bash completion placeholder
# The actual completion file was not found during package creation
# Please reinstall the package or check the completion directory
EOF
    fi
}

create_postinst_script() {
    log_info "Creating post-installation script..."

    cat > "$DEBIAN_DIR/postinst" <<EOF
#!/bin/sh
set -e

# Post-installation script for HPone
# This script runs after package installation

log_info() {
    echo "[INFO] \$1"
}

log_success() {
    echo "[SUCCESS] \$1"
}

log_warning() {
    echo "[WARNING] \$1"
}

log_error() {
    echo "[ERROR] \$1" >&2
}

case "\$1" in
    configure)
        log_info "Configuring HPone..."

        # Install Python dependencies
        if [ -f /opt/hpone/requirements.txt ]; then
            log_info "Installing Python dependencies..."
            if pip3 install -r /opt/hpone/requirements.txt --quiet; then
                log_success "Python dependencies installed"
            else
                log_warning "Failed to install some Python dependencies"
            fi
        fi

        # Create necessary directories with proper permissions
        log_info "Creating HPone working directories..."
        mkdir -p /opt/hpone/docker /opt/hpone/data /opt/hpone/conf

        # Set initial permissions for working directories
        if getent group docker >/dev/null 2>&1; then
            chgrp docker /opt/hpone/docker /opt/hpone/data /opt/hpone/conf 2>/dev/null || true
            chmod 775 /opt/hpone/docker /opt/hpone/data /opt/hpone/conf 2>/dev/null || true
        else
            chmod 755 /opt/hpone/docker /opt/hpone/data /opt/hpone/conf 2>/dev/null || true
        fi

        # Check and install Docker Compose if needed
        if ! command -v docker >/dev/null 2>&1; then
            log_warning "Docker is not installed. HPone requires Docker to function properly."
            log_info "Please install Docker: sudo apt-get install docker.io"
        fi

        # Install Docker Compose plugin if not available
        if ! docker compose version >/dev/null 2>&1 && [ ! -f /usr/local/lib/docker/cli-plugins/docker-compose ]; then
            log_info "Installing Docker Compose plugin..."
            mkdir -p /usr/local/lib/docker/cli-plugins
            if curl -SL "https://github.com/docker/compose/releases/download/$DOCKER_COMPOSE_VERSION/docker-compose-linux-x86_64" \
                -o /usr/local/lib/docker/cli-plugins/docker-compose; then
                chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
                log_success "Docker Compose plugin installed"
            else
                log_warning "Failed to install Docker Compose plugin"
            fi
        fi

        # Set proper permissions
        chmod -R 755 /opt/hpone
        chown -R root:root /opt/hpone

        # Configure automatic group inheritance for key directories
        # Any new files/folders created will automatically inherit the docker group
        # Use more permissive permissions to handle Docker container user ID mapping

        # Check if docker group exists, create if not
        if ! getent group docker >/dev/null 2>&1; then
            log_warning "Docker group not found. Creating docker group..."
            groupadd docker
        fi

        # Docker directory - where compose files and .env files are generated/modified
        if [ -d /opt/hpone/docker ]; then
            chgrp -R docker /opt/hpone/docker
            chmod -R 2775 /opt/hpone/docker  # SGID bit ensures group inheritance
            find /opt/hpone/docker -type f -exec chmod 664 {} \;
        fi

        # Data directory - where honeypot data is stored (needs write access for any user)
        if [ -d /opt/hpone/data ]; then
            chgrp -R docker /opt/hpone/data
            chmod -R 2775 /opt/hpone/data  # SGID + world writable for container users
            find /opt/hpone/data -type f -exec chmod 664 {} \;
        fi

        # Conf directory - where configurations are stored
        if [ -d /opt/hpone/conf ]; then
            chgrp -R docker /opt/hpone/conf
            chmod -R 2775 /opt/hpone/conf  # SGID bit ensures group inheritance
            find /opt/hpone/conf -type f -exec chmod 664 {} \;
        fi

        # Honeypots directory - where YAML files might be modified
        if [ -d /opt/hpone/honeypots ]; then
            chgrp -R docker /opt/hpone/honeypots
            chmod -R 2775 /opt/hpone/honeypots  # SGID bit ensures group inheritance
            find /opt/hpone/honeypots -type f -exec chmod 664 {} \;
        fi

        # Set default ACLs for even better inheritance (if available)
        if command -v setfacl >/dev/null 2>&1; then
            log_info "Setting up ACLs for automatic group inheritance..."
            # Standard directories with normal permissions
            for dir in docker conf honeypots; do
                if [ -d "/opt/hpone/\$dir" ]; then
                    setfacl -R -d -m g:docker:rwx "/opt/hpone/\$dir" 2>/dev/null || true
                    setfacl -R -d -m u::rwx "/opt/hpone/\$dir" 2>/dev/null || true
                    setfacl -R -d -m o::r-- "/opt/hpone/\$dir" 2>/dev/null || true
                    setfacl -R -m g:docker:rwx "/opt/hpone/\$dir" 2>/dev/null || true
                fi
            done
            # Data directory with more permissive ACLs for container access
            if [ -d "/opt/hpone/data" ]; then
                setfacl -R -d -m g:docker:rwx "/opt/hpone/data" 2>/dev/null || true
                setfacl -R -d -m u::rwx "/opt/hpone/data" 2>/dev/null || true
                setfacl -R -d -m o::rwx "/opt/hpone/data" 2>/dev/null || true
                setfacl -R -m g:docker:rwx "/opt/hpone/data" 2>/dev/null || true
                setfacl -R -m o::rwx "/opt/hpone/data" 2>/dev/null || true
            fi
        fi

        # Make sure app.py is executable
        chmod +x /opt/hpone/app.py

        # Verify bash completion
        if [ -f /usr/share/bash-completion/completions/hpone ]; then
            log_success "Bash completion installed successfully"
            log_info "Restart your shell or run 'source /etc/bash_completion' to enable completion"
        fi

        log_success "HPone installation completed successfully!"
        log_info "Run 'hpone --help' to get started"
        log_info "Permission setup complete - containers can write to data directory"
        log_info "Add your user to docker group: sudo usermod -aG docker \$USER"
        log_info "Then logout and login again, or run: newgrp docker"
        ;;

    abort-upgrade|abort-remove|abort-deconfigure)
        log_info "Installation aborted"
        ;;

    *)
        log_error "Unknown postinst action: \$1"
        exit 1
        ;;
esac

exit 0
EOF

    chmod 755 "$DEBIAN_DIR/postinst"
    log_success "Post-installation script created"
}

create_prerm_script() {
    log_info "Creating pre-removal script..."

    cat > "$DEBIAN_DIR/prerm" <<EOF
#!/bin/sh
set -e

# Pre-removal script for HPone
case "\$1" in
    remove|upgrade|deconfigure)
        echo "[INFO] Preparing to remove HPone..."

        # Stop any running HPone containers (best effort)
        if command -v docker >/dev/null 2>&1; then
            echo "[INFO] Cleaning up HPone Docker resources..."

            # Stop and remove containers with hpone label
            if docker ps -q --filter "label=hpone" | grep -q .; then
                echo "[INFO] Stopping HPone labeled containers..."
                docker stop \$(docker ps -q --filter "label=hpone") 2>/dev/null || true
                echo "[INFO] Removing HPone labeled containers..."
                docker rm \$(docker ps -aq --filter "label=hpone") 2>/dev/null || true
            fi

            # Remove HPone images by pattern (backward compatibility)
            echo "[INFO] Removing HPone images..."
            docker images --format "{{.Repository}}:{{.Tag}}" | grep -E "^(dtagdevsec|ghcr.io/telekom-security)/" | xargs -r docker rmi 2>/dev/null || true

            # Remove images with hpone label (for new installations)
            if docker images -q --filter "label=hpone" | grep -q .; then
                echo "[INFO] Removing HPone labeled images..."
                docker rmi \$(docker images -q --filter "label=hpone") 2>/dev/null || true
            fi

            echo "[INFO] Docker cleanup completed"
        fi
        ;;

    failed-upgrade)
        echo "[INFO] Upgrade failed, cleaning up..."
        ;;

    *)
        echo "[ERROR] Unknown prerm action: \$1" >&2
        exit 1
        ;;
esac

exit 0
EOF

    chmod 755 "$DEBIAN_DIR/prerm"
    log_success "Pre-removal script created"
}

create_postrm_script() {
    log_info "Creating post-removal script..."

    cat > "$DEBIAN_DIR/postrm" <<EOF
#!/bin/sh
set -e

# Post-removal script for HPone
case "\$1" in
    remove)
        echo "[INFO] Cleaning up HPone files..."

        # Remove bash completion
        rm -f /usr/share/bash-completion/completions/$APP_NAME

        # Remove application directory
        rm -rf /opt/$APP_NAME

        echo "[SUCCESS] HPone removed successfully"
        ;;

    purge)
        echo "[INFO] Purging HPone configuration..."

        # Remove bash completion
        rm -f /usr/share/bash-completion/completions/$APP_NAME

        # Remove application directory
        rm -rf /opt/$APP_NAME

        # Remove any remaining configuration files
        rm -rf /etc/$APP_NAME 2>/dev/null || true

        echo "[SUCCESS] HPone purged successfully"
        ;;

    upgrade|failed-upgrade|abort-install|abort-upgrade|disappear)
        # Do nothing for these cases
        ;;

    *)
        echo "[ERROR] Unknown postrm action: \$1" >&2
        exit 1
        ;;
esac

exit 0
EOF

    chmod 755 "$DEBIAN_DIR/postrm"
    log_success "Post-removal script created"
}

create_documentation() {
    log_info "Creating documentation..."

    # Create copyright file
    cat > "$DOC_DIR/copyright" <<EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: HPone
Upstream-Contact: $MAINTAINER
Source: $REPO_URL

Files: *
Copyright: $(date +%Y) Aria Fatah
License: MIT

License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
EOF

    # Create changelog
    cat > "$DOC_DIR/changelog.Debian.gz" <<EOF
$APP_NAME ($VERSION) unstable; urgency=medium

  * Enhanced Debian package with improved error handling
  * Added comprehensive documentation and validation
  * Internationalized all user-facing messages to English
  * Improved Docker Compose integration
  * Enhanced security and permission handling

 -- $MAINTAINER  $(date -R)
EOF
    gzip "$DOC_DIR/changelog.Debian.gz"

    log_success "Documentation created"
}

build_package() {
    log_info "Building .deb package..."

    # Ensure output directory exists
    mkdir -p "$(dirname "$PKG_PATH$PKG_NAME")"

    # Build the versioned package
    if dpkg-deb --build "$BUILD_DIR" "$PKG_PATH$PKG_NAME"; then
        log_success "Package built successfully: $PKG_PATH$PKG_NAME"

        # Show package information
        local pkg_size
        pkg_size=$(du -h "$PKG_PATH$PKG_NAME" | cut -f1)
        log_info "Package size: $pkg_size"

        # Validate package
        log_info "Validating package..."
        if dpkg-deb --info "$PKG_PATH$PKG_NAME" >/dev/null 2>&1; then
            log_success "Package validation passed"
        else
            log_warning "Package validation failed, but package was created"
        fi

        # Create latest version copy
        local latest_pkg_name="hpone_all.deb"
        local latest_pkg_path="$PKG_PATH$latest_pkg_name"

        log_info "Creating latest version package..."
        if cp "$PKG_PATH$PKG_NAME" "$latest_pkg_path"; then
            log_success "Latest package created: $latest_pkg_path"
        else
            log_warning "Failed to create latest package copy"
        fi

        return 0
    else
        log_error "Failed to build package"
        return 1
    fi
}

# Main execution
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -v|--version)
                show_version
                exit 0
                ;;
            local|remote|repo)
                BUILD_MODE="$1"
                shift
                ;;
            -*)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
            *)
                log_error "Unknown argument: $1"
                log_info "Valid build modes: local, remote, repo"
                show_usage
                exit 1
                ;;
        esac
    done

    show_banner

    # Show current configuration
    log_info "Configuration:"
    log_info "  Build mode: $BUILD_MODE"
    if [ "$BUILD_MODE" = "local" ]; then
        log_info "  Source directory: $(realpath "${SOURCE_DIR:-./}")"
    else
        log_info "  Repository URL: ${CUSTOM_REPO_URL:-$REPO_URL}"
    fi
    log_info "  Output package: $PKG_PATH$PKG_NAME"
    echo

    validate_dependencies
    validate_version
    validate_build_mode

    setup_build_environment
    clone_source_code
    create_control_file
    create_launcher_script
    install_bash_completion
    create_documentation
    create_postinst_script
    create_prerm_script
    create_postrm_script

    if build_package; then
        echo
        log_success "=== BUILD COMPLETED SUCCESSFULLY ==="
        log_info "Versioned package: $PKG_PATH$PKG_NAME"
        log_info "Latest package: ${PKG_PATH}hpone_all.deb"
        log_info "Build mode: $BUILD_MODE"
        if [ "$BUILD_MODE" = "local" ]; then
            log_info "Source: $(realpath "$SOURCE_DIR")"
        else
            log_info "Source: $CUSTOM_REPO_URL"
        fi
        log_info "Install versioned: sudo dpkg -i $PKG_PATH$PKG_NAME && sudo apt-get install -f"
        log_info "Install latest: sudo dpkg -i ${PKG_PATH}hpone_all.deb && sudo apt-get install -f"
        log_info "Or: sudo apt install ./$PKG_NAME"
        echo
    else
        log_error "=== BUILD FAILED ==="
        exit 1
    fi
}

# Execute main function
main "$@"
