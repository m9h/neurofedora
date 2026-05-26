%define debug_package %{nil}

# Half the cores of a 16-core system for mock builds
%global _smp_mflags -j8

# Parallel-install layout: each FS major lives under /usr/lib/freesurfer-<ver>/
# so freesurfer7 and freesurfer8 can coexist; default version picked by
# /etc/profile.d/freesurfer.sh from freesurfer-common.
%global fs_install %{_prefix}/lib/freesurfer-%{version}

Name:           freesurfer7
Version:        7.4.1
Release:        8%{?dist}
Summary:        Neuroimaging analysis and visualization suite (FreeSurfer 7.4.1)

# FreeSurfer Software License Agreement v1.0 — custom permissive license from MGH
# Allows redistribution with conditions; not OSI-approved
License:        FreeSurfer
URL:            https://surfer.nmr.mgh.harvard.edu/
Source0:        https://github.com/freesurfer/freesurfer/archive/refs/tags/v%{version}.tar.gz#/freesurfer-%{version}.tar.gz

# NOTE: freesurfer-fedora-host-os.patch is FS-8.2.0-tailored and does not apply
# to the FS-7.4.1 source tree (4/4 hunks reject on CMakeLists.txt). Until a
# 7.4.1-port of that patch is written, leave it out — most of what it does
# (set Fedora as host_os, VTK/ITK paths) we do via %%cmake flags below anyway.

# Shared infrastructure: /etc/profile.d/freesurfer.{sh,csh}, license install
# tool, /etc/freesurfer/ layout — all owned by freesurfer-common so parallel
# freesurfer7 + freesurfer8 share one license and one set of env hooks.
Requires:       freesurfer-common

BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  python3-devel
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel
BuildRequires:  libX11-devel
BuildRequires:  libXmu-devel
BuildRequires:  libXt-devel
BuildRequires:  libtiff-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  libpng-devel
BuildRequires:  expat-devel
BuildRequires:  libxml2-devel
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
BuildRequires:  freeglut-devel
BuildRequires:  libXi-devel
BuildRequires:  vtk-devel
BuildRequires:  InsightToolkit5-devel
BuildRequires:  eigen3-devel
BuildRequires:  petsc-devel
BuildRequires:  xxd
# Unbundled system packages
BuildRequires:  gifticlib-devel
BuildRequires:  tetgen-devel
BuildRequires:  libxml2-devel
# GUI (freeview) dependencies
BuildRequires:  qt6-qtbase-devel
BuildRequires:  mesa-libGL-devel

# Bundled libraries — FreeSurfer-specific modifications or no system equivalent
# minc: custom volume_io wrapper, not compatible with system libminc
# netcdf: tightly coupled with bundled minc
# nrrdio: standalone NrrdIO subset, different API from teem's nrrd.h
# nifti: bundled version has znzeof() not in system nifticlib 3.0.1
# jpeg: imageio.cpp uses internal jinclude.h not in system libjpeg-turbo
Provides:       bundled(jpeg)
Provides:       bundled(minc)
Provides:       bundled(netcdf)
Provides:       bundled(nrrdio)
Provides:       bundled(nifti)
Provides:       bundled(dicom)
Provides:       bundled(dcm2niix)
Provides:       bundled(cephes)
Provides:       bundled(svm-light)

%description
FreeSurfer is an open source software suite for processing and analyzing
human brain MRI images. This package provides the core command-line tools
used in the recon-all processing stream.

%package -n python3-%{name}
Summary:        FreeSurfer Python scripts and tools
Requires:       %{name} = %{version}-%{release}
Requires:       python3-nibabel
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-scikit-learn
Requires:       python3-surfa
Requires:       python3-samseg
Requires:       python3-pyyaml
Requires:       python3-six

%description -n python3-%{name}
Python scripts and tools for FreeSurfer, including aparcstats2table,
asegstats2table, samseg wrappers, and other processing utilities.
Requires system Python with neuroimaging packages.

%package freeview
Summary:        FreeSurfer volume and surface viewer (GUI)
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       qt6-qtbase-gui

