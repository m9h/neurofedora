# FEBioStudio statically links its own module libs into one 22MB binary; debug
# extraction on it is large and not useful for a first packaging.
%global debug_package %{nil}

Name:           febiostudio
Version:        3.1
Release:        1%{?dist}
Summary:        Pre- and post-processor GUI for the FEBio biomechanics solver

License:        MIT
URL:            https://febio.org/
Source0:        https://github.com/febiosoftware/FEBioStudio/archive/refs/tags/v%{version}.tar.gz#/FEBioStudio-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  gcc
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  chrpath
BuildRequires:  desktop-file-utils
# Qt6 GUI (>= 6.5; uses GuiPrivate -> qtbase-private-devel)
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtcharts-devel
BuildRequires:  qt6-qtshadertools-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  glew-devel
# FEBio SDK (find_package(FEBio) -> FEBio::<Module> targets)
BuildRequires:  febio-devel
# Optional features (all from Fedora): MMG remeshing, tetgen, CAD (OCCT+NetGen),
# remote jobs (libssh/openssl), model repository (libzip/sqlite), image analysis
# (SimpleITK), Python scripting (pybind11). FFMPEG is omitted (Fedora's ffmpeg 8
# dropped the avcodec_close API FEBio Studio 3.1 uses).
BuildRequires:  mmg-devel
BuildRequires:  mmg3d-devel
BuildRequires:  mmgs-devel
BuildRequires:  mmg2d-devel
BuildRequires:  tetgen-devel
BuildRequires:  opencascade-devel
BuildRequires:  netgen-mesher-devel
BuildRequires:  libssh-devel
BuildRequires:  openssl-devel
BuildRequires:  libzip-devel
BuildRequires:  sqlite-devel
BuildRequires:  simpleitk-devel
BuildRequires:  pybind11-devel
BuildRequires:  python3-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  libomp-devel

# The FEBio runtime libraries (febiostudio's binary RPATHs %{_libdir}/febio).
Requires:       febio%{?_isa} = 4.12

%description
FEBio Studio is the integrated pre- and post-processing environment for FEBio,
the finite element solver for biomechanics and biophysics from the University of
Utah. It provides interactive model building, meshing, material assignment, job
control and result visualization for FEBio simulations.

This build links the system FEBio solver and enables MMG adaptive remeshing,
TetGen, CAD import/meshing (OpenCASCADE + NetGen), remote job execution over SSH,
the online model repository, SimpleITK image analysis, and Python scripting.
Video (mp4) export is not built (incompatible with the system ffmpeg version).

%prep
%autosetup -n FEBioStudio-%{version}

# Fedora forbids static libstdc++/libgcc; FEBio Studio hardcodes them on Linux.
sed -i 's/ -static-libstdc++//g' CMakeLists.txt
sed -i '/target_link_libraries(FEBioStudio -static-libstdc++ -static-libgcc)/d' CMakeLists.txt

%build
# Raw cmake (FEBio Studio's CMake is sensitive). Qt6 + our FEBio SDK via
# CMAKE_PREFIX_PATH. QT_6_10=ON so it pulls Qt6::GuiPrivate (needed by RHILib).
# MMG/TetGen/SSH/MODEL_REPO/ITK/Python auto-detect ON from the system -devel pkgs;
# CAD needs explicit Fedora paths (OCC 7.9 -> USE_NEW_OCC). FFMPEG off.
cmake -S . -B cbuild -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_PREFIX_PATH=%{_prefix} \
    -DQt6_DIR=%{_libdir}/cmake/Qt6 \
    -DFEBio_DIR=%{_libdir}/cmake/FEBio \
    -DQT_6_10=ON \
    -DUSE_FFMPEG=OFF \
    -DCAD_FEATURES=ON -DUSE_NEW_OCC=ON \
    -DOCCT_INC=%{_includedir}/opencascade -DOCCT_LIB_DIR=%{_libdir} \
    -DNETGEN_INC=%{_includedir}/netgen-mesher -DNETGEN_LIB_DIR=%{_libdir}
cmake --build cbuild %{?_smp_mflags}

%install
install -D -m 0755 cbuild/bin/FEBioStudio %{buildroot}%{_bindir}/FEBioStudio

# Keep only the FEBio runtime libdir on the RPATH (drop the empty build-tree leak).
chrpath -r '%{_libdir}/febio' %{buildroot}%{_bindir}/FEBioStudio

# Desktop entry + icon.
install -D -m 0644 icons/FEBioStudio.png \
    %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/febiostudio.png
cat > %{name}.desktop <<EOF
[Desktop Entry]
Name=FEBio Studio
Comment=Pre/post-processor for the FEBio biomechanics solver
Exec=FEBioStudio
Icon=febiostudio
Terminal=false
Type=Application
Categories=Science;Education;Engineering;
EOF
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{name}.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/FEBioStudio
%{_datadir}/applications/febiostudio.desktop
%{_datadir}/icons/hicolor/256x256/apps/febiostudio.png

%changelog
* Sat Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 3.1-1
- Initial package: FEBio Studio 3.1, the Qt6 GUI pre/post-processor for FEBio.
  Links the system FEBio SDK (febio-devel) and enables MMG, TetGen, CAD
  (OpenCASCADE+NetGen), SSH, model repository, SimpleITK and Python scripting.
  FFMPEG video export omitted (system ffmpeg 8 dropped avcodec_close). Static
  module libs are linked into the binary; static libstdc++/libgcc removed for
  Fedora policy.
