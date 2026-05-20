%global sitk_major 2
%global sitk_minor 5

Name:           python-simpleitk
Version:        2.5.5
Release:        3%{?dist}
Summary:        Simplified interface to the Insight Toolkit (ITK) for image analysis

License:        Apache-2.0
URL:            https://simpleitk.org/
Source0:        https://github.com/SimpleITK/SimpleITK/archive/refs/tags/v%{version}/SimpleITK-%{version}.tar.gz
# Source1 (SimpleITK-%%{version}-R-ExternalData.tar.gz) is retained in
# SOURCES/ but unreferenced here — see the WRAP_R comment in %%build for
# why the R wrap is disabled in this release.

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch:    %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.16
BuildRequires:  ninja-build
BuildRequires:  swig >= 4.0
# Lua interpreter required for filter source code generation (not wrapping)
BuildRequires:  lua
# Doxygen API HTML for the simpleitk-doc subpackage
BuildRequires:  doxygen
BuildRequires:  graphviz
BuildRequires:  InsightToolkit5-devel >= 5.4.6
# ITK VtkGlue is needed for image display support
BuildRequires:  InsightToolkit5-vtk-devel >= 5.4.6
# Python bindings
BuildRequires:  python3-devel
BuildRequires:  python3-numpy
# ITK transitive cmake deps
BuildRequires:  fftw-devel
BuildRequires:  expat-devel
BuildRequires:  libtiff-devel
BuildRequires:  libjpeg-devel
BuildRequires:  libpng-devel
BuildRequires:  zlib-devel
BuildRequires:  hdf5-devel
BuildRequires:  gdcm-devel
BuildRequires:  dcmtk-devel
BuildRequires:  openjpeg2-devel
%if 0%{?fedora}
BuildRequires:  libminc-devel
%endif
# VTK transitive cmake deps (find_package in VTK's module config)
BuildRequires:  vtk-devel
BuildRequires:  freetype-devel
BuildRequires:  pugixml-devel
BuildRequires:  fmt-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  nlohmann-json-devel
BuildRequires:  json-devel
BuildRequires:  lz4-devel
BuildRequires:  xz-devel
BuildRequires:  double-conversion-devel
BuildRequires:  glew-devel
BuildRequires:  libxml2-devel
BuildRequires:  libogg-devel
BuildRequires:  libtheora-devel
BuildRequires:  sqlite-devel
BuildRequires:  libharu-devel
BuildRequires:  proj-devel
BuildRequires:  gdal-devel
BuildRequires:  netcdf-cxx-devel
BuildRequires:  cgnslib-devel
BuildRequires:  libarchive-devel
BuildRequires:  libpq-devel
BuildRequires:  mariadb-connector-c-devel
BuildRequires:  openslide-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXt-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libGL-devel
BuildRequires:  cmake(Qt6)
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  qt5-qtwebkit-devel
BuildRequires:  qt6-qtdeclarative-devel

%global _description %{expand:
SimpleITK is a simplified, open-source interface to the Insight Toolkit
(ITK), a C++ library for computational medical imaging. SimpleITK wraps
ITK's C++ code into Python (and other languages), providing a streamlined
API for image filtering, segmentation, registration, and I/O of 2D, 3D,
and 4D images.}

%description %{_description}

%package -n simpleitk
Summary:        C++ shared libraries
Provides:       simpleitk = %{version}-%{release}

%description -n simpleitk
%{_description}

This package contains the core SimpleITK C++ shared libraries.

%package -n simpleitk-devel
Summary:        Development files
Requires:       simpleitk%{?_isa} = %{version}-%{release}
Requires:       InsightToolkit5-devel >= 5.4.6

%description -n simpleitk-devel
Headers and cmake configuration files for developing C++ applications
with SimpleITK.

%package -n python3-simpleitk
Summary:        Python 3 bindings
Requires:       simpleitk%{?_isa} = %{version}-%{release}
Requires:       python3-numpy
%{?python_provide:%python_provide python3-simpleitk}

%description -n python3-simpleitk
%{_description}

This package contains the Python 3 bindings for SimpleITK.

%package -n simpleitk-doc
Summary:        Doxygen-generated API HTML documentation
BuildArch:      noarch

%description -n simpleitk-doc
%{_description}

This package contains the Doxygen-generated HTML API reference for
SimpleITK. After install, browse %{_docdir}/simpleitk-doc/html/index.html.

%prep
%autosetup -n SimpleITK-%{version}