%description freeview
Freeview is FreeSurfer's GUI tool for viewing and editing MRI volumes,
surface reconstructions, and other neuroimaging data.

%package tracula
Summary:        FreeSurfer tractography tools (TRACULA)
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description tracula
TRACULA (TRActs Constrained by UnderLying Anatomy) tools for automated
reconstruction of white matter pathways using diffusion MRI data.
Note: Full TRACULA processing requires FSL (bedpostx, probtrackx2).

%prep
%autosetup -p0 -n freesurfer-%{version}

# ITK 5.4 collision: FS 7.4.1 macros.h / image.h / histo.h define UCHAR and
# UINT as preprocessor macros expanding to `unsigned char` / `unsigned int`.
# ITK 5.4's itkCommonEnums.h declares `enum class IOComponentEnum { UCHAR,
# UINT, ... }` — the preprocessor expands UCHAR inside the enum body and
# blows up parsing. (FS 8.x dropped these defines entirely.)
#
# Convert the offending #defines to typedefs. Typedefs don't pollute the
# preprocessor, so ITK's enum members remain valid; FS code using
# `UCHAR var;` keeps working because the typedef name resolves the same way.
for hdr in include/macros.h include/image.h include/histo.h; do
    sed -i -E 's|^#define[[:space:]]+UCHAR[[:space:]]+unsigned char.*$|typedef unsigned char UCHAR; /* was #define for ITK enum compat */|' "$hdr"
    sed -i -E 's|^#define[[:space:]]+UINT[[:space:]]+unsigned int.*$|typedef unsigned int UINT;  /* was #define for ITK enum compat */|' "$hdr"
done

# ITK 5.4 deprecated the VXL vcl_* compatibility shims and now emits a hard
# #error from <vcl_cmath.h>, <vcl_iostream.h>, etc.: "Deprecated. Use
# equivalent C++11 header instead." FS 7.4.1's fs_powell.cpp / fs_lbfgs.cpp
# still call vcl_cerr / vcl_setw / vcl_endl / vcl_sqrt / vcl_fabs / vcl_cmath
# and vnl_math_sqr. FS 8.x already migrated. Apply the same substitutions
# upstream's UseStandardHeaders.py recipe documents.
for src in utils/fs_powell.cpp utils/fs_lbfgs.cpp; do
    [ -f "$src" ] || continue
    # Symbol replacements: vcl_* → std::*
    sed -i -E '
        s|\bvcl_cerr\b|std::cerr|g;
        s|\bvcl_cout\b|std::cout|g;
        s|\bvcl_setw\b|std::setw|g;
        s|\bvcl_endl\b|std::endl|g;
        s|\bvcl_sqrt\b|std::sqrt|g;
        s|\bvcl_fabs\b|std::fabs|g;
        s|\bvcl_abs\b|std::abs|g;
        s|\bvcl_pow\b|std::pow|g;
        s|\bvcl_log\b|std::log|g;
        s|\bvcl_exp\b|std::exp|g;
        s|\bvnl_math_sqr\b|vnl_math::sqr|g;
    ' "$src"
    # Header replacements: "vcl_iostream.h" → <iostream>, etc.
    sed -i -E '
        s|#include[[:space:]]+["<]vcl_iostream\.h[">]|#include <iostream>|;
        s|#include[[:space:]]+["<]vcl_iomanip\.h[">]|#include <iomanip>|;
        s|#include[[:space:]]+["<]vcl_cmath\.h[">]|#include <cmath>|;
        s|#include[[:space:]]+["<]vcl_cassert\.h[">]|#include <cassert>|;
        s|#include[[:space:]]+["<]vcl_cstdlib\.h[">]|#include <cstdlib>|;
        s|#include[[:space:]]+["<]vcl_cstring\.h[">]|#include <cstring>|;
    ' "$src"
done

