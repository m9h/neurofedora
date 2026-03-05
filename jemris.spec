Name:           jemris
Version:        2.9.2
Release:        1%{?dist}
Summary:        Juelich Extensible MRI Simulator

License:        GPL-2.0-or-later
URL:            https://github.com/JEMRIS/jemris
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  sundials-devel
BuildRequires:  xerces-c-devel
BuildRequires:  hdf5-devel
BuildRequires:  cln-devel
BuildRequires:  ginac-devel
BuildRequires:  ismrmrd-devel
BuildRequires:  openmpi-devel
BuildRequires:  boost-devel

%description
JEMRIS is a general MRI simulation framework. It is designed to simulate
realistic MRI experiments with arbitrary pulse sequences, coil setups,
and samples.

%prep
%autosetup -n %{name}-%{version}

# Remove hardcoded mpicxx compiler
sed -i '/set(CMAKE_CXX_COMPILER/d' CMakeLists.txt

# Remove bundled conda logic or other non-RPM parts
sed -i '/message( NOTICE "creating conda environment/,/endif()/d' CMakeLists.txt
# Remove docker pull from CMakeLists.txt
sed -i '/message( NOTICE "pulling docker image/,/endif()/d' CMakeLists.txt

# Fix SUNDIALS 7.x types (realtype -> sunrealtype)
sed -i 's/\brealtype\b/sunrealtype/g' src/*.cpp src/*.h

# Fix SUNDIALS 7.x API (passing comm by value instead of pointer)
sed -i 's/SUNContext_Create( \&comm,/SUNContext_Create( comm,/g' src/*.cpp

# Remove deprecated CVodeSetErrFile (not in SUNDIALS 6+)
sed -i 's/CVodeSetErrFile.*//g' src/*.cpp

# Fix HDF5/size_t conflict in NDData.h
# On 64-bit Fedora, hsize_t and size_t are same, causing an overload conflict.
# We use a more robust way to remove the duplicate constructor.
sed -i '/NDData (const std::vector<hsize_t>& dims)/,/}/d' src/NDData.h

# Add missing includes for newer GCC
sed -i '1i #include <cstdint>\n#include <stdexcept>\n#include <algorithm>' src/NDData.h

%build
# Standard serial build
%cmake \
    -DSKIP_CONDA=ON \
    -DJEMRIS_ENABLE_MPI=OFF
%cmake_build

%install
%cmake_install

%files
%license COPYING
%doc README.md AUTHORS ChangeLog
%{_bindir}/jemris
%{_bindir}/sanityck
%{_datadir}/jemris/

%changelog
* Fri Feb 27 2026 Gemini CLI <gemini@example.com> - 2.9.2-1
- Initial package for Fedora