%build
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint -fpermissive"

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_SKIP_INSTALL_RPATH=ON \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TESTING=OFF \
    -DBUILD_EXAMPLES=OFF \
    -DBUILD_DOXYGEN=ON \
    `# USE_ITK_DOXYGEN_TAGS defaults to ON and fetches ITK's tag file at` \
    `# configure time. With SimpleITK_FORBID_DOWNLOADS=ON that fetch is` \
    `# blocked; the build aborts. Disable the cross-link tags entirely.` \
    -DUSE_ITK_DOXYGEN_TAGS=OFF \
    -DSimpleITK_BUILD_DISTRIBUTE=ON \
    -DSimpleITK_FORBID_DOWNLOADS=ON \
    -DSimpleITK_INT64_PIXELIDS=ON \
    -DSimpleITK_EXPLICIT_INSTANTIATION=OFF \
    -DSimpleITK_USE_ELASTIX=OFF \
    -DSimpleITK_INSTALL_LIBRARY_DIR=%{_lib} \
    -DSimpleITK_INSTALL_ARCHIVE_DIR=%{_lib} \
    -DSimpleITK_INSTALL_PACKAGE_DIR=%{_lib}/cmake/SimpleITK-%{sitk_major}.%{sitk_minor} \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4 \
    -DWRAP_DEFAULT=OFF \
    -DWRAP_PYTHON=ON \
    -DSimpleITK_PYTHON_USE_LIMITED_API=OFF \
    `# WRAP_R deferred: SimpleITK 2.5.5 PR #2587 patched their bundled` \
    `# SWIG for R 4.6.0 API removals, but we use Fedora's system SWIG` \
    `# (no equivalent patch), so the SWIG-generated SimpleITKR_wrap.cxx` \
    `# fails to compile against R 4.6 (read-only CHARACTER_POINTER on` \
    `# STRING_PTR_RO). Reinstate WRAP_R=ON once Fedora's swig package` \
    `# carries the upstream PR #2587 backport or SimpleITK 2.5.6 ships a` \
    `# system-SWIG-compatible workaround.` \
    -DWRAP_R=OFF \
    -DWRAP_LUA=OFF \
    -DWRAP_JAVA=OFF \
    -DWRAP_CSHARP=OFF \
    -DWRAP_TCL=OFF \
    -DWRAP_RUBY=OFF

%cmake_build

%install
%cmake_install

# SimpleITK's cmake LegacyPackaging path (non-SKBUILD) does not install the
# Python module. Manually install the SWIG-generated extension and Python
# package from the build tree into site-packages.
sitk_builddir=%{__cmake_builddir}
install -d %{buildroot}%{python3_sitearch}/SimpleITK

# SWIG-generated C extension (.so)
install -m 0755 ${sitk_builddir}/Wrapping/Python/SimpleITK/_SimpleITK*.so \
    %{buildroot}%{python3_sitearch}/SimpleITK/

# SWIG-generated Python wrapper
install -m 0644 ${sitk_builddir}/Wrapping/Python/SimpleITK/SimpleITK.py \
    %{buildroot}%{python3_sitearch}/SimpleITK/

# Python package files
for f in __init__.py extra.py py.typed; do
    install -m 0644 ${sitk_builddir}/Wrapping/Python/SimpleITK/${f} \
        %{buildroot}%{python3_sitearch}/SimpleITK/
done

# Version file (generated by cmake from _version.py.in)
install -m 0644 ${sitk_builddir}/Wrapping/Python/SimpleITK/_version.py \
    %{buildroot}%{python3_sitearch}/SimpleITK/

# R bindings install step removed — WRAP_R=OFF in this release.

# Move the Doxygen HTML output into the doc subpackage's docdir. Upstream
# emits it to a sibling `Documentation/html/` under the build tree.
install -d %{buildroot}%{_docdir}/simpleitk-doc
if [ -d ${sitk_builddir}/Documentation/html ]; then
    cp -a ${sitk_builddir}/Documentation/html %{buildroot}%{_docdir}/simpleitk-doc/
fi

# Remove bundled docs installed by cmake (we use %doc/%license).
# Note: this strips the cmake-installed doc dir but the doxygen output we
# just placed under %%{_docdir}/simpleitk-doc/ is intentional and stays.
rm -rf %{buildroot}%{_datadir}/doc/SimpleITK-%{sitk_major}.%{sitk_minor}

