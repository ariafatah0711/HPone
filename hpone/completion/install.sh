#!/bin/bash
# Installation script for HPone bash completion

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPLETION_SCRIPT="${SCRIPT_DIR}/hpone-completion.bash"
ABS_COMPLETION_SCRIPT="$(cd "$(dirname "${COMPLETION_SCRIPT}")" && pwd)/$(basename "${COMPLETION_SCRIPT}")"

echo "Installing HPone bash completion..."

if [[ ! -f "${COMPLETION_SCRIPT}" ]]; then
    echo "Error: Completion script not found at ${COMPLETION_SCRIPT}"
    exit 1
fi

chmod +x "${COMPLETION_SCRIPT}"

if [[ -d "/etc/bash_completion.d" ]] && [[ $EUID -eq 0 ]]; then
    cp "${COMPLETION_SCRIPT}" /etc/bash_completion.d/hpone
    echo "✓ Installed system-wide to /etc/bash_completion.d/hpone"
else
    if [[ -d "${HOME}/.bash_completion.d" ]]; then
        cp "${COMPLETION_SCRIPT}" "${HOME}/.bash_completion.d/hpone"
        echo "✓ Installed for current user to ${HOME}/.bash_completion.d/hpone"
    elif [[ -f "${HOME}/.bashrc" ]]; then
        if ! grep -q "hpone-completion.bash" "${HOME}/.bashrc"; then
            echo "" >> "${HOME}/.bashrc"
            echo "# HPone bash completion" >> "${HOME}/.bashrc"
            echo "source ${ABS_COMPLETION_SCRIPT}" >> "${HOME}/.bashrc"
            echo "✓ Added completion to ${HOME}/.bashrc"
        else
            echo "✓ Completion already configured in ${HOME}/.bashrc"
        fi
    else
        echo "Warning: Could not find .bashrc or .bash_completion.d"
        echo "Please manually source: ${ABS_COMPLETION_SCRIPT}"
    fi
fi

echo ""
echo "Installation complete!"
echo "Restart your shell or run: source ${ABS_COMPLETION_SCRIPT}"
