#!/bin/bash
# Uninstall script for HPone bash completion

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_SCRIPT="${SCRIPT_DIR}/hpone-completion.bash"

echo "HPone Bash Completion Uninstaller"
echo "================================="

# Function to remove bash completion
remove_bash_completion() {
    echo "Removing bash completion..."
    
    # Check system-wide installation
    if [[ -f "/etc/bash_completion.d/hpone" ]]; then
        if [[ $EUID -eq 0 ]]; then
            rm -f /etc/bash_completion.d/hpone
            echo "✓ Removed system-wide completion from /etc/bash_completion.d/hpone"
        else
            echo "⚠️  System-wide completion found at /etc/bash_completion.d/hpone"
            echo "   Run: sudo rm /etc/bash_completion.d/hpone"
        fi
    fi
    
    # Check user-specific installation
    if [[ -f "${HOME}/.bash_completion.d/hpone" ]]; then
        rm -f "${HOME}/.bash_completion.d/hpone"
        echo "✓ Removed user completion from ${HOME}/.bash_completion.d/hpone"
    fi
    
    # Check .bashrc for completion lines
    if [[ -f "${HOME}/.bashrc" ]]; then
        # Create backup
        cp "${HOME}/.bashrc" "${HOME}/.bashrc.hpone.backup.$(date +%Y%m%d_%H%M%S)"
        echo "✓ Created backup: ${HOME}/.bashrc.hpone.backup.$(date +%Y%m%d_%H%M%S)"
        
        # Remove completion lines
        local temp_file=$(mktemp)
        local removed_lines=0
        
        while IFS= read -r line; do
            if [[ "$line" =~ hpone-completion ]] || [[ "$line" =~ "HPone bash completion" ]]; then
                echo "  Removing line: $line"
                ((removed_lines++))
            else
                echo "$line" >> "$temp_file"
            fi
        done < "${HOME}/.bashrc"
        
        if [[ $removed_lines -gt 0 ]]; then
            mv "$temp_file" "${HOME}/.bashrc"
            echo "✓ Removed $removed_lines completion lines from ${HOME}/.bashrc"
        else
            rm -f "$temp_file"
            echo "✓ No completion lines found in ${HOME}/.bashrc"
        fi
    fi
}

# Function to clean up completion files
cleanup_completion_files() {
    echo "Cleaning up completion files..."
    
    # List completion files
    echo "Completion files in $SCRIPT_DIR:"
    ls -la "$SCRIPT_DIR"/*.bash 2>/dev/null || echo "  No completion files found"
    
    # Ask if user wants to remove completion files
    echo ""
    read -p "Do you want to remove completion files from $SCRIPT_DIR? [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f "$SCRIPT_DIR"/*.bash
        echo "✓ Removed completion files from $SCRIPT_DIR"
    else
        echo "✓ Keeping completion files in $SCRIPT_DIR"
    fi
}

# Main uninstall logic
echo "This will remove HPone bash completion from your system."
echo ""

# Confirm uninstall
read -p "Are you sure you want to uninstall HPone completion? [y/N]: " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Uninstall cancelled."
    exit 0
fi

echo ""

# Remove bash completion
remove_bash_completion

echo ""

# Clean up files (optional)
cleanup_completion_files

echo ""
echo "✅ Uninstall complete!"
echo ""
echo "To apply changes:"
echo "1. Restart your shell, or"
echo "2. Run: source ~/.bashrc"
echo ""
echo "Note: Backup files have been created with .hpone.backup extension"
echo "You can restore them if needed."
