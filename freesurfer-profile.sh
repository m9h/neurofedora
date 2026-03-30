# FreeSurfer environment setup for Fedora
# Installed by freesurfer RPM to /etc/profile.d/

export FREESURFER_HOME=/usr/lib/freesurfer
export PATH="${FREESURFER_HOME}/bin:${PATH}"

# Default SUBJECTS_DIR to user's home directory
if [ -z "$SUBJECTS_DIR" ]; then
    export SUBJECTS_DIR="${HOME}/freesurfer/subjects"
fi
