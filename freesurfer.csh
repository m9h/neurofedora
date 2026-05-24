# /etc/profile.d/freesurfer.csh — tcsh/csh environment for FreeSurfer.
# Mirrors freesurfer.sh; see that file for selection-order documentation.

if (! $?FREESURFER_HOME) then
    set _fs_pin = ""
    if (-r "$HOME/.freesurfer/version") then
        set _fs_pin = `cat "$HOME/.freesurfer/version" >& /dev/null`
    else if (-r /etc/freesurfer/default-version) then
        set _fs_pin = `cat /etc/freesurfer/default-version >& /dev/null`
    endif
    if ("$_fs_pin" != "" && -d "/usr/lib/freesurfer-${_fs_pin}") then
        setenv FREESURFER_HOME "/usr/lib/freesurfer-${_fs_pin}"
    else
        set _fs_latest = `ls -d /usr/lib/freesurfer-*/ >& /dev/null | sort -V | tail -1`
        if ("$_fs_latest" != "") then
            setenv FREESURFER_HOME "$_fs_latest:h"
        endif
    endif
    unset _fs_pin _fs_latest
endif

if (-r "$HOME/.freesurfer/license.txt") then
    setenv FS_LICENSE "$HOME/.freesurfer/license.txt"
endif

if ($?FREESURFER_HOME) then
    if (-r "$FREESURFER_HOME/SetUpFreeSurfer.csh") then
        source "$FREESURFER_HOME/SetUpFreeSurfer.csh" > /dev/null
    endif
endif