%check
# Minimal import + version check. Runs against the just-installed Python
# module in %%{buildroot}; uses PYTHONPATH because the module isn't on the
# system path yet at %%check time.
PYTHONPATH=%{buildroot}%{python3_sitearch} \
LD_LIBRARY_PATH=%{buildroot}%{_libdir} \
%{python3} -c "
import SimpleITK as sitk
print('SimpleITK', sitk.Version_VersionString())
print('ITK', sitk.Version_ITKVersionString())
assert sitk.Version_MajorVersion() == %{sitk_major}, 'wrong major'
assert sitk.Version_MinorVersion() == %{sitk_minor}, 'wrong minor'
# Touch a representative filter to confirm the C++ symbols resolve at runtime
img = sitk.Image(64, 64, sitk.sitkUInt8)
img = sitk.SmoothingRecursiveGaussian(img, 1.0)
print('SmoothingRecursiveGaussian ok')
"

%ldconfig_scriptlets -n simpleitk

%files -n simpleitk
%license LICENSE
%doc NOTICE Readme.md
# 48 shared libraries: 5 core + 42 ITK module wrappers + 1 SimpleITKFilters
%{_libdir}/libSimpleITK*-%{sitk_major}.%{sitk_minor}.so.1

%files -n simpleitk-devel
%doc NOTICE Readme.md
%{_includedir}/SimpleITK-%{sitk_major}.%{sitk_minor}/
%{_libdir}/libSimpleITK*-%{sitk_major}.%{sitk_minor}.so
%{_libdir}/cmake/SimpleITK-%{sitk_major}.%{sitk_minor}/

%files -n python3-simpleitk
%doc NOTICE Readme.md
# Python package with SWIG extension, wrapper, and supporting files
%{python3_sitearch}/SimpleITK/

%files -n simpleitk-doc
%license LICENSE
%doc NOTICE Readme.md
%{_docdir}/simpleitk-doc/html/

%changelog
* Wed May 20 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.5-3
- Six Fedora-review-prep fixes:
  1. Drop `%%define debug_package %%{nil}` so the standard Fedora
     strip+debuginfo flow runs. Produces a proper simpleitk-debuginfo
     subpackage; shrinks the simpleitk binary RPM by ~75%%.
  2. Add %%check stanza that imports SimpleITK and exercises one
     representative filter against the just-built tree.
  3. Enable BUILD_DOXYGEN=ON + new simpleitk-doc noarch subpackage
     shipping HTML API reference under %%{_docdir}/simpleitk-doc/html/.
     USE_ITK_DOXYGEN_TAGS=OFF to keep SimpleITK_FORBID_DOWNLOADS=ON.
  4. Add %%doc NOTICE Readme.md to simpleitk-devel and
     python3-simpleitk subpackages (rpmlint no-documentation).
  5. Bump simpleitk-devel's transitive Requires: InsightToolkit5-devel
     to >= 5.4.6 (was >= 5.4.5, stale).
  6. Drop "SimpleITK"/"for SimpleITK" from subpackage Summary: tags
     (rpmlint name-repeated-in-summary).

* Tue May 19 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.5-2
- Disable WRAP_R for now. Build #10480856 failed at step 1057/1058
  compiling SimpleITKR_wrap.cxx — the SWIG-generated R wrapper writes
  through CHARACTER_POINTER(VECTOR_ELT(result, pos))[vpos] which R 4.6
  made read-only (STRING_PTR_RO). SimpleITK 2.5.5's PR #2587 patched
  their bundled SWIG to emit Rf_SET_STRING_ELT-style code, but the
  patch lives in SuperBuild/External_SWIG.cmake — irrelevant when we
  build against Fedora's system SWIG. Reinstate WRAP_R=ON when
  Fedora's swig backports the fix or SimpleITK 2.5.6 finds a
  system-SWIG-compatible workaround. Drop the R-SimpleITK subpackage
  and the R install glue for now.

* Mon May 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.5-1
- Update to SimpleITK 2.5.5 (upstream 2026-05-13)
- Enable WRAP_R=ON: SimpleITK 2.5.5 includes the R 4.6.0 API-removal fixes
  (PR #2585 R CLOENV, PR #2587 SWIG superbuild patch) needed against
  Fedora 44's R 4.6.0
- Add R-SimpleITK subpackage with R bindings installed under
  %%{_libdir}/R/library/SimpleITK
- Require InsightToolkit5 5.4.6 (upstream 2026-05-01, GDCM CVE-2026-3650)

* Sun Mar 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.3-2
- Add lua BuildRequires: needed for filter source code generation

* Sun Mar 15 2026 Morgan Hough <morgan.hough@gmail.com> - 2.5.3-1
- Initial package for SimpleITK 2.5.3
- Python 3 bindings via SWIG
- Requires ITK 5.4.5 with SimpleITKFilters and LabelErodeDilate modules
