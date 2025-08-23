#!/bin/bash
# Bash completion script for HPone Docker Honeypot Manager
#
# Installation:
# 1. Copy this file to /etc/bash_completion.d/ or ~/.bash_completion.d/
# 2. Or source it directly: source hpone-completion.bash
# 3. Restart your shell or run: source ~/.bashrc

# Helper function to find honeypots directory
_hpone_find_honeypots_dir() {
    local honeypots_dir=""

    # Always try to find from script location first (most reliable)
    local script_dir=""
    if [[ -n "${BASH_SOURCE[0]}" ]]; then
        script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd)" || script_dir=""
    fi

    if [[ -n "${script_dir}" ]]; then
        local app_dir="$(dirname "$(dirname "${script_dir}")")"
        if [[ -d "${app_dir}/honeypots" ]]; then
            honeypots_dir="${app_dir}/honeypots"
        fi
    fi

    # Fallback: try current directory
    if [[ -z "${honeypots_dir}" ]] && [[ -d "honeypots" ]]; then
        honeypots_dir="honeypots"
    fi

    # Fallback: try relative to app.py if it exists
    if [[ -z "${honeypots_dir}" ]] && [[ -f "app.py" ]] && [[ -d "honeypots" ]]; then
        honeypots_dir="honeypots"
    fi

    echo "$honeypots_dir"
}

_hpone_completion() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Available commands (hapus import dan update)
    cmds="check list status inspect enable disable up down shell logs clean"

    # If this is the first argument (command)
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- "${cur}") )
        return 0
    fi

    # Get the command
    local cmd="${COMP_WORDS[1]}"

    case "${cmd}" in
        "inspect"|"enable"|"disable"|"up"|"down"|"shell"|"logs"|"clean")
            # These commands need a honeypot name
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                # Get available honeypots from honeypots/ directory
                local honeypots_dir=$(_hpone_find_honeypots_dir)

                if [[ -n "${honeypots_dir}" ]] && [[ -d "${honeypots_dir}" ]]; then
                    local honeypots=$(find "${honeypots_dir}" -name "*.yml" -exec basename {} .yml \; 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${honeypots}" -- "${cur}") )
                fi
            fi
            ;;
        "list")
            # List command has -a option for details
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                COMPREPLY=( $(compgen -W "-a" -- "${cur}") )
            fi
            ;;
        "status"|"check")
            # These commands don't need additional arguments
            ;;
    esac

    # Handle options for specific commands
    case "${cmd}" in
        "up")
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                # First try to complete honeypot names
                local honeypots_dir=$(_hpone_find_honeypots_dir)

                if [[ -n "${honeypots_dir}" ]] && [[ -d "${honeypots_dir}" ]]; then
                    local honeypots=$(find "${honeypots_dir}" -name "*.yml" -exec basename {} .yml \; 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${honeypots} --all" -- "${cur}") )
                else
                    COMPREPLY=( $(compgen -W "--all" -- "${cur}") )
                fi
            elif [[ ${COMP_CWORD} -eq 3 ]]; then
                if [[ "${prev}" == "--all" ]]; then
                    COMPREPLY=( $(compgen -W "--force") )
                fi
            fi
            ;;
        "down")
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                # First try to complete honeypot names
                local honeypots_dir=$(_hpone_find_honeypots_dir)

                if [[ -n "${honeypots_dir}" ]] && [[ -d "${honeypots_dir}" ]]; then
                    local honeypots=$(find "${honeypots_dir}" -name "*.yml" -exec basename {} .yml \; 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${honeypots} --all" -- "${cur}") )
                else
                    COMPREPLY=( $(compgen -W "--all" -- "${cur}") )
                fi
            fi
            ;;
        "clean")
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                # First try to complete honeypot names
                local honeypots_dir=$(_hpone_find_honeypots_dir)

                if [[ -n "${honeypots_dir}" ]] && [[ -d "${honeypots_dir}" ]]; then
                    local honeypots=$(find "${honeypots_dir}" -name "*.yml" -exec basename {} .yml \; 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${honeypots} --all" -- "${cur}") )
                else
                    COMPREPLY=( $(compgen -W "--all" -- "${cur}") )
                fi
            elif [[ ${COMP_CWORD} -eq 3 ]]; then
                if [[ "${prev}" == "--all" ]]; then
                    COMPREPLY=( $(compgen -W "--data --image --volume" -- "${cur}") )
                else
                    COMPREPLY=( $(compgen -W "--data --image --volume" -- "${cur}") )
                fi
            fi
            ;;
    esac

    return 0
}

honeypots_dir=$(_hpone_find_honeypots_dir)
echo $honeypots_dir

# Register the completion function
complete -F _hpone_completion hpone
complete -F _hpone_completion ./app.py
# complete -F _hpone_completion python3 app.py
# complete -F _hpone_completion python app.py

# Also complete for the script name if it's in PATH
if command -v hpone >/dev/null 2>&1; then
    complete -F _hpone_completion hpone
fi
