# FSL environment setup for Fedora
# Installed by the fsl RPM to /etc/profile.d/
export FSLDIR=/usr/lib/fsl
export PATH="${FSLDIR}/share/fsl/bin:${PATH}"
if [ -f "${FSLDIR}/etc/fslconf/fsl.sh" ]; then
    . "${FSLDIR}/etc/fslconf/fsl.sh"
fi
export FSLOUTPUTTYPE="${FSLOUTPUTTYPE:-NIFTI_GZ}"
