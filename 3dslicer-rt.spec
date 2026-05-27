# SlicerRT — Radiation Therapy extension for 3D Slicer.
# Provides DICOM-RT import/export, dose volume histograms, contour
# operations, and supports treatment planning workflows.
#
# Large extension (C++ modules); among the most-installed Slicer
# extensions in oncology research labs.

%global commit       cba32f11
%global longcommit   cba32f1100000000000000000000000000000000
%global snapdate     20260515

Name:           3dslicer-rt
Version:        0
Release:        0.1.%{snapdate}git%{commit}%{?dist}
Summary:        Radiation Therapy extension for 3D Slicer

License:        BSD-3-Clause
URL:            https://github.com/SlicerRt/SlicerRt
Source0:        %{url}/archive/%{commit}/SlicerRt-%{commit}.tar.gz

BuildRequires:  cmake >= 3.20
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  3dslicer-devel >= 5.10.0
BuildRequires:  InsightToolkit5-devel >= 5.4.6
BuildRequires:  vtk-devel >= 9.6
BuildRequires:  dcmtk-devel
# plastimatch — for ABAS-style registration; we already package plastimatch.
BuildRequires:  plastimatch-devel

Requires:       3dslicer >= 5.10.0
Requires:       plastimatch

%description
SlicerRT extends 3D Slicer with radiation-therapy-specific functionality:

  * DICOM-RT Structure Set, Dose, Plan, Image import/export
  * Dose volume histogram (DVH) computation
  * Contour comparison metrics (Dice, Hausdorff, mean surface distance)
  * Patient hierarchy for multi-modality oncology cases
  * Dose accumulation with deformable registration
  * Beam visualization and dose viewing

Built on the plastimatch library and used widely in academic radiation
oncology and dose research.

%prep
%autosetup -p1 -n SlicerRt-%{longcommit}

%build
%cmake -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING:BOOL=OFF \
    -DSlicer_DIR:PATH=%{_prefix}/lib/slicer-5.10.0/lib/cmake/Slicer \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk \
    -DPLASTIMATCH_DIR:PATH=%{_libdir}/cmake/plastimatch \
    -DCMAKE_SKIP_INSTALL_RPATH:BOOL=ON \
    -DCMAKE_INSTALL_PREFIX:PATH=%{_prefix}/lib/slicer-5.10.0
%cmake_build

%install
%cmake_install

%files
%license License.txt 2>/dev/null || true
%doc README.md
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/qt-loadable-modules/*RT*
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/qt-loadable-modules/*Dose*
%{_prefix}/lib/slicer-5.10.0/lib/Slicer-5.10/cli-modules/*DICOM*RT*
%{_prefix}/lib/slicer-5.10.0/share/Slicer-5.10/qt-loadable-modules/*

%changelog
* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20260515gitcba32f11
- Initial COPR package tracking SlicerRt master.
- Builds against stable 3dslicer-5.10.0 + plastimatch (from this COPR).
