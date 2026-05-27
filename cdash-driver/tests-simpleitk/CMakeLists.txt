cmake_minimum_required(VERSION 3.16)
project(neurofedora-simpleitk-smoke NONE)

include(CTest)

find_program(PYTHON3 python3 REQUIRED)

add_test(NAME simpleitk-import
         COMMAND ${PYTHON3} -c "import SimpleITK as sitk; print('SimpleITK', sitk.Version_VersionString())")

add_test(NAME simpleitk-image-create
         COMMAND ${PYTHON3} -c "import SimpleITK as sitk; img=sitk.Image([16,16,16], sitk.sitkFloat32); img+=1.0; assert img.GetSize()==(16,16,16); print('size', img.GetSize())")

add_test(NAME simpleitk-gaussian
         COMMAND ${PYTHON3} -c "import SimpleITK as sitk; img=sitk.Image([16,16,16], sitk.sitkFloat32); img+=1.0; sm=sitk.DiscreteGaussian(img, 1.5); print('mean', sitk.GetArrayViewFromImage(sm).mean())")

add_test(NAME simpleitk-nifti-roundtrip
         COMMAND ${PYTHON3} -c "import SimpleITK as sitk, os, tempfile; td=tempfile.mkdtemp(); p=os.path.join(td,'rt.nii.gz'); img=sitk.Image([8,8,8], sitk.sitkFloat32); img+=2.0; sitk.WriteImage(img,p); r=sitk.ReadImage(p); assert r.GetSize()==(8,8,8); print('ok', p)")
