#!/bin/sh
# /etc/profile.d/slicer.sh — 3D Slicer environment hook
#
# Selects $Slicer_HOME based on (in order):
#   1. SLICER_HOME pre-set in parent shell (advanced override)
#   2. ~/.slicer/version            (per-user pin: write "5.10.0")
#   3. /etc/slicer/default-version  (site-wide pin)
#   4. newest /usr/lib/slicer-* directory (alphabetical => version-sort)
#
# Then prepends $Slicer_HOME to PATH so `slicer` invokes the right copy
# even if multiple parallel-installed versions are present.

if [ -z "${Slicer_HOME:-}" ]; then
    if [ -f "$HOME/.slicer/version" ]; then
        _ver=$(cat "$HOME/.slicer/version" 2>/dev/null)
    elif [ -f /etc/slicer/default-version ]; then
        _ver=$(cat /etc/slicer/default-version 2>/dev/null)
    else
        _ver=$(ls -1 /usr/lib/ 2>/dev/null | grep '^slicer-' | sort -V | tail -1 | sed 's/^slicer-//')
    fi
    if [ -n "$_ver" ] && [ -d "/usr/lib/slicer-$_ver" ]; then
        Slicer_HOME="/usr/lib/slicer-$_ver"
        export Slicer_HOME
        case ":${PATH}:" in
            *":$Slicer_HOME:"*) : ;;
            *) PATH="$Slicer_HOME:$PATH"; export PATH ;;
        esac
    fi
    unset _ver
fi
