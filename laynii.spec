Name:           laynii
Version:        2.10.0
Release:        1%{?dist}
Summary:        Suite of C++ programs for layer-fMRI neuroimaging analysis

License:        BSD-3-Clause
URL:            https://github.com/layerfMRI/LAYNII
Source0:        %{url}/archive/v%{version}/LAYNII-%{version}.tar.gz
Patch0:         0001-Fix-missing-cstdint-include-in-idalib.patch

BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  zlib-devel
BuildRequires:  SDL2-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  desktop-file-utils

%description
LayNii is a standalone suite of C++ programs for layer-fMRI (layer-functional
magnetic resonance imaging) analysis. It provides tools for cortical depth
segmentation, layer-specific smoothing, cortical columnar analysis, BOLD
correction for VASO contrast, and cortical patch flattening of MRI
neuroimaging data.

LayNii requires only a C++ compiler and zlib, with no other external
dependencies. It processes NIfTI format neuroimaging files.

%package        ida
Summary:        Interactive display application for layer-fMRI data
Requires:       SDL2
Requires:       mesa-libGL
Provides:       bundled(imgui) = 1.90.1

%description    ida
LayNii IDA (Interactive Display Application) is a high-performance GUI tool
for fast and intuitive interaction with large-scale, ultra-high-resolution MRI
data. It enables real-time visualization of 4D neuroimaging datasets with
interactive slice navigation, voxel-level time course analysis, and
correlation analysis.

Built with Dear ImGui, SDL2, and OpenGL for fluid, responsive visualization.

%prep
%autosetup -n LAYNII-%{version} -p1

# Use Fedora compiler and linker flags instead of hardcoded -O3
sed -i 's|^CFLAGS\t*=.*-std=c++11 -DHAVE_ZLIB|CFLAGS = %{optflags} -std=c++11 -DHAVE_ZLIB|' Makefile
sed -i '/^CFLAGS.*+=.*-O3/d' Makefile
sed -i 's|^LFLAGS\t*=.*|LFLAGS = %{build_ldflags} -lm -lz|' Makefile

# Apply Fedora flags to ida Makefile
sed -i 's|^CXXFLAGS = -std=c++11|CXXFLAGS = %{optflags} -std=c++11|' ida/src/Makefile
sed -i '/^CXXFLAGS += -O3/d' ida/src/Makefile
# Relax format warnings that Fedora's -Werror=format-security promotes to errors
# (upstream uses llu format specifier for uint64_t and empty ImGui format strings)
sed -i '/^CXXFLAGS += -g -Wall -Wformat/s/$/ -Wno-error=format-security -Wno-format-zero-length/' ida/src/Makefile

# Create desktop file
cat > laynii-ida.desktop << 'EOF'
[Desktop Entry]
Name=LayNii IDA
Comment=Interactive display application for layer-fMRI data
Exec=LayNii_IDA
Icon=laynii
Terminal=false
Type=Application
Categories=Science;MedicalSoftware;DataVisualization;
Keywords=fMRI;neuroimaging;MRI;layers;visualization;
EOF

%build
# Build CLI tools
%make_build

# Build IDA GUI application
%make_build -C ida/src LayNii_IDA

%install
# Install CLI tools
mkdir -p %{buildroot}%{_bindir}
for bin in LN_* LN2_*; do
    if [ -f "$bin" ] && [ -x "$bin" ]; then
        install -p -m 0755 "$bin" %{buildroot}%{_bindir}/
    fi
done

# Install IDA
install -p -m 0755 ida/src/LayNii_IDA %{buildroot}%{_bindir}/

# Install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
desktop-file-install --dir=%{buildroot}%{_datadir}/applications laynii-ida.desktop

# Install icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/scalable/apps
install -p -m 0644 visuals/LayNii_logo.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/laynii.svg

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/laynii-ida.desktop

