Name:           geant4
Version:        11.4.1
Release:        1%{?dist}
Summary:        Toolkit for the simulation of the passage of particles through matter
License:        Geant4
URL:            https://geant4.web.cern.ch/
Source0:        https://gitlab.cern.ch/geant4/geant4/-/archive/v%{version}/geant4-v%{version}.tar.gz

# Data sets
Source1:        https://cern.ch/geant4-data/datasets/G4NDL.4.7.1.tar.gz
Source2:        https://cern.ch/geant4-data/datasets/G4EMLOW.8.8.tar.gz
Source3:        https://cern.ch/geant4-data/datasets/G4PhotonEvaporation.6.1.2.tar.gz
Source4:        https://cern.ch/geant4-data/datasets/G4RadioactiveDecay.6.1.2.tar.gz
Source5:        https://cern.ch/geant4-data/datasets/G4PARTICLEXS.4.2.tar.gz
Source6:        https://cern.ch/geant4-data/datasets/G4PII.1.3.tar.gz
Source7:        https://cern.ch/geant4-data/datasets/G4RealSurface.2.2.tar.gz
Source8:        https://cern.ch/geant4-data/datasets/G4SAIDDATA.2.0.tar.gz
Source9:        https://cern.ch/geant4-data/datasets/G4ABLA.3.3.tar.gz
Source10:       https://cern.ch/geant4-data/datasets/G4INCL.1.3.tar.gz
Source11:       https://cern.ch/geant4-data/datasets/G4ENSDFSTATE.3.0.tar.gz
Source12:       https://cern.ch/geant4-data/datasets/G4CHANNELING.2.0.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  expat-devel
BuildRequires:  zlib-devel
BuildRequires:  xerces-c-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qt3d-devel
BuildRequires:  libX11-devel
BuildRequires:  libXmu-devel
BuildRequires:  libXpm-devel
BuildRequires:  libXft-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libGLU-devel

Requires:       %{name}-data = %{version}-%{release}
Requires:       qt6-qtbase
Requires:       xerces-c

%description
Geant4 is a toolkit for the simulation of the passage of particles through matter.
Its areas of application include high energy, nuclear and accelerator physics,
as well as studies in medical and space science.

%package devel
Summary:        Development files for Geant4
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       cmake

%description devel
This package contains the header files and CMake configuration files necessary
for developing applications using Geant4.

%package data
Summary:        Data files for Geant4 physics models
BuildArch:      noarch

%description data
This package provides the data files required by Geant4 physics models.
It includes cross-sections, decay tables, and other data needed for
accurate simulation of particle interactions.

%prep
%setup -q -n geant4-v%{version}

# Unpack data files into a 'data' subdirectory for easier handling
mkdir -p data_archive
cp %{SOURCE1} %{SOURCE2} %{SOURCE3} %{SOURCE4} %{SOURCE5} %{SOURCE6} \
   %{SOURCE7} %{SOURCE8} %{SOURCE9} %{SOURCE10} %{SOURCE11} %{SOURCE12} \
   data_archive/

%build
%cmake \
    -DGEANT4_INSTALL_DATA=OFF \
    -DGEANT4_USE_SYSTEM_EXPAT=ON \
    -DGEANT4_USE_SYSTEM_ZLIB=ON \
    -DGEANT4_USE_QT=ON \
    -DGEANT4_USE_OPENGL_X11=ON \
    -DGEANT4_USE_RAYTRACER_X11=ON \
    -DGEANT4_USE_GDML=ON \
    -DGEANT4_BUILD_MULTITHREADED=ON \
    -DGEANT4_INSTALL_EXAMPLES=OFF \
    -DGEANT4_BUILD_TLS_MODEL=global-dynamic

%cmake_build

%install
%cmake_install

# Install data files
mkdir -p %{buildroot}%{_datadir}/geant4/data
for f in data_archive/*.tar.gz; do
    tar -xf "$f" -C %{buildroot}%{_datadir}/geant4/data/
done

# Create a shell script to set environment variables
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
cat <<EOF > %{buildroot}%{_sysconfdir}/profile.d/geant4.sh
export G4NEUTRONHPDATA=%{_datadir}/geant4/data/G4NDL4.7.1
export G4LEDATA=%{_datadir}/geant4/data/G4EMLOW8.8
export G4LEVELGAMMADATA=%{_datadir}/geant4/data/G4PhotonEvaporation6.1.2
export G4RADIOACTIVEDATA=%{_datadir}/geant4/data/RadioactiveDecay6.1.2
export G4PARTICLEXSDATA=%{_datadir}/geant4/data/G4PARTICLEXS4.2
export G4PIIDATA=%{_datadir}/geant4/data/G4PII1.3
export G4REALSURFACEDATA=%{_datadir}/geant4/data/RealSurface2.2
export G4SAIDXSDATA=%{_datadir}/geant4/data/G4SAIDDATA2.0
export G4ABLADATA=%{_datadir}/geant4/data/G4ABLA3.3
export G4INCLDATA=%{_datadir}/geant4/data/G4INCL1.3
export G4ENSDFSTATEDATA=%{_datadir}/geant4/data/G4ENSDFSTATE3.0
export G4CHANNELINGDATA=%{_datadir}/geant4/data/G4CHANNELING2.0
EOF

# Create C-shell version
cat <<EOF > %{buildroot}%{_sysconfdir}/profile.d/geant4.csh
setenv G4NEUTRONHPDATA %{_datadir}/geant4/data/G4NDL4.7.1
setenv G4LEDATA %{_datadir}/geant4/data/G4EMLOW8.8
setenv G4LEVELGAMMADATA %{_datadir}/geant4/data/G4PhotonEvaporation6.1.2
setenv G4RADIOACTIVEDATA %{_datadir}/geant4/data/RadioactiveDecay6.1.2
setenv G4PARTICLEXSDATA %{_datadir}/geant4/data/G4PARTICLEXS4.2
setenv G4PIIDATA %{_datadir}/geant4/data/G4PII1.3
setenv G4REALSURFACEDATA %{_datadir}/geant4/data/RealSurface2.2
setenv G4SAIDXSDATA %{_datadir}/geant4/data/G4SAIDDATA2.0
setenv G4ABLADATA %{_datadir}/geant4/data/G4ABLA3.3
setenv G4INCLDATA %{_datadir}/geant4/data/G4INCL1.3
setenv G4ENSDFSTATEDATA %{_datadir}/geant4/data/G4ENSDFSTATE3.0
setenv G4CHANNELINGDATA %{_datadir}/geant4/data/G4CHANNELING2.0
EOF

%files
%license LICENSE
%doc README*
%{_bindir}/*
%{_libdir}/*.so.*
# %{_datadir}/Geant4-%{version}/  <-- Empty when data/examples disabled
%{_sysconfdir}/profile.d/geant4.sh
%{_sysconfdir}/profile.d/geant4.csh
%{_datadir}/Geant4/

%files devel
%{_includedir}/Geant4/
%{_libdir}/*.so
%{_libdir}/cmake/Geant4/
%{_libdir}/Geant4-%{version}/
%{_libdir}/pkgconfig/G4ptl.pc

%files data
%{_datadir}/geant4/data/

%changelog
* Wed Apr 23 2026 Morgan Hough <morgan.hough@gmail.com> - 11.4.1-1
- Update to 11.4.1

* Mon Feb 02 2026 Antigravity <antigravity@example.com> - 11.4.0-1
- Initial package for Geant4 11.4.0 with bundled data package
