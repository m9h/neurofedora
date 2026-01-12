Name:           liblsl
Version:        1.16.2
Release:        1%{?dist}
Summary:        Lab Streaming Layer (LSL) library

License:        MIT
URL:            https://github.com/sccn/liblsl
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  boost-devel
BuildRequires:  ninja-build
BuildRequires:         chrpath

%description
The Lab Streaming Layer (LSL) is a system for the unified collection of
measurement time series in research experiments that handles both the
networking, time-synchronization, (near-) real-time access as well as
optionally the centralized collection, viewing and disk recording of the data.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains the header files and libraries needed to
develop applications that use the Lab Streaming Layer.

%prep
%autosetup -p1

%build
# Use Fedora cmake macro. The -GNinja flag forces the Ninja generator.
# We disable bundled boost to comply with Fedora policies.
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DLSL_BundledBoost=OFF

%cmake_build

%install
%cmake_install
chrpath --delete %{buildroot}%{_bindir}/lslver

%check
%ctest

%ldconfig_scriptlets

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/lslver
%{_libdir}/liblsl.so.*

%files devel
%{_includedir}/lsl/
%{_includedir}/lsl_c.h
%{_includedir}/lsl_cpp.h
%{_libdir}/liblsl.so
%{_libdir}/cmake/LSL/

%changelog
* Wed Jan 07 2026 Morgan Hough <morgan.hough@gmail.com> - 1.16.2-1
- Initial RPM build for Fedora using standard macros
