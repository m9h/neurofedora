%define debug_package %{nil}
%global install_dir %{_libdir}/%{name}

Name:           mrtrix3
Version:        3.0.8
Release:        1%{?dist}
Summary:        Advanced Diffusion MRI Processing and Visualisation

License:        MPL-2.0
URL:            https://www.mrtrix.org/
Source0:        https://github.com/MRtrix3/%{name}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  python3
BuildRequires:  python3-devel
BuildRequires:  eigen3-devel
BuildRequires:  zlib-devel
BuildRequires:  fftw-devel
BuildRequires:  libtiff-devel
BuildRequires:  libpng-devel
# Qt5 Dependencies
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLU-devel

Requires:       python3
Requires:       python3-numpy
Requires:       qt5-qtbase
Requires:       qt5-qtsvg
Requires:       mesa-libGL

%description
MRtrix3 provides a set of tools to perform various types of diffusion MRI
analyses, from various forms of tractography through to next-generation
group-level analyses.

%prep
%autosetup

%build
# 1. Fix build scripts to use python3 (Required for Mock/Fedora)
# MRtrix3 defaults to 'python', which doesn't exist in clean Fedora chroots.
sed -i 's|#!/usr/bin/env python|#!/usr/bin/python3|' configure build

# 2. Compiler Flags (CXXFLAGS)
export CXXFLAGS="%{optflags} -g"

# 3. Linker Flags (Map Fedora's LDFLAGS to MRtrix's LINKFLAGS)
export LDFLAGS="%{?__global_ldflags}"
export LINKFLAGS="$LDFLAGS"

# 4. Architecture
export ARCH="native"

# 5. Qt5 Paths
export QMAKE=/usr/bin/qmake-qt5
export MOC=/usr/bin/moc-qt5
export RCC=/usr/bin/rcc-qt5

# 6. Configure (now using python3)
./configure -debug

# 7. Build (now using python3)
./build

%install
mkdir -p %{buildroot}%{install_dir}
mkdir -p %{buildroot}%{_bindir}

# Copy artifacts to private dir
cp -a bin %{buildroot}%{install_dir}/
cp -a lib %{buildroot}%{install_dir}/
cp -a share %{buildroot}%{install_dir}/

# Symlink binaries to /usr/bin
for b in %{buildroot}%{install_dir}/bin/*; do
    binary_name=$(basename "$b")
    # Only symlink if it's not the python binary itself
    if [ "$binary_name" != "python" ]; then
        ln -s %{install_dir}/bin/"$binary_name" %{buildroot}%{_bindir}/"$binary_name"
    fi
done

# --- SHEBANG FIX ---
# Robustly rewrite ALL python shebangs to #!/usr/bin/python3
# We loop through every file in bin/, check if it's a script calling python,
# and forcefully overwrite the first line.
for f in %{buildroot}%{install_dir}/bin/*; do
    if [ -f "$f" ]; then
        # Check if the first line contains "python"
        if head -n 1 "$f" | grep -q "python"; then
            echo "Fixing shebang in $f"
            # Replace the entire first line with #!/usr/bin/python3
            sed -i '1s|^#!.*|#!/usr/bin/python3|' "$f"
        fi
    fi
done

%files
%license LICENCE.txt
%doc README.md
%{install_dir}/
%{_bindir}/*

%changelog
* Sun Jan 04 2026 Morgan Hough <morgan.hough@gmail.com> - 3.0.8-1
- Initial package for MRtrix3 version 3.0.8