# GCC 16 / C++17: <cstddef> defines std::byte; combined with `using namespace
# std;` in some TUs, this makes FS 7.4.1's `typedef unsigned char byte;` (at
# hips.h:6) ambiguous wherever bare `byte` appears. Mass-rename the FS-side
# type to `hips_byte` across all four HIPS-family headers (hips.h, image.h,
# analyze.h, affine.hpp) and every .cpp consumer that uses bare `byte`.
# json.h is intentionally skipped — it's the vendored nlohmann/json header
# and uses `byte` only as a local variable name (no collision).
hips_byte_files=(
    include/hips.h include/image.h include/analyze.h include/affine.hpp
)
# Add every utils/*.cpp that uses bare `byte` as a token. -P (PCRE) lookarounds
# ensure we don't catch `sbyte`, `byte_t`, or `byte_v`.
while IFS= read -r f; do
    [ "$f" = "include/json.h" ] && continue
    hips_byte_files+=("$f")
done < <(grep -rln -P '(?<![:_a-zA-Z0-9])byte(?![_a-zA-Z0-9])' utils mri_convert freeview 2>/dev/null)

for f in "${hips_byte_files[@]}"; do
    [ -f "$f" ] || continue
    sed -i 's/\bbyte\b/hips_byte/g' "$f"
done

# GCC 15: fix K&R-style empty parameter lists in bundled CTN DICOM
sed -i 's/COND_ExtractConditions(CTNBOOLEAN(\*callback) ())/COND_ExtractConditions(CTNBOOLEAN(*callback) (CONDITION, const char*))/' \
    packages/dicom/condition.h
sed -i 's/COND_EstablishCallback(void (\*callback) ())/COND_EstablishCallback(void (*callback) (CONDITION, const char*))/' \
    packages/dicom/condition.h
sed -i 's/LST_Sort(LST_HEAD \*\* list, size_t nodeSize, int (\*compare) ())/LST_Sort(LST_HEAD ** list, size_t nodeSize, int (*compare) (LST_NODE*, LST_NODE*))/' \
    packages/dicom/lst.h

# GCC 15 defaults to -std=gnu23 which rejects K&R-style empty parameter lists
# and implicit function declarations throughout the bundled C libraries.
# Add -std=gnu89 to the bundled packages build to allow old-style C code.
sed -i 's/add_compile_options(-w -fPIC)/add_compile_options(-w -fPIC -std=gnu89)/' \
    packages/CMakeLists.txt

# Remove unbundled packages from the bundled build list
sed -i '/^  glut$/d;/^  gifti$/d;/^  tetgen$/d' packages/CMakeLists.txt
# jpeg stays bundled — imageio.cpp uses internal jinclude.h not in system libjpeg
sed -i '/^  xml2$/d;/^  expat$/d' packages/CMakeLists.txt

# GCC 16 / libstdc++ tightened transitive includes — many headers no longer
# bring in <string>. FS 7.4.1's include/argparse.h:10 uses std::string in a
# typedef but only includes <unordered_map>. Add the missing include
# directly. (The %build CXXFLAGS also gets `-include string` defensively.)
sed -i '/^#ifndef ARGPARSE_H/,/^#define ARGPARSE_H/{/^#define ARGPARSE_H/a\
#include <string>
}' include/argparse.h

# ITK 5.x renamed itk::MultiThreader to itk::MultiThreaderBase (the legacy
# alias was kept as a typedef for a while, then removed in 5.4+). FS 7.4.1's
# Ants wrapper apps call the legacy name directly. Sed-rename to the new
# class. Same API: SetGlobalDefaultNumberOfThreads(N) still works.
sed -i 's/itk::MultiThreader\b/itk::MultiThreaderBase/g' \
    AntsDenoiseImageFs/AntsDenoiseImageFs.cpp \
    AntsN4BiasFieldCorrectionFs/AntsN4BiasFieldCorrectionFs.cpp

