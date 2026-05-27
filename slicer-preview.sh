#!/bin/sh
# /etc/profile.d/slicer-preview.sh — 3D Slicer Preview environment hook.
# Mirrors slicer.sh but for the preview channel under /usr/lib/slicer-preview.
# Sets Slicer_PREVIEW_HOME and prepends its bin to PATH only if the user
# explicitly exports SLICER_USE_PREVIEW=1 (so the stable `slicer` binary
# remains the default in normal sessions).

if [ -d /usr/lib/slicer-preview ] && [ "${SLICER_USE_PREVIEW:-0}" = "1" ]; then
    Slicer_PREVIEW_HOME=/usr/lib/slicer-preview
    export Slicer_PREVIEW_HOME
    case ":${PATH}:" in
        *":$Slicer_PREVIEW_HOME:"*) : ;;
        *) PATH="$Slicer_PREVIEW_HOME:$PATH"; export PATH ;;
    esac
fi
