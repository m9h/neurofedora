cmake_minimum_required(VERSION 3.16)
project(neurofedora-simpleitk-smoke NONE)

include(CTest)

# Use the SYSTEM interpreter, not whatever "python3" happens to be first on PATH.
# These tests exist to verify RPM-installed modules, which live in the system
# interpreter's site-packages. A conda/miniforge or pyenv python earlier on PATH
# has a different site-packages entirely, so every import fails and the component
# reports a total wipeout that looks like a broken package. Seen live on
# rpi-the-great, where python3 is miniforge3's 3.13 while the RPMs install into
# /usr/lib64/python3.14 -- VTK-python and SimpleITK reported 0/4 while the system
# interpreter imported both fine.
# (The mirror of this is legion, where a pip --user joblib made a MISSING RPM
# dependency look satisfied. Both directions corrupt the dashboard.)
set(PYTHON3 /usr/bin/python3)
if(NOT EXISTS "${PYTHON3}")
  message(FATAL_ERROR "system interpreter ${PYTHON3} not found")
endif()

add_test(NAME simpleitk-import
         COMMAND ${PYTHON3} -c "import SimpleITK as sitk; print('SimpleITK', sitk.Version_VersionString())")

add_test(NAME simpleitk-image-create
         COMMAND ${PYTHON3} -c "import SimpleITK as sitk; img=sitk.Image([16,16,16], sitk.sitkFloat32); img+=1.0; assert img.GetSize()==(16,16,16); print('size', img.GetSize())")

add_test(NAME simpleitk-gaussian
         COMMAND ${PYTHON3} -c "import SimpleITK as sitk; img=sitk.Image([16,16,16], sitk.sitkFloat32); img+=1.0; sm=sitk.DiscreteGaussian(img, 1.5); print('mean', sitk.GetArrayViewFromImage(sm).mean())")

add_test(NAME simpleitk-nifti-roundtrip
         COMMAND ${PYTHON3} -c "import SimpleITK as sitk, os, tempfile; td=tempfile.mkdtemp(); p=os.path.join(td,'rt.nii.gz'); img=sitk.Image([8,8,8], sitk.sitkFloat32); img+=2.0; sitk.WriteImage(img,p); r=sitk.ReadImage(p); assert r.GetSize()==(8,8,8); print('ok', p)")