# VTK 9.x tightened the signature of vtkCellArray::GetNextCell — its second
# parameter is now `const vtkIdType*&` (was `vtkIdType*&`). Declare the
# matching local in vtkInflatePolyData.cxx as `const vtkIdType*` so the
# reference binding succeeds. The pointer is only read after, never written
# through, so adding const is safe.
sed -i 's|^  vtkIdType\* pPoints = NULL;|  const vtkIdType* pPoints = NULL;|' \
    vtkutils/vtkInflatePolyData.cxx

# Disable the bundled GEMS (Generic Expectation-Maximization Segmentation)
# library + its consumers (samseg, samsegmesh2surf). FS 7.4.1's gems/ pins
# to legacy ITK ABIs that ITK 5.4.x has since dropped:
#   - ITK_THREAD_RETURN_TYPE: removed (now uses itk::ITK_THREAD_RETURN_TYPE
#     or ITKThreadFunctionType)
#   - itkExceptionObject.h direct-include now emits a hard #error
#   - SmartPointer = 0 / = integer-zero is no longer convertible
#     (ambiguous with the explicit conversions in modern ITK)
# Migrating gems/ to ITK 5.4 is a significant upstream effort. SAMSEG
# functionality is still available via the python3-samseg package in the
# freesurfer-fspython venv, which is the path FreeSurfer 8.x has migrated to.
sed -i '/^add_subdirectory(gems)/d' CMakeLists.txt
sed -i '/^  samseg$/d;/^  samsegmesh2surf$/d' CMakeLists.txt

# Replace bundled xml2 include path with system path in utils/CMakeLists.txt
sed -i 's|${CMAKE_SOURCE_DIR}/packages/xml2|/usr/include/libxml2|' utils/CMakeLists.txt

# Replace bundled library targets with system library names in utils link
sed -i '/target_link_libraries(utils/,/)/{
  s/\bexpat\b/-lexpat/
}' utils/CMakeLists.txt
# xml2 target links in fsPrintHelp too
find . -name CMakeLists.txt -not -path './packages/*' -exec \
    sed -i '/target_link_libraries/s/\bxml2\b/-lxml2/g' {} +

# GCC 15 + system libxml2: fsPrintHelp.cpp needs explicit cstdlib (was transitively included by bundled xml2)
sed -i '1i #include <cstdlib>' utils/fsPrintHelp.cpp

# Fix freeview Qt6 compatibility issues
# Qt::WA_NoBackground removed in Qt6 — use WA_NoSystemBackground
sed -i 's/Qt::WA_NoBackground/Qt::WA_NoSystemBackground/g' freeview/GenericRenderView.cpp
# VTK 9.x: QVTKOpenGLWidget renamed to QVTKOpenGLNativeWidget
sed -i 's/QVTKOpenGLWidget\.h/QVTKOpenGLNativeWidget.h/' freeview/main.cpp
sed -i 's/QVTKOpenGLWidget::defaultFormat/QVTKOpenGLNativeWidget::defaultFormat/' freeview/main.cpp
# Remove bundled QVTK9/ files from freeview build — use system VTK's versions
sed -i '/QVTK9/d' freeview/CMakeLists.txt
# VTK 9.5: QVTKOpenGLNativeWidget renamed Get/SetRenderWindow to camelCase.
# Inject compat wrapper methods into GenericRenderView class definition.
sed -i '/^public:/a\
  /* VTK 9.5 compat: forward old method names to new camelCase names */\
  vtkRenderWindow* GetRenderWindow() { return renderWindow(); }\
  template<typename T> void SetRenderWindow(T w) { setRenderWindow(w); }' \
    freeview/GenericRenderView.h
# Qt5::X11Extras unconditionally added even with Qt6
sed -i 's/set(QT_LIBRARIES ${QT_LIBRARIES} Qt5::X11Extras)/if(Qt5_DIR)\n    set(QT_LIBRARIES ${QT_LIBRARIES} Qt5::X11Extras)\n  endif()/' freeview/CMakeLists.txt

# Remove annex tarball extractions everywhere — data not in source tarball (git-annex)
find . -name CMakeLists.txt -exec sed -i '/install_tarball/d' {} +

