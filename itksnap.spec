%global snap_ver 4.4.0-beta2

# Pinned submodule commits for v4.4.0-beta2
%global c3d_commit        d4d963629d7dfdca4b0607907f0e91827c22ea2a
%global greedy_commit     2d5dfa1891ac726524495d4ca8a3461be86c12f5
%global digestible_commit 1b66709e99c43d280bb472e1a0e36185ef2ea412

# No shared libs installed (BUILD_SHARED_LIBS=OFF); suppress empty debug pkg
%define debug_package %{nil}

Name:           itksnap
Version:        4.4.0~beta2
Release:        0.5%{?dist}
Summary:        Medical image segmentation tool for 3D/4D biomedical images

License:        GPL-3.0-or-later
URL:            http://www.itksnap.org

# Main source — GitHub does not include submodules in the tarball; they are
# handled separately below via Sources 1-3.
Source0:        https://github.com/pyushkevich/itksnap/archive/refs/tags/v%{snap_ver}.tar.gz#/itksnap-%{snap_ver}.tar.gz
Source1:        https://github.com/pyushkevich/c3d/archive/%{c3d_commit}/c3d-%{c3d_commit}.tar.gz
Source2:        https://github.com/pyushkevich/greedy/archive/%{greedy_commit}/greedy-%{greedy_commit}.tar.gz
Source3:        https://github.com/pyushkevich/digestible/archive/%{digestible_commit}/digestible-%{digestible_commit}.tar.gz

BuildRequires:  cmake >= 3.16
BuildRequires:  ninja-build
BuildRequires:  gcc-c++

# ITK 5.4+ from our COPR; installed to non-standard suffix path so ITK_DIR is
# set explicitly in %%build.
BuildRequires:  InsightToolkit5-devel

# VTK 9.3.1+ required; Fedora ships 9.2.6 so this comes from our COPR.
BuildRequires:  vtk-devel

# Qt6 — use cmake() virtual BRs so RPM pulls the right subpackage automatically
BuildRequires:  cmake(Qt6Widgets)
BuildRequires:  cmake(Qt6OpenGL)
BuildRequires:  cmake(Qt6OpenGLWidgets)
BuildRequires:  cmake(Qt6Concurrent)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  cmake(Qt6LinguistTools)

# Networking (libssh is REQUIRED; CURL is optional but requested by upstream)
BuildRequires:  libssh-devel
BuildRequires:  libcurl-devel

# FFTW3 — used by the Greedy registration submodule
BuildRequires:  fftw-devel

# OpenGL / X11
BuildRequires:  mesa-libGL-devel
BuildRequires:  libX11-devel

# VTK transitive dependencies: VTK's cmake config propagates these as required
# link targets (nlohmann_json::nlohmann_json, Freetype::Freetype, JsonCpp::JsonCpp,
# etc.) so they must be present in any chroot that builds against vtk-devel.
BuildRequires:  json-devel
BuildRequires:  freetype-devel
BuildRequires:  jsoncpp-devel
BuildRequires:  utf8cpp-devel
BuildRequires:  PEGTL-devel
BuildRequires:  lz4-devel
BuildRequires:  double-conversion-devel

Requires:       hicolor-icon-theme

%description
ITK-SNAP is a software application used to segment structures in 3D and 4D
biomedical images such as MRI, CT, and PET scans.  It provides:

  * Semi-automatic segmentation using active contour methods
  * AI-assisted segmentation (nnInteractive: point, scribble, lasso modes)
  * Manual delineation and label editing tools
  * High-performance OpenGL2-based 2D slice rendering
  * External 3D/4D mesh visualization

This package also includes the Convert3D (c3d) command-line image conversion
tool and the Greedy diffeomorphic image registration tool, both of which are
built as subprojects alongside ITK-SNAP.


%prep
%setup -q -n itksnap-%{itksnap_commit}

# Populate git submodule directories from the pinned tarballs.
# The upstream CMakeLists hard-codes ADD_SUBDIRECTORY into Submodules/{c3d,greedy};
# both directories must exist and contain the unpacked source.
tar -xf %{SOURCE1} -C Submodules/c3d         --strip-components=1
tar -xf %{SOURCE2} -C Submodules/greedy      --strip-components=1
tar -xf %{SOURCE3} -C Submodules/digestible  --strip-components=1

