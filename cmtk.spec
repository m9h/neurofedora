Name:           cmtk
Version:        3.4.0
Release:        4%{?dist}
Summary:        Computational Morphometry Toolkit

# The core is GPLv3+, but it bundles/links against other licensed code
# NrrdIO: LGPLv2.1+, alglib: GPLv2+, dcmtk: BSD-3-Clause, mxml: LGPLv2 with exceptions, 
# numdiff: GPLv3+, sqlite3: Public Domain (SQLite)
License:        GPL-3.0-or-later AND LGPL-2.1-or-later AND BSD-3-Clause AND MIT AND SQLite
URL:            https://www.nitrc.org/projects/cmtk/
# Using GitHub mirror for source as NITRC is hard to automate
%global commit  ae983a9cdb1eae603ffa49695d514989366dbe12
%global shortcommit %(c=%{commit}; echo ${c:0:7})
Source0:        https://github.com/jefferis/cmtk/archive/%{commit}/%{name}-%{version}-git%{shortcommit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  fftw-devel
BuildRequires:  mxml-devel
# dcmtk-devel causes API compatibility issues with current CMTK 3.4.0
# BuildRequires:  dcmtk-devel
BuildRequires:  sqlite-devel
BuildRequires:  zlib-devel
BuildRequires:  bzip2-devel
BuildRequires:  libpng-devel
BuildRequires:  libtiff-devel
BuildRequires:  libX11-devel
# For parallel processing
BuildRequires:  gcc-gfortran

# Skip RPATH checks because CMTK sets them for its binaries and we want to avoid issues with standard paths
%global __brp_check_rpaths %{nil}

%description
CMTK is a software toolkit for computational morphometry. It includes
many command-line tools for image registration (affine and non-rigid),
image analysis, and processing.

%package devel
Summary:        Development files for CMTK
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -n %{name}-%{commit}

# Fix conflict with std::byte in C++17/20
# Rename CMTK's 'byte' to 'cmtk_byte'
grep -rle "\bbyte\b" core | xargs sed -i 's/\bbyte\b/cmtk_byte/g'

# cmake 4.x removed EXPORT_LIBRARY_DEPENDENCIES (deprecated in 3.0, gone in 4.0)
sed -i '/EXPORT_LIBRARY_DEPENDENCIES/d' core/CMakeLists.txt
# Also remove the install of the now-non-existent CMTKLibraryDepends.cmake
sed -i '/CMTKLibraryDepends.cmake/d' core/CMakeLists.txt

# cmake 4.x removed CMP0005; bundled numdiff sets it to OLD which now errors
sed -i '/cmake_policy(SET CMP0005 OLD)/d' core/Utilities/numdiff-5.2.1/CMakeLists.txt

# Disable bundled numdiff entirely — its C sources (errors.c, new.c) FTBFS
# on GCC 16 (stricter ISO C parser, macro expansion errors). numdiff is a
# test utility CMTK itself doesn't link against, so dropping the subdir is safe.
sed -i '/ADD_SUBDIRECTORY[[:space:]]*(numdiff/Id; /add_subdirectory[[:space:]]*(numdiff/Id' \
    core/Utilities/CMakeLists.txt 2>/dev/null || true

%build
cd core
%cmake \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DBUILD_SHARED_LIBS=ON \
    -DCMAKE_SKIP_RPATH=ON \
    -DCMTK_INSTALL_BIN_DIR=bin \
    -DCMTK_INSTALL_LIB_DIR=%{_lib}/cmtk \
    -DCMTK_BUILD_DCMTK=ON \
    -DCMTK_BUILD_MXML=OFF \
    -DCMTK_BUILD_SQLITE=OFF \
    -DCMTK_USE_QT=OFF \
    -DCMTK_USE_FFTW=ON
%cmake_build

%install
cd core
%cmake_install

# CMTK installs binaries into %{_libdir}/cmtk/bin
# Move them to %{_bindir}
mkdir -p %{buildroot}%{_bindir}
mv %{buildroot}%{_libdir}/cmtk/bin/* %{buildroot}%{_bindir}/
rmdir %{buildroot}%{_libdir}/cmtk/bin

# Overwrite the 'cmtk' wrapper with a clean version for Fedora
cat > %{buildroot}%{_bindir}/cmtk <<EOF
#!/bin/bash
TOOL_PATH="%{_bindir}"
if [ \$# -lt 1 ]; then
  echo "Usage: cmtk <command> [options]"
  exit 1
fi
COMMAND="\$1"
shift
if [ -x "\${TOOL_PATH}/\${COMMAND}" ]; then
  exec "\${TOOL_PATH}/\${COMMAND}" "\$@"
else
  echo "CMTK command '\${COMMAND}' not found."
  exit 1
fi
EOF
chmod 755 %{buildroot}%{_bindir}/cmtk

%check
# Run a basic tool to verify it works
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}/cmtk
%{buildroot}%{_bindir}/describe --help

%files
%license core/COPYING.txt core/LICENSE core/Licenses/
%doc core/README.txt core/CHANGELOG
%{_bindir}/*
%dir %{_libdir}/cmtk
%{_libdir}/cmtk/*.so
%{_datadir}/cmtk/

%files devel
%{_includedir}/cmtk/
%{_libdir}/cmtk/*.cmake

%changelog
* Sat May 23 2026 Morgan Hough <morgan.hough@gmail.com> - 3.4.0-4
- Disable bundled numdiff subdir: errors.c and new.c FTBFS on GCC 16
  (stricter ISO C parsing rejects the macro expansions). numdiff is a
  test utility CMTK doesn't link against, so the subdir can go.

* Sat May 23 2026 Morgan Hough <morgan.hough@gmail.com> - 3.4.0-3
- Remove cmake 4.x dead commands (policy floor isn't enough):
  - EXPORT_LIBRARY_DEPENDENCIES + CMTKLibraryDepends install in core/CMakeLists.txt:698
  - cmake_policy(SET CMP0005 OLD) in bundled numdiff (CMP0005 was removed)

* Sat May 23 2026 Morgan Hough <morgan.hough@gmail.com> - 3.4.0-2
- Add -DCMAKE_POLICY_VERSION_MINIMUM=3.5 for cmake 4.x compatibility (F44+)

* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 3.4.0-1
- Initial CMTK package
- Updated licenses and installation paths