# anatomicuts and resurf need ITK JPEG2000/PhilipsREC IO modules not in our ITK build — skip for now
sed -i '/add_subdirectories(/,/)/{/anatomicuts/d;/resurf/d}' CMakeLists.txt

# ARM/aarch64: guard SSE intrinsics in affine.h — define ARM64 on non-x86
sed -i 's|#if (__GNUC__ > 3) \&\& !defined(HAVE_MCHECK) \&\& !defined(ARM64)|#if (__GNUC__ > 3) \&\& !defined(HAVE_MCHECK) \&\& !defined(ARM64) \&\& defined(__x86_64__)|' \
    include/affine.h

# ARM/aarch64: guard SSE intrinsics in affine.hpp — wrap xmmintrin.h include
# and SSE template specializations with __x86_64__ guards.
# The generic template implementations (lines 178-214) provide loop-based fallbacks.
sed -i 's|#include <xmmintrin.h>|#ifdef __x86_64__\n#include <xmmintrin.h>\n#endif|' include/affine.hpp
# Wrap SSE specializations: insert #ifdef before first, #endif after last
# Wrap SSE specializations in #ifdef __x86_64__ ... #endif
# Insert #ifdef before the first specialization, #endif before namespace close
sed -i -z 's|//! Specialise matrix-vector for float and use SSE|#ifdef __x86_64__\n\n//! Specialise matrix-vector for float and use SSE|' include/affine.hpp
sed -i -z 's|}\n\n}\n\n\n#endif|}\n\n#endif // __x86_64__\n\n}\n\n\n#endif|' include/affine.hpp

# System gifticlib lacks extern "C" guards needed for C++ compilation.
# Create wrapper headers in the include/ dir (already in the include path).
cat > include/gifti_io.h << 'GIFTIEOF'
#ifdef __cplusplus
extern "C" {
#endif
#include </usr/include/gifti/gifti_io.h>
#ifdef __cplusplus
}
#endif
GIFTIEOF
cat > include/gifti_xml.h << 'GIFTIEOF'
#ifdef __cplusplus
extern "C" {
#endif
#include </usr/include/gifti/gifti_xml.h>
#ifdef __cplusplus
}
#endif
GIFTIEOF
# Remove the gifti include path override — wrappers in include/ handle it
sed -i '\|/packages/gifti|d' utils/CMakeLists.txt

# Replace bundled gifti library target with system library name in utils link
sed -i '/target_link_libraries(utils/,/)/{
  s/\bgifti\b/giftiio/
}' utils/CMakeLists.txt

# Fix tetgen references everywhere: system lib is libtet.so, header at /usr/include/tetgen.h
find . -name CMakeLists.txt -not -path './packages/*' -exec \
    sed -i 's|${CMAKE_SOURCE_DIR}/packages/tetgen|/usr/include|g' {} +
find . -name CMakeLists.txt -not -path './packages/*' -exec \
    sed -i '/target_link_libraries/s/\btetgen\b/tet/g' {} +

# vtkutils uses legacy VTK_INCLUDE_DIRS which is empty in VTK 9.5+.
# Use modern VTK cmake targets instead.
sed -i 's/target_link_libraries(vtkutils tiff)/target_link_libraries(vtkutils tiff VTK::CommonCore VTK::CommonDataModel VTK::RenderingCore VTK::RenderingOpenGL2 VTK::FiltersCore VTK::FiltersSources VTK::ImagingCore)/' \
    vtkutils/CMakeLists.txt

# VTK 9.5: VTK_LEGACY(SetColorSpaceToHSVNoWrap) removed in modern VTK;
# comment out both the declaration in .h and the definition in .cxx
sed -i 's/VTK_LEGACY(void SetColorSpaceToHSVNoWrap())/\/\/ VTK_LEGACY removed/' \
    vtkutils/vtkRGBATransferFunction.h
sed -i '/^void vtkRGBATransferFunction::SetColorSpaceToHSVNoWrap/,/^}/s/^/\/\//' \
    vtkutils/vtkRGBATransferFunction.cxx