# get_git_commit_date() fails when building from a tarball (SNAP_VERSION_GIT_BRANCH
# is empty, making the call have only 1 argument instead of 2). Set timestamp directly.
sed -i 's|get_git_commit_date.*SNAP_VERSION_GIT_TIMESTAMP.*|set(SNAP_VERSION_GIT_TIMESTAMP "")|' CMakeLists.txt


%build
# C++17 is required; -include cstdint guards against GCC 15 missing-header errors
# seen in ITK-internal headers on Fedora 43+.
export CXXFLAGS="%{optflags} -std=c++17 -include cstdint"

%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    \
    -DITK_DIR=%{_prefix}/lib/cmake/ITK-5.4 \
    \
    -DBUILD_SHARED_LIBS=OFF \
    -DSNAP_USE_GPU=OFF \
    -DSNAP_USE_OSMESA=OFF \
    -DSNAP_USE_IWYU=OFF \
    \
    -DCMAKE_SKIP_INSTALL_RPATH=ON

%cmake_build


%install
%cmake_install

# qt.conf is written by qt_generate_deploy_app_script(); not needed for a
# system-installed Qt application where plugins are found via standard paths.
rm -f %{buildroot}%{_bindir}/qt.conf


%files
%license COPYING

# Main application — the forwarding wrapper and the real binary
%{_bindir}/itksnap
%{_prefix}/lib/snap-4.4.0/ITK-SNAP

# Workspace tool (CLI for managing ITK-SNAP workspaces)
%{_bindir}/itksnap-wt

# Convert3D CLI tools (from c3d submodule)
%{_bindir}/c2d
%{_bindir}/c3d
%{_bindir}/c3d_affine_tool
%{_bindir}/c4d

# Greedy registration tools (from greedy submodule)
%{_bindir}/greedy
%{_bindir}/greedy_propagation
%{_bindir}/greedy_template_average
%{_bindir}/multi_chunk_greedy


%changelog
* Wed May 20 2026 Morgan Hough <morgan@hough.dev> - 4.4.0~beta2-0.6
- Rebuild against InsightToolkit5 5.4.6 (the -0.5 RPM was built against
  5.4.5 on 2026-05-02 and segfaults at startup against a system with
  ITK 5.4.6 installed: libjsoncpp.so.26's static initializer crashes
  during dl_init for the ITK-SNAP binary, presumably due to ABI drift
  in a VTK/ITK transitive that pulled in jsoncpp differently between
  the build chroot then and the user system now).
- Bump InsightToolkit5-devel BR to >= 5.4.6.

* Mon May 04 2026 Morgan Hough <morgan@hough.dev> - 4.4.0-1
- Update to stable 4.4.0 release (September 9, 2025)

* Sun Mar 01 2026 Morgan Hough <morgan@hough.dev> - 4.4.0~beta2-0.5
- Remove qt.conf from /usr/bin (Qt deploy artifact, not needed for system install)

* Sun Mar 01 2026 Morgan Hough <morgan@hough.dev> - 4.4.0~beta2-0.4
- Fix file list: add itksnap-wt, greedy_template_average, multi_chunk_greedy,
  greedy_propagation; add forwarding binary at /usr/lib/snap-*/ITK-SNAP and
  qt.conf; remove nonexistent /usr/share/itksnap directory

* Fri Feb 27 2026 Morgan Hough <morgan@hough.dev> - 4.4.0~beta2-0.3
- Add VTK transitive BuildRequires: json-devel, freetype-devel, jsoncpp-devel,
  utf8cpp-devel, PEGTL-devel, lz4-devel, double-conversion-devel; VTK cmake
  config propagates these as required link targets into downstream builds

* Fri Feb 27 2026 Morgan Hough <morgan@hough.dev> - 4.4.0~beta2-0.2
- Patch CMakeLists.txt in prep: replace get_git_commit_date() with set() to
  avoid CMake error when building from a tarball with no git history

* Wed Feb 25 2026 Morgan Hough <morgan@hough.dev> - 4.4.0~beta2-0.1
- Initial spec for ITK-SNAP 4.4.0-beta2
- Bundles c3d and greedy as CMake subprojects per upstream design
- Requires VTK >= 9.3.1 and ITK 5.4 from mhough/neurofedora COPR
