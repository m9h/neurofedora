# FreeSurfer environment setup for Fedora (csh/tcsh)
# Installed by freesurfer RPM to /etc/profile.d/

setenv FREESURFER_HOME /usr/lib/freesurfer
setenv PATH "${FREESURFER_HOME}/bin:${PATH}"

# Default SUBJECTS_DIR to user's home directory
if ( ! $?SUBJECTS_DIR ) then
    setenv SUBJECTS_DIR "${HOME}/freesurfer/subjects"
endif