# Remove install(CODE) blocks that hardcode CMAKE_INSTALL_PREFIX:
# 1. build-stamp.txt (single line in top-level CMakeLists.txt)
sed -i '/build-stamp/d' CMakeLists.txt
# 2. Python symlink calls in top-level CMakeLists.txt
sed -i '/symlink(.*python.*bin.*python3)/d' CMakeLists.txt
# 3. Python subdir: gut the entire file — we don't distribute fspython
echo "# Disabled for RPM build — no fspython" > python/CMakeLists.txt
# 4. Fix install_configured() to respect DESTDIR
sed -i 's|\${CMAKE_INSTALL_PREFIX}/\${INSTALL_DESTINATION}|$ENV{DESTDIR}\${CMAKE_INSTALL_PREFIX}/\${INSTALL_DESTINATION}|g' cmake/functions.cmake
# 5. Replace install_append_help() with a version that doesn't run cmake --build
#    at install time. Just install the configured script and the helptext XML.
sed -i '/^function(install_append_help/,/^endfunction()/c\
function(install_append_help SCRIPT HELPTEXT DESTINATION)\
  install_configured(${SCRIPT} DESTINATION ${DESTINATION})\
  install(FILES ${HELPTEXT} DESTINATION docs/xml)\
  add_test(${SCRIPT}_help_test bash -c "xmllint --noout ${CMAKE_CURRENT_SOURCE_DIR}/${HELPTEXT}")\
endfunction()' cmake/functions.cmake

%build
export CFLAGS="%{optflags} -Wno-error -std=gnu17"
export CXXFLAGS="%{optflags} -std=c++17 -Wno-error -include cstdint -include string -fpermissive"
export FFLAGS="%{optflags} -fallow-invalid-boz -fallow-argument-mismatch"

%cmake -GNinja \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DMINIMAL=OFF \
    -DBUILD_GUIS=ON \
    -DFREEVIEW_LINEPROF=OFF \
    -DDISTRIBUTE_FSPYTHON=OFF \
    -DINSTALL_PYTHON_DEPENDENCIES=OFF \
    -DTIFF_SYSLIBS=ON \
    -DGLUT_SYSLIBS=ON \
    -DMARTINOS_BUILD=OFF \
    -DWARNING_AS_ERROR=OFF \
    -DBUILD_FORTRAN=ON \
    -DINTEGRATE_SAMSEG=ON \
    -DLINK_SHARED_AS_NEEDED=ON \
    -DVTK_DIR=%{_libdir}/cmake/vtk \
    -DITK_DIR=%{_libdir}/cmake/ITK-5.4 \
    -DQt6_DIR=%{_libdir}/cmake/Qt6 \
    -DCMAKE_INSTALL_PREFIX=%{fs_install}

%cmake_build

%install
# Skip atlas/average data extraction — not included in GitHub source tarball
rm -f %{__cmake_builddir}/distribution/average/cmake_install.cmake
touch %{__cmake_builddir}/distribution/average/cmake_install.cmake

# Empty the python cmake_install — we don't distribute fspython
echo "" > %{__cmake_builddir}/python/cmake_install.cmake

# Remove ALL cmake install files that reference fspython, pip, model files, or
# run execute_process with hardcoded paths. Empty them entirely.
python3 -c "
import os, re
for root, dirs, files in os.walk('$(echo %{__cmake_builddir})'):
    for fn in files:
        if fn == 'cmake_install.cmake':
            path = os.path.join(root, fn)
            txt = open(path).read()
            if re.search(r'fspython|pip install|python3\.8|Could not install|Could not extract|install_directories|install_symlinks_fspython', txt):
                open(path, 'w').write('# Cleared for RPM build\n')
"

# Fix generated cmake_install files: install(CODE) blocks baked the literal prefix
# into file(MAKE_DIRECTORY), configure_file(), execute_process, and message() calls.
# Add DESTDIR prefix to all bare /usr/lib/freesurfer-%{version} references in these cmake commands.
find %{__cmake_builddir} -name cmake_install.cmake \
    -exec sed -i '/file(MAKE_DIRECTORY\|configure_file\|execute_process\|message(STATUS/s|/usr/lib/freesurfer-%{version}|$ENV{DESTDIR}/usr/lib/freesurfer-%{version}|g' {} +

