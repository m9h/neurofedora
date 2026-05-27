# SlicerDMRI — Diffusion MRI extension for 3D Slicer.
# Provides tractography, tensor analysis, and fiber-bundle visualization.
# Used widely in neuroimaging research.

%global commit       a40200bf
%global longcommit   a40200bf000000000000000000000000000000ff
%global snapdate     20260411

Name:           3dslicer-dmri
Version:        0
Release:        0.1.%{snapdate}git%{commit}%{?dist}
Summary:        Diffusion MRI extension for 3D Slicer

License:        BSD-3-Clause
URL:            https://github.com/SlicerDMRI/SlicerDMRI
Source0:        %{url}/archive/%{commit}/SlicerDMRI-%{commit}.tar.gz

BuildRequires:  cmake >= 3.20
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  3dslicer-devel >= 5.10.0
BuildRequires:  InsightToolkit5-devel >= 5.4.6
BuildRequires:  vtk-devel >= 9.6
BuildRequires:  teem-devel
BuildRequires:  SlicerExecutionModel-devel

Requires:       3dslicer >= 5.10.0

%description
SlicerDMRI is the diffusion MRI extension for 3D Slicer. It provides:

  * Diffusion tensor estimation and visualization (FA, MD, color FA)
  * Whole-brain and ROI-based tractography (deterministic + probabilistic)
  * Fiber bundle clustering and statistics
  * DICOM Diffusion import
  * UKFTractography (Unscented Kalman Filter tractography)

Developed by the Brigham and Women's Hospital / Harvard SPL team and the
SlicerDMRI consortium.

%prep
%autosetup -p1 -n SlicerDMRI-%{longcommit}

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_DIR:PATH=%{_prefix}/lib/slicer-5.10.0/lib/cmake/Slicer \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix}/lib/slicer-5.10.0
%cmake_build

%install
%cmake_install

%files
%license License.txt
%doc README.md
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/qt-loadable-modules/*SlicerDMRI*
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/qt-scripted-modules/*Tract*
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/cli-modules/*UKF*
%{_prefix}/lib/slicer-5.10.0/share/Slicer-5.10/qt-loadable-modules/*

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20260411gita40200bf
- Initial COPR package tracking SlicerDMRI master.
- Builds against stable 3dslicer-5.10.0 (via Slicer_DIR cmake hint).
- Installs into the 3dslicer-5.10.0 install root so the Extension
  Manager / module loader picks it up.
