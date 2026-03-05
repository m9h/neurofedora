Name:           ismrmrd
Version:        1.15.0
Release:        1%{?dist}
Summary:        ISMRM Raw Data Format

License:        MIT
URL:            https://github.com/ismrmrd/ismrmrd
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  hdf5-devel
BuildRequires:  boost-devel
BuildRequires:  pugixml-devel
BuildRequires:  fftw-devel
BuildRequires:  doxygen

%description
The ISMRMRD format combines a mix of flexible data structures (XML header)
and fixed structures (equivalent to C-structs) to represent MRI data.
This package provides the C++ library and utilities for reading and
writing ISMRMRD files.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       hdf5-devel%{?_isa}
Requires:       pugixml-devel%{?_isa}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup

%build
%cmake
%cmake_build

%install
%cmake_install

# Remove unnecessary files
rm -rf %{buildroot}%{_datadir}/%{name}/matlab

%files
%license LICENSE
%{_libdir}/libismrmrd.so.1*
%{_bindir}/ismrmrd_*

%files devel
%{_includedir}/ismrmrd/
%{_libdir}/libismrmrd.so
%{_libdir}/cmake/ISMRMRD/
%{_datadir}/ismrmrd/

%changelog
* Fri Feb 27 2026 Gemini CLI <gemini@example.com> - 1.15.0-1
- Initial package for Fedora