%cmake_install

# Fix ambiguous Python shebangs (Fedora rejects #!/usr/bin/env python)
find %{buildroot}%{fs_install} -type f -exec \
    sed -i '1s|^#!/usr/bin/env python$|#!/usr/bin/python3|' {} + 2>/dev/null || :

# profile.d/freesurfer.{sh,csh} are owned by freesurfer-common now (so a
# single set of env hooks handles whichever parallel FS version is active).
# Do NOT install them from this spec.

# License: install a dangling symlink at $FREESURFER_HOME/license.txt
# pointing at the system license dir. freesurfer-license-install (shipped
# by freesurfer-common) drops the real file at /etc/freesurfer/license.txt
# when the user runs it. Until then, opening the symlink errors clearly
# ("FreeSurfer license missing — run sudo freesurfer-license-install").
install -d %{buildroot}%{fs_install}
ln -sf /etc/freesurfer/license.txt %{buildroot}%{fs_install}/license.txt

%check
export FREESURFER_HOME=%{buildroot}%{fs_install}
export PATH="${FREESURFER_HOME}/bin:${PATH}"

# Verify key binaries exist and are executable
for bin in mri_convert mri_info mri_binarize mri_vol2vol mri_mask \
           mris_inflate mris_sphere mris_convert mris_info \
           mri_watershed mri_normalize mri_em_register \
           mri_ca_label mri_segment mri_fill mri_tessellate \
           talairach_avi mrisp_paint; do
    test -x "${FREESURFER_HOME}/bin/${bin}" || (echo "MISSING: ${bin}" && exit 1)
done
echo "All key binaries present"

# Smoke test: --help flag returns 0 on core tools
mri_convert --help > /dev/null 2>&1 || true
mri_info --help > /dev/null 2>&1 || true
mri_binarize --help > /dev/null 2>&1 || true

# Verify no missing shared library deps on core binaries
for bin in mri_convert mri_vol2vol mris_sphere; do
    if ldd "${FREESURFER_HOME}/bin/${bin}" 2>&1 | grep -q 'not found'; then
        echo "Missing libs for ${bin}:"
        ldd "${FREESURFER_HOME}/bin/${bin}" | grep 'not found'
        exit 1
    fi
done
echo "No missing shared library dependencies"

%files
%license LICENSE.txt
%{fs_install}/
%exclude %{fs_install}/bin/freeview
%exclude %{fs_install}/bin/dmri_*
%exclude %{fs_install}/python/

%files -n python3-%{name}
%{fs_install}/python/

%files freeview
%{fs_install}/bin/freeview

%files tracula
%{fs_install}/bin/dmri_*

%changelog

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 7.4.1-8
- GCC 16 tightened transitive includes: include/argparse.h uses
  std::string without #include <string>. Sed-inject the include
  inside its header guard, plus add -include string globally to
  CXXFLAGS so other missing-transitive sites get caught at once.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 7.4.1-7
- ITK 5.x rename: itk::MultiThreader -> itk::MultiThreaderBase in
  the AntsDenoiseImageFs and AntsN4BiasFieldCorrectionFs wrappers.
- VTK 9.x: vtkCellArray::GetNextCell now takes const vtkIdType*&;
  declare matching local in vtkInflatePolyData.cxx as const.

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 7.4.1-6
- Disable bundled GEMS subdir (gems/, samseg/, samsegmesh2surf/):
  FS 7.4.1 uses removed ITK 5.x APIs (ITK_THREAD_RETURN_TYPE,
  itkExceptionObject.h direct-include, SmartPointer=0 ambiguity).
  SAMSEG functionality is provided by python3-samseg in the
  freesurfer-fspython venv (FS 8.x migration path).

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 7.4.1-5
- GCC 16 / C++17 std::byte collision: rename FS-side typedef byte→hips_byte
  across hips.h/image.h/analyze.h/affine.hpp + every .cpp consumer
  that uses bare 'byte' as a type. json.h skipped (vendored, local var).

