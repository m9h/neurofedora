# SlicerRT — Radiation Therapy extension for 3D Slicer.
# Provides DICOM-RT import/export, dose volume histograms, contour
# operations, and supports treatment planning workflows.
#
# Large extension (C++ modules); among the most-installed Slicer
# extensions in oncology research labs.

%global commit       cba32f11
%global longcommit   cba32f1100000000000000000000000000000000
%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.12

%global snapdate     20260515

Name:           3dslicer-rt
Version:        0
Release:        0.2.%{snapdate}git%{commit}%{?dist}
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
# plastimatch: our package ships the binaries ONLY -- no -devel subpackage and no
# headers at all (`dnf repoquery -l plastimatch | grep /usr/include` is empty), so
# plastimatch-devel is unsatisfiable and was blocking the buildroot. SlicerRT's
# plastimatch-backed registration modules need those headers, so build without
# them for now; packaging plastimatch-devel is a prerequisite for turning them on.
%bcond_with plastimatch

Requires:       3dslicer >= 5.10.0

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
    `# Was %{_prefix}/lib/slicer-5.10.0/lib/cmake/Slicer -- a Slicer 5.10 layout` \
    `# that has not existed since the 5.12 retarget. This spec was written then` \
    `# and never built, so nothing ever caught it.` \
    -DSlicer_DIR:PATH=%{slicer_inst}/lib/%{slicer_subdir} \
    -DITK_DIR:PATH=%{_prefix}/lib/cmake/ITK-5.4 \
    -DVTK_DIR:PATH=%{_libdir}/cmake/vtk \
%if %{with plastimatch}
    -DPLASTIMATCH_DIR:PATH=%{_libdir}/cmake/plastimatch \
%endif
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
* Sun Aug 02 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.2.20260515gitcba32f11
- Point Slicer_DIR at the 5.12 layout (was a Slicer 5.10 path that has not existed
  since the retarget) and drop the unsatisfiable plastimatch-devel BuildRequires --
  our plastimatch package ships binaries only, no headers. Gate PLASTIMATCH_DIR on
  a %%bcond so the plastimatch-backed modules can be turned on once
  plastimatch-devel exists.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20260515gitcba32f11
- Initial COPR package tracking SlicerRt master.
- Builds against stable 3dslicer-5.10.0 + plastimatch (from this COPR).
