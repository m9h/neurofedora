Name:           opentopas
Version:        4.2.2
Release:        1%{?dist}
Summary:        Monte Carlo tool for particle simulation
License:        MIT
URL:            https://github.com/OpenTOPAS/OpenTOPAS
Source0:        https://github.com/OpenTOPAS/OpenTOPAS/archive/refs/tags/v%{version}.tar.gz#/OpenTOPAS-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  geant4-devel >= 11.3.2
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qt3d-devel
BuildRequires:  gdcm-devel
BuildRequires:  expat-devel
BuildRequires:  xerces-c-devel
BuildRequires:  zlib-devel
BuildRequires:  libX11-devel
BuildRequires:  libXmu-devel
BuildRequires:  libXpm-devel
BuildRequires:  libXft-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLU-devel

Requires:       geant4 >= 11.3.2
Requires:       gdcm
Requires:       qt6-qtbase

%description
OpenTOPAS is a Monte Carlo tool for particle simulation, designed for
medical physics applications. It wraps the Geant4 Simulation Toolkit
to provide an easier-to-use interface for complex simulations.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       geant4-devel
Requires:       gdcm-devel

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.
%prep
%setup -q -n OpenTOPAS-%{version}

%build
%cmake \
    -DGeant4_DIR=%{_libdir}/Geant4-11.4.0/ \
    -DTOPAS_USE_SYSTEM_GDCM=ON \
    -DTOPAS_USE_QT6=ON \
    -DBUILD_SHARED_LIBS=OFF \
    -DTOPAS_INSTALL_EXAMPLES=OFF \


%cmake_build

%install
%cmake_install

# --- Fix Library Locations and Cleanup ---
# OpenTOPAS installs libraries to /usr/lib by default, ignoring -DLIB_INSTALL_DIR on some paths.
# We must move static libs to %{_libdir} (e.g. /usr/lib64) and remove bundled shared libs.

# 1. Move static libraries (.a) to the correct libdir if they ended up in /usr/lib
if [ "%{_prefix}/lib" != "%{_libdir}" ] && [ -d %{buildroot}%{_prefix}/lib ]; then
    mkdir -p %{buildroot}%{_libdir}
    mv %{buildroot}%{_prefix}/lib/*.a %{buildroot}%{_libdir}/ 2>/dev/null || :
fi

# 3. Cleanup artifacts
# Remove internal CMakeLists.txt that gets installed
rm -f %{buildroot}%{_prefix}/CMakeLists.txt

# Remove system hmac files that might have been copied/bundled
rm -f %{buildroot}%{_libdir}/.lib*.hmac
rm -f %{buildroot}%{_prefix}/lib/.lib*.hmac

# 4. Cleanup Bundled System Libraries (.so) in %{_prefix}/lib as well
rm -f %{buildroot}%{_prefix}/lib/*.so*

# 5. Cleanup Bundled System Static Libraries (.a)
# OpenTOPAS accidentally bundles glibc/system static libs. We must verify and remove them.
# We whitelist known OpenTOPAS libs or blacklist system ones. Blacklist is safer for now.
# System libs to remove: libanl.a, libc_nonshared.a, libdl.a, libg.a, libmcheck.a, libpthread.a, librt.a, libutil.a, libsysprof-capture-4.a
for lib in libanl.a libc_nonshared.a libdl.a libg.a libmcheck.a libpthread.a librt.a libutil.a libsysprof-capture-4.a; do
    rm -f %{buildroot}%{_libdir}/$lib
done

# --- Fix FHS Compliance ---
# OpenTOPAS installs files directly to %{_prefix} (e.g., /usr/LICENSE.txt), which is invalid.

# 1. License (handled by %license macro)
rm -f %{buildroot}%{_prefix}/LICENSE.txt

# 2. Move SDK/Data files to %{_datadir}/opentopas
mkdir -p %{buildroot}%{_datadir}/opentopas
mv %{buildroot}%{_prefix}/topas.cc %{buildroot}%{_datadir}/opentopas/
mv %{buildroot}%{_prefix}/CMakeHandleExtensions.cmake %{buildroot}%{_datadir}/opentopas/
mv %{buildroot}%{_prefix}/rundemos.csh %{buildroot}%{_datadir}/opentopas/
mv %{buildroot}%{_prefix}/extensions %{buildroot}%{_datadir}/opentopas/

# Fix permissions
chmod +x %{buildroot}%{_datadir}/opentopas/rundemos.csh

# 3. Move Headers to namespace directory
mkdir -p %{buildroot}%{_includedir}/opentopas
mv %{buildroot}%{_includedir}/*.hh %{buildroot}%{_includedir}/opentopas/
mv %{buildroot}%{_includedir}/*.icc %{buildroot}%{_includedir}/opentopas/
mv %{buildroot}%{_includedir}/TsTopasConfig.hh %{buildroot}%{_includedir}/opentopas/ 2>/dev/null || :

# 4. Remove unwanted artifacts
# Remove cmake install manifest if present? often fine.
# We disabled examples via cmake flag, verify they are gone.
rm -rf %{buildroot}%{_prefix}/examples


%files
%license LICENSE.txt
%doc README.md
%{_bindir}/topas
%{_datadir}/opentopas/

%files devel
%{_includedir}/opentopas/
%{_libdir}/*.a

%changelog
* Mon Feb 02 2026 Antigravity <antigravity@example.com> - 4.2.2-1
- Initial package for OpenTOPAS 4.2.2

