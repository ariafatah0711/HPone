#!/bin/bash
# Bash completion script for HPone Docker Template Manager
# 
# Installation:
# 1. Copy this file to /etc/bash_completion.d/ or ~/.bash_completion.d/
# 2. Or source it directly: source hpone-completion.bash
# 3. Restart your shell or run: source ~/.bashrc

_hpone_completion() {
    local cur prev opts cmds
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    
    # Available commands
    cmds="check import update list status inspect enable disable up down shell clean"
    
    # If this is the first argument (command)
    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${cmds}" -- "${cur}") )
        return 0
    fi
    
    # Get the command
    local cmd="${COMP_WORDS[1]}"
    
    case "${cmd}" in
        "import"|"inspect"|"enable"|"disable"|"up"|"down"|"shell"|"clean")
            # These commands need a tool name
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                # Get available tools from tools/ directory
                local tools_dir="tools"
                if [[ -d "${tools_dir}" ]]; then
                    local tools=$(find "${tools_dir}" -name "*.yml" -exec basename {} .yml \; 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${tools}" -- "${cur}") )
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
        "update")
            # Update command doesn't need additional arguments
            ;;
    esac
    
    # Handle options for specific commands
    case "${cmd}" in
        "import")
            if [[ ${COMP_CWORD} -eq 3 ]]; then
                COMPREPLY=( $(compgen -W "--all --force" -- "${cur}") )
            fi
            ;;
        "up")
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                # First try to complete tool names
                local tools_dir="tools"
                if [[ -d "${tools_dir}" ]]; then
                    local tools=$(find "${tools_dir}" -name "*.yml" -exec basename {} .yml \; 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${tools} --all" -- "${cur}") )
                else
                    COMPREPLY=( $(compgen -W "--all" -- "${cur}") )
                fi
            elif [[ ${COMP_CWORD} -eq 3 ]]; then
                if [[ "${prev}" == "--all" ]]; then
                    COMPREPLY=( $(compgen -W "--update" -- "${cur}") )
                else
                    COMPREPLY=( $(compgen -W "--force --update" -- "${cur}") )
                fi
            fi
            ;;
        "down")
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                # First try to complete tool names
                local tools_dir="tools"
                if [[ -d "${tools_dir}" ]]; then
                    local tools=$(find "${tools_dir}" -name "*.yml" -exec basename {} .yml \; 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${tools} --all" -- "${cur}") )
                else
                    COMPREPLY=( $(compgen -W "--all" -- "${cur}") )
                fi
            fi
            ;;
        "clean")
            if [[ ${COMP_CWORD} -eq 2 ]]; then
                # First try to complete tool names
                local tools_dir="tools"
                if [[ -d "${tools_dir}" ]]; then
                    local tools=$(find "${tools_dir}" -name "*.yml" -exec basename {} .yml \; 2>/dev/null)
                    COMPREPLY=( $(compgen -W "${tools} --all" -- "${cur}") )
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

# Register the completion function
complete -F _hpone_completion hpone
complete -F _hpone_completion ./app.py
# complete -F _hpone_completion python3 app.py
# complete -F _hpone_completion python app.py

# Also complete for the script name if it's in PATH
if command -v hpone >/dev/null 2>&1; then
    complete -F _hpone_completion hpone
fi
