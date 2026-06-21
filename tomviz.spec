%global debug_package %{nil}

Name:           tomviz
Version:        2.3.1
Release:        1%{?dist}
Summary:        3D visualization and analysis of tomography data

License:        BSD-3-Clause
URL:            https://tomviz.org/
Source0:        https://github.com/OpenChemistry/tomviz/archive/refs/tags/%{version}.tar.gz#/tomviz-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  gcc
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  chrpath
BuildRequires:  desktop-file-utils
# ParaView-based GUI (its SDK pulls Qt6 + the Qt6 help module)
BuildRequires:  paraview-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qt5compat-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  InsightToolkit5-devel
BuildRequires:  vtk-devel
BuildRequires:  protobuf-devel
BuildRequires:  protobuf-compiler
BuildRequires:  tbb-devel
BuildRequires:  python3-devel
BuildRequires:  pybind11-devel

Requires:       paraview
Requires:       python3-vtk
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-h5py

%description
Tomviz is a cross-platform, open-source application (SCI/Kitware/OpenChemistry)
for the processing, visualization and analysis of 3D tomographic data, widely
used in materials science and electron microscopy. It provides a ParaView-based
pipeline GUI with a Python operator framework for reconstruction, segmentation
and quantification of volumetric datasets.

%prep
%autosetup -n tomviz-%{version}

# Unbundle pybind11 (git submodule, absent from the release archive) -> use
# Fedora's pybind11-devel, which provides pybind11_add_module().
sed -i 's|add_subdirectory(${PROJECT_SOURCE_DIR}/thirdparty/pybind11)|find_package(pybind11 CONFIG REQUIRED)|' CMakeLists.txt

%build
cmake -S . -B cbuild -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DParaView_DIR=%{_libdir}/cmake/paraview \
    -DITK_DIR=%{_libdir}/cmake/ITK-5.4 \
    -DCMAKE_PREFIX_PATH=%{_prefix}
%cmake_build -C cbuild 2>/dev/null || cmake --build cbuild %{?_smp_mflags}

%install
DESTDIR=%{buildroot} cmake --install cbuild

# tomviz links ParaView's private libdir; keep that on the RPATH, drop the leak.
chrpath -r '%{_libdir}/paraview' %{buildroot}%{_bindir}/tomviz 2>/dev/null || :

# Static convenience lib is not needed at runtime.
rm -f %{buildroot}%{_libdir}/libtomviz.a

# Desktop entry + icon (upstream does not install XDG files on Linux).
install -D -m 0644 tomviz/icons/tomviz.png \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/tomviz.png
cat > %{name}.desktop <<EOF
[Desktop Entry]
Name=Tomviz
Comment=3D visualization and analysis of tomography data
Exec=tomviz
Icon=tomviz
Terminal=false
Type=Application
Categories=Science;Education;DataVisualization;
EOF
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{name}.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/tomviz
%{_libdir}/libtomvizcore.so
%{python3_sitearch}/tomviz/
%{_datadir}/tomviz/
%{_datadir}/applications/tomviz.desktop
%{_datadir}/icons/hicolor/256x256/apps/tomviz.png

%changelog
* Sat Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 2.3.1-1
- Initial package: Tomviz 2.3.1, the ParaView-based 3D tomography visualization
  and analysis GUI (materials science / electron microscopy). Net-new to Fedora;
  built against the system ParaView/ITK/VTK/Qt6, pybind11 unbundled.