%files
%license LICENSE
%doc README.md CONTRIBUTING.md CITATION.cff
# Layer-fMRI v2 tools
%{_bindir}/LN2_BORDERIZE
%{_bindir}/LN2_CHOLMO
%{_bindir}/LN2_COLUMNS
%{_bindir}/LN2_CONNECTED_CLUSTERS
%{_bindir}/LN2_DESPIKE
%{_bindir}/LN2_DEVEIN
%{_bindir}/LN2_DIRECTIONALITY_BIN
%{_bindir}/LN2_FRISGO
%{_bindir}/LN2_GEODISTANCE
%{_bindir}/LN2_GRADIENTS
%{_bindir}/LN2_GRAMAG
%{_bindir}/LN2_HEXBIN
%{_bindir}/LN2_IFPOINTS
%{_bindir}/LN2_INTPRO
%{_bindir}/LN2_LAPLACIAN
%{_bindir}/LN2_LAYER_SMOOTH
%{_bindir}/LN2_LAYERDIMENSION
%{_bindir}/LN2_LAYERS
%{_bindir}/LN2_MASK
%{_bindir}/LN2_MULTILATERATE
%{_bindir}/LN2_NEIGHBORS
%{_bindir}/LN2_PATCH_FLATTEN
%{_bindir}/LN2_PATCH_FLATTEN_2D
%{_bindir}/LN2_PATCH_UNFLATTEN
%{_bindir}/LN2_PHASE_GRADIENTS
%{_bindir}/LN2_PHASE_JOLT
%{_bindir}/LN2_PHASE_LAPLACIAN
%{_bindir}/LN2_PROFILE
%{_bindir}/LN2_RECIPROCAL
%{_bindir}/LN2_RIM_BORDERIZE
%{_bindir}/LN2_RIM_POLISH
%{_bindir}/LN2_RIMIFY
%{_bindir}/LN2_SENSITIVITY
%{_bindir}/LN2_SNAPCAST
%{_bindir}/LN2_SPECIFICITY
%{_bindir}/LN2_UVD_FILTER
%{_bindir}/LN2_VORONOI
%{_bindir}/LN2_ZERO_CROSSING
%{_bindir}/LN2_ZSCORE
# Legacy tools
%{_bindir}/LN_3DCOLUMNS
%{_bindir}/LN_BOCO
%{_bindir}/LN_COLUMNAR_DIST
%{_bindir}/LN_CONLAY
%{_bindir}/LN_CORREL2FILES
%{_bindir}/LN_DIRECT_SMOOTH
%{_bindir}/LN_EXTREMETR
%{_bindir}/LN_FLOAT_ME
%{_bindir}/LN_GFACTOR
%{_bindir}/LN_GRADSMOOTH
%{_bindir}/LN_GROW_LAYERS
%{_bindir}/LN_IMAGIRO
%{_bindir}/LN_INFO
%{_bindir}/LN_INT_ME
%{_bindir}/LN_INTPRO
%{_bindir}/LN_LAYER_SMOOTH
%{_bindir}/LN_LEAKY_LAYERS
%{_bindir}/LN_LOITUMA
%{_bindir}/LN_MP2RAGE_DNOISE
%{_bindir}/LN_NOISE_KERNEL
%{_bindir}/LN_NOISEME
%{_bindir}/LN_PHYSIO_PARS
%{_bindir}/LN_RAGRUG
%{_bindir}/LN_SHORT_ME
%{_bindir}/LN_SKEW
%{_bindir}/LN_TEMPSMOOTH
%{_bindir}/LN_TRIAL
%{_bindir}/LN_ZOOM

%files ida
%license LICENSE
%{_bindir}/LayNii_IDA
%{_datadir}/applications/laynii-ida.desktop
%{_datadir}/icons/hicolor/scalable/apps/laynii.svg

%changelog
* Sun Mar 29 2026 Morgan Hough <morgan.hough@gmail.com> - 2.10.0-1
- Initial package for Fedora
- Add laynii-ida subpackage with GUI visualization application
