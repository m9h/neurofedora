%global _lto_cflags %{nil}
# ANTs instantiates ITK templates across 2D/3D/4D; each g++ process peaks at ~3 GB.
# Limit parallelism so the build stays within COPR worker memory (typically 16 GB).
%global _smp_mflags -j4
# Use 'define' not 'global' for debug_package: EPEL 9 auto-injects the debuginfo
# package stanza during spec parsing and 'global' scope causes a conflict.
%define debug_package %{nil}

Name:           ANTs
Version:        2.6.5
Release:        11%{?dist}
Summary:        Advanced Normalization Tools for medical imaging

License:        Apache-2.0
URL:            https://github.com/ANTsX/ANTs
Source0:        https://github.com/ANTsX/ANTs/archive/v%{version}/%{name}-%{version}.tar.gz

Conflicts:      ants
BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.16
BuildRequires:  make
BuildRequires:  zlib-devel
BuildRequires:  InsightToolkit5-devel >= 5.4.6
# These are transitive deps re-found by ITK's module cmake files (ITKHDF5.cmake, ITKMINC.cmake, etc.)
# when a downstream project does include(${ITK_USE_FILE}).
BuildRequires:  hdf5-devel
%if 0%{?fedora}
BuildRequires:  libminc-devel
%endif

%description
Advanced Normalization Tools (ANTs) extracts information from complex datasets
that include imaging. ANTs computes high-dimensional mappings to capture the
statistics of brain structure and function.

%prep
%autosetup -n %{name}-%{version}
# antsUtilities lacks SOVERSION in upstream cmake; add it so the installed
# libantsUtilities.so.1 has a valid versioned SONAME (Fedora packaging requirement).
sed -i '/^target_link_libraries(antsUtilities/a set_target_properties(antsUtilities PROPERTIES SOVERSION 1)' \
    Examples/CMakeLists.txt

%build
# C++17 required by ITK 5.x; permissive mode for older ANTs code on GCC 14+
export CXXFLAGS="%{optflags} -std=c++17 -fpermissive -Wno-error=incompatible-pointer-types"
export CFLAGS="%{optflags} -std=gnu17 -Wno-error=implicit-function-declaration -Wno-error=int-conversion -Wno-error=incompatible-pointer-types"

# Build ANTs directly against system InsightToolkit5 — no superbuild network downloads.
# ANTs_SUPERBUILD=OFF: skip the ExternalProject wrapper and configure ANTs directly.
# ITK_DIR points to the versioned cmake config installed by InsightToolkit5-devel.
%cmake \
    -DANTS_SUPERBUILD=OFF \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DUSE_SYSTEM_ITK:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DCMAKE_CXX_STANDARD:STRING=17 \
    -DCMAKE_CXX_STANDARD_REQUIRED:BOOL=ON \
    -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix} \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON

%cmake_build

%install
%cmake_install
# Remove static archives: ANTs' internal l_* libraries are not a public API
find %{buildroot}%{_libdir} -name '*.a' -delete
# Remove unversioned .so symlinks (devel-file-in-non-devel-package rpmlint warning).
# These are internal implementation libraries, not a public development API.
find %{buildroot}%{_libdir} -maxdepth 1 -name '*.so' -type l -delete

# Install ALL upstream Scripts/ -- ANTS.cmake only ships ~21 curated wrappers
# to /usr/bin (see install(PROGRAMS Scripts/...) block). The remaining
# ~43 utility/example scripts (buildtemplateparallel.sh, multi_template_*.sh,
# the cbf_*.R batch scripts, the waitForXgridJobs.pl helpers, etc.) ship to
# %%{_datadir}/ANTs/scripts/ so users can find and use them.
# NB: %%cmake_install above already populated /usr/bin/ with the curated set.
mkdir -p %{buildroot}%{_datadir}/ANTs/scripts
cp -p Scripts/* %{buildroot}%{_datadir}/ANTs/scripts/
for f in %{buildroot}%{_bindir}/*; do
    rm -f "%{buildroot}%{_datadir}/ANTs/scripts/$(basename "$f")"
done
# Permissions: .sh/.pl/utility scripts executable; .R aren't
chmod 0755 %{buildroot}%{_datadir}/ANTs/scripts/*.sh \
           %{buildroot}%{_datadir}/ANTs/scripts/*.pl 2>/dev/null || :
chmod 0644 %{buildroot}%{_datadir}/ANTs/scripts/*.R 2>/dev/null || :

%ldconfig_scriptlets

%files
%license COPYING.txt
%doc README.md CONTRIBUTING.md
%{_bindir}/*
%{_libdir}/libantsUtilities.so.*
%{_libdir}/libl_*.so.*
%dir %{_datadir}/ANTs
%{_datadir}/ANTs/scripts/

%changelog
* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-11
- Re-apply ALL-scripts install + Documentation/code_of_conduct.md docs.
  Skipping bogus -10 release (its `%%cmake_install` literal in a comment was
  macro-expanded by RPM and run as a stray shell command, crashing %install).
- Comment now uses `%%cmake_install` (escaped) and explicit double-quotes
  in the rm-loop to prevent any future filename surprises.

* Mon May 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-9
- Rebuild against InsightToolkit5 5.4.6 (GDCM CVE-2026-3650, F44 target)
- Bump BuildRequires: InsightToolkit5-devel >= 5.4.6

* Fri Feb 27 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-8
- Rewrite changelog entries to remove RPM directive names (install, prep, files);
  EPEL 9 rpmbuild treats these as spec directives, causing "second install" error

* Thu Feb 26 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-7
- Add debug_package suppression via define scope to fix EPEL 9 SRPM rebuild

* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-6
- Patch Examples/CMakeLists.txt in prep to add SOVERSION 1 to antsUtilities:
  fixes rpmlint E: invalid-soname (library installed with unversioned SONAME)
- Delete unversioned .so symlinks in install step: resolves devel-file-in-non-devel-package
  warnings; l_* and antsUtilities are internal libraries, not a public API

* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-5
- Add l_* and libantsUtilities shared libs to files list (required at runtime by ANTs
  binaries; each binary wraps its corresponding l_*.so entry point)
- Add ldconfig scriptlets for proper shared library management

* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-4
- Add -DCMAKE_SKIP_INSTALL_RPATH=ON: ANTs binaries embed /usr/lib64 RPATH which
  is a standard system path; brp-check-rpaths treats this as a fatal error

* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-3
- Add -DUSE_SYSTEM_ITK=ON: without this, ANTS.cmake's staging/lib64 install rule
  triggers even with SUPERBUILD=OFF (condition guards on NOT USE_SYSTEM_ITK),
  causing cmake install to fail when staging dir was never populated by superbuild

* Tue Feb 24 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-2
- Limit parallel build jobs to -j4: each ITK template g++ process peaks at ~3 GB;
  16-way parallelism OOMs even on 32 GB hosts and would fail on COPR 16 GB workers

* Mon Feb 23 2026 Morgan Hough <morgan.hough@gmail.com> - 2.6.5-1
- Upgrade to ANTs 2.6.5
- Switch to direct build against system InsightToolkit5-devel (ANTs_SUPERBUILD=OFF)
- Remove git BuildRequires (no longer downloading ITK at build time)
- Add InsightToolkit5-devel BuildRequires
- Use standard cmake/cmake_build/cmake_install RPM macros

* Sun Jan 04 2026 mhough - 2.5.4-1
- Switched to SuperBuild due to incompatible system ITK v4
- Added C++17 and C17 flags for GCC 15 compatibility
- Added memory constraints for build stability
