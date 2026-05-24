# /etc/profile.d/freesurfer.sh — POSIX-shell environment for FreeSurfer.
#
# Selection order for which install to source:
#   1) $FREESURFER_HOME already set in the parent shell → leave alone.
#   2) $HOME/.freesurfer/version (per-user pin), e.g. "7.4.1"
#   3) /etc/freesurfer/default-version (system default)
#   4) Newest installed version under /usr/lib/freesurfer-* (lexical sort)
#
# License selection (in same shell context):
#   1) $HOME/.freesurfer/license.txt if present
#   2) /etc/freesurfer/license.txt if present
#   3) (none — most tools will refuse to run; user should run
#       freesurfer-license-install)

if [ -z "$FREESURFER_HOME" ]; then
    _fs_pin=""
    if [ -r "$HOME/.freesurfer/version" ]; then
        _fs_pin=$(cat "$HOME/.freesurfer/version" 2>/dev/null)
    elif [ -r /etc/freesurfer/default-version ]; then
        _fs_pin=$(cat /etc/freesurfer/default-version 2>/dev/null)
    fi
    if [ -n "$_fs_pin" ] && [ -d "/usr/lib/freesurfer-${_fs_pin}" ]; then
        FREESURFER_HOME="/usr/lib/freesurfer-${_fs_pin}"
    else
        _fs_latest=$(ls -d /usr/lib/freesurfer-*/ 2>/dev/null | sort -V | tail -1)
        [ -n "$_fs_latest" ] && FREESURFER_HOME="${_fs_latest%/}"
    fi
    unset _fs_pin _fs_latest
    [ -n "$FREESURFER_HOME" ] && export FREESURFER_HOME
fi

# License: per-user wins. The symlink at $FREESURFER_HOME/license.txt
# already points to /etc/freesurfer/license.txt, so we only export
# FS_LICENSE explicitly when a per-user override exists.
if [ -r "$HOME/.freesurfer/license.txt" ]; then
    export FS_LICENSE="$HOME/.freesurfer/license.txt"
fi

# Source the version-specific env if available. SetUpFreeSurfer.sh sets
# PATH, SUBJECTS_DIR, FUNCTIONALS_DIR, MNI_DIR, etc.
if [ -n "$FREESURFER_HOME" ] && [ -r "$FREESURFER_HOME/SetUpFreeSurfer.sh" ]; then
    # Silence FreeSurfer's verbose source-time output for /etc/profile.d use;
    # users sourcing manually still see it.
    . "$FREESURFER_HOME/SetUpFreeSurfer.sh" > /dev/null 2>&1
fi
