# FSL environment setup for Fedora (csh/tcsh)
# Installed by the fsl RPM to /etc/profile.d/
setenv FSLDIR /usr/lib/fsl
setenv PATH ${FSLDIR}/share/fsl/bin:${PATH}
if ( -f ${FSLDIR}/etc/fslconf/fsl.csh ) then
    source ${FSLDIR}/etc/fslconf/fsl.csh
endif
if ( ! $?FSLOUTPUTTYPE ) setenv FSLOUTPUTTYPE NIFTI_GZ
