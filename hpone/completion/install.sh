#!/bin/bash
# Installation script for HPone bash completion

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_SCRIPT="${SCRIPT_DIR}/hpone-completion.bash"

echo "Installing HPone bash completion..."

# Check if completion script exists
if [[ ! -f "${COMPLETION_SCRIPT}" ]]; then
    echo "Error: Completion script not found at ${COMPLETION_SCRIPT}"
    exit 1
fi

# Make completion script executable
chmod +x "${COMPLETION_SCRIPT}"

# Try system-wide installation first
if [[ -d "/etc/bash_completion.d" ]] && [[ $EUID -eq 0 ]]; then
    cp "${COMPLETION_SCRIPT}" /etc/bash_completion.d/hpone
    echo "✓ Installed system-wide to /etc/bash_completion.d/hpone"
else
    # User-specific installation
    if [[ -d "${HOME}/.bash_completion.d" ]]; then
        cp "${COMPLETION_SCRIPT}" "${HOME}/.bash_completion.d/hpone"
        echo "✓ Installed for current user to ${HOME}/.bash_completion.d/hpone"
    elif [[ -f "${HOME}/.bashrc" ]]; then
        # Add to .bashrc
        if ! grep -q "source.*hpone-completion.bash" "${HOME}/.bashrc"; then
            echo "" >> "${HOME}/.bashrc"
            echo "# HPone bash completion" >> "${HOME}/.bashrc"
            echo "source ${COMPLETION_SCRIPT}" >> "${HOME}/.bashrc"
            echo "✓ Added completion to ${HOME}/.bashrc"
        else
            echo "✓ Completion already configured in ${HOME}/.bashrc"
        fi
    else
        echo "Warning: Could not find .bashrc or .bash_completion.d"
        echo "Please manually source: ${COMPLETION_SCRIPT}"
    fi
fi

echo ""
echo "Installation complete!"
echo ""
echo "To use completion:"
echo "1. Restart your shell, or"
echo "2. Run: source ${COMPLETION_SCRIPT}"
echo ""
echo "Usage examples:"
echo "  ./app.py <TAB>                    # Complete commands"
echo "  ./app.py inspect <TAB>            # Complete tool names"
echo "  ./app.py up <TAB>                 # Complete tool names or --all"
echo "  ./app.py clean --all <TAB>        # Complete options"
