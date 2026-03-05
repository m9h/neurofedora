%define debug_package %{nil}

Name:           babelbrain
Version:        0.8.1
Release:        3%{?dist}
Summary:        GUI for modeling transcranial ultrasound neuromodulation

License:        BSD-3-Clause
URL:            https://github.com/ProteusMRIgHIFU/BabelBrain
Source0:        https://github.com/ProteusMRIgHIFU/BabelBrain/archive/main.tar.gz#/BabelBrain-main.tar.gz

BuildRequires:  python3-devel
BuildRequires:  python3-hatchling
BuildRequires:  python3-pip
BuildRequires:  chrpath
# Add runtime deps here if needed for tests or byte-compilation checks
# BuildRequires:  python3-babelviscofdtd

Requires:       python3-babelviscofdtd
Requires:       python3-pyside6
Requires:       python3-h5py
Requires:       python3-hdf5plugin
Requires:       python3-pydicom
Requires:       python3-nibabel
Requires:       python3-pyvista
Requires:       python3-vtk
Requires:       python3-numba
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-matplotlib
Requires:       python3-pandas
Requires:       python3-scikit-image
Requires:       python3-pyopencl
Requires:       python3-pymupdf
# Requires:       python3-pymeshfix # Might not be in Fedora
Requires:       python3-trimesh
# Requires:       python3-manifold3d # Might not be in Fedora
Requires:       python3-numpy-stl
# Requires:       python3-pwlf # Might not be in Fedora
Requires:       python3-superqt
Requires:       python3-simpleitk
# Requires:       python3-histoprint # Might not be in Fedora
# Requires:       python3-linetimer # Might not be in Fedora
Requires:       python3-xmltodict
Requires:       python3-openpyxl
Requires:       python3-et_xmlfile
Requires:       python3-networkx
Requires:       python3-scooby
Requires:       python3-platformdirs
Requires:       python3-packaging
Requires:       python3-click
Requires:       python3-requests
Requires:       python3-pillow
Requires:       python3-pywavelets

%description
Plymouth's TUS Planning Toolbox (BabelBrain).
BabelBrain is a graphical user interface aimed to simplify the planning of
Transcranial Focused Ultrasound (TUS) procedures.

%prep
%autosetup -n BabelBrain-main

# Generate pyproject.toml since it is missing in the source
cat > pyproject.toml <<EOF
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "BabelBrain"
version = "%{version}"
description = "GUI for modeling transcranial ultrasound neuromodulation"
authors = [{name = "BabelBrain Developers"}]
license = {text = "BSD-3-Clause"}
dependencies = [
    "babelviscofdtd",
    "pyside6",
    "h5py",
    "hdf5plugin",
    "pydicom",
    "nibabel",
    "pyvista",
    "vtk",
    "numba",
    "numpy",
    "scipy",
    "matplotlib",
    "pandas",
    "scikit-image",
    "pyopencl",
    "pymupdf",
    "trimesh",
    "numpy-stl",
    "superqt",
    "simpleitk",
    "xmltodict",
    "openpyxl",
    "et_xmlfile",
    "networkx",
    "scooby",
    "platformdirs",
    "packaging",
    "click",
    "requests",
    "pillow",
    "pywavelets",
]

[tool.hatch.build.targets.wheel]
packages = ["BabelBrain"]
EOF

%build
%pyproject_wheel

%install
%pyproject_install

# Access via wrapper script due to missing entry point/init
mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/babelbrain <<EOF
#!/bin/bash
export PYTHONPATH="%{python3_sitelib}"
exec %{__python3} %{python3_sitelib}/BabelBrain/BabelBrain.py "\$@"
EOF
chmod +x %{buildroot}%{_bindir}/babelbrain

# Fix invalid RPATHs in bundled binaries
chrpath -d %{buildroot}%{python3_sitelib}/BabelBrain/ExternalBin/elastix/linux/bin/elastix
chrpath -d %{buildroot}%{python3_sitelib}/BabelBrain/ExternalBin/elastix/linux/bin/transformix
chrpath -d %{buildroot}%{python3_sitelib}/BabelBrain/ExternalBin/elastix/linux/lib/*.so*

# Fix script permissions
chmod +x %{buildroot}%{python3_sitelib}/BabelBrain/CreateVoxelMask.py
chmod +x %{buildroot}%{python3_sitelib}/BabelBrain/ExternalBin/*/run_linux.sh

# Remove Mac/Windows specific scripts to clean up package
rm -f %{buildroot}%{python3_sitelib}/BabelBrain/ExternalBin/*/run_mac.sh
rm -f %{buildroot}%{python3_sitelib}/BabelBrain/ExternalBin/*/run_mac_transformix.sh

%files
%license LICENSE
%doc README.md
%{_bindir}/babelbrain
%{python3_sitelib}/BabelBrain
%{python3_sitelib}/babelbrain-%{version}.dist-info

%changelog
* Sun Feb 01 2026 Morgan Hough <morgan.hough@gmail.com> - 0.8.1-3
- Fix package summary length and spelling issues

* Sun Feb 01 2026 Morgan Hough <morgan.hough@gmail.com> - 0.8.1-2
- Fix script permissions and clean up non-Linux scripts
- Fix RPATHs for bundled elastix binaries
- Disable debuginfo generation for bundled binaries

* Sun Feb 01 2026 Morgan Hough <morgan.hough@gmail.com> - 0.8.1-1
- Initial package