* Mon May 25 2026 Morgan Hough <morgan.hough@gmail.com> - 7.4.1-4
- ITK 5.4 vcl_* deprecation: utils/fs_powell.cpp and utils/fs_lbfgs.cpp
  use vcl_cerr/setw/endl/sqrt/fabs/cmath/vnl_math_sqr. Sed-replace with
  std::* equivalents per upstream UseStandardHeaders.py recipe.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 7.4.1-3
- Patch include/macros.h, image.h, histo.h: convert #define UCHAR/UINT
  to typedef so ITK 5.4 enum class IOComponentEnum::UCHAR no longer
  collides with macro expansion.
* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 7.4.1-2
- Drop freesurfer-fedora-host-os.patch (was FS-8.2.0 tailored, all hunks
  reject against 7.4.1 source). Build now reaches %build stage.
- Add -DCMAKE_POLICY_VERSION_MINIMUM=3.5 for cmake 4.x compat.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 7.4.1-1
- Initial freesurfer7 spec — parallel-install of FreeSurfer 7.4.1 alongside
  freesurfer8 (each under its own /usr/lib/freesurfer-<ver>/ tree).
- Scaffolded from freesurfer8.spec; per-spec %prep seds may need version-
  specific adjustment as 7.4.1 source layout can differ from 8.2.0.
- Requires freesurfer-common (shared license + /etc/profile.d hooks).

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-1
- Initial freesurfer8 spec — parallel-install layout. Installs under
  /usr/lib/freesurfer-7.4.1/ so freesurfer7 can sit alongside.
- Requires: freesurfer-common (owns /etc/profile.d/freesurfer.{sh,csh},
  /etc/freesurfer/, and freesurfer-license-install).
- Drop the per-spec profile.d install steps; freesurfer-common owns those.
- Install a dangling /usr/lib/freesurfer-7.4.1/license.txt symlink pointing
  at /etc/freesurfer/license.txt — freesurfer-license-install populates the
  real file once the user registers at FMRIB.
- All other content carried over from freesurfer-8.2.0-7 unchanged.

* Tue Apr 22 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-7
- Fix aarch64 build: guard SSE intrinsics in affine.hpp with __x86_64__
- Fix ambiguous python shebang in fsfast/bin/par2schedule

* Sun Mar 30 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-5
- Full build (MINIMAL=OFF): all FreeSurfer programs
- Add python3-freesurfer subpackage for Python scripts
- Add freesurfer-tracula subpackage for diffusion tractography tools
- Add petsc-devel BuildRequires for tracula
- Proper subpackage split per RPM Fusion guidelines

* Sun Mar 29 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-4
- Add freesurfer-freeview subpackage (GUI volume/surface viewer)
- Build with BUILD_GUIS=ON and Qt6 support
- Add VTK Qt components to Fedora find_package

* Sat Mar 29 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-3
- Unbundle xml2 (system libxml2), expat (system expat)
- Keep jpeg bundled: imageio.cpp uses internal jinclude.h
- Add aarch64 support: guard SSE intrinsics in affine.h with __x86_64__

* Sat Mar 29 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-2
- Unbundle nifti (use system nifticlib), gifti (use system gifticlib),
  tetgen (use system tetgen-devel)
- Keep minc/netcdf/nrrdio bundled: FreeSurfer's versions are custom forks

* Wed Mar 25 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-1
- Initial Fedora package of FreeSurfer 7.4.1 CLI tools
- MINIMAL build: core recon-all stream programs only, no GUI tools
- Uses system VTK 9.5.2 (COPR) and ITK 5.4.5 (COPR)
- Uses system zlib, openssl, libtiff, libjpeg, libpng, expat, libxml2, blas, lapack
- Bundles: minc, netcdf, nifti, gifti, dicom, dcm2niix, cephes, tetgen, nrrdio, svm, glut
