%global realname urdfdom_headers

Name:           urdfdom-headers
Version:        1.1.2
Release:        3%{?dist}
Summary:        The URDF (U-Robot Description Format) headers

License:        BSD-3-Clause
URL:            http://ros.org/wiki/urdf
Source0:        https://github.com/ros/%{realname}/archive/%{version}/%{realname}-%{version}.tar.gz
BuildArch:      noarch

# Install configs to arch independent paths
# https://github.com/ros/urdfdom_headers/issues/27
Patch0:         urdfdom-headers-1.1.2-fedora.patch

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake

%description
%{summary}

%package devel
Summary:        The URDF (U-Robot Description Format) headers
Requires:       pkgconfig
BuildArch:      noarch
Provides:       %{name}-static = %{version}-%{release}

%description devel
The URDF (U-Robot Description Format) headers provides core data structure
headers for URDF.

For now, the details of the URDF specifications reside on
http://ros.org/wiki/urdf

%prep
%autosetup -Sgendiff -p1 -n %{realname}-%{version}

%build
%cmake -DCMAKE_BUILD_TYPE:STRING=Release
%cmake_build

%install
%cmake_install

%files devel
%license LICENSE
%doc README.md
%{_includedir}/urdfdom_headers
%{_datadir}/pkgconfig/*.pc
%{_datadir}/%{realname}

%changelog
* Wed May 20 2026 Morgan Hough <morgan.hough@gmail.com> - 1.1.2-3
- Revive from Fedora orphan state (was dropped after F42, August 2025).
- Imported F42 spec unchanged; rebuilt for F44 against current toolchain.
- First step in reviving the urdfdom-headers / urdfdom / fcl / DART chain
  for the COPR scientific stack.

* Sun Jan 19 2025 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Fri Jan 10 2025 Scott K Logan <logans@cottsay.net> - 1.1.2-1
- Update to release 1.1.2
- Review SPDX license identifier

* Wed Sep 04 2024 Miroslav Suchý <msuchy@redhat.com> - 1.1.1-3
- convert license to SPDX

* Sat Jul 20 2024 Fedora Release Engineering <releng@fedoraproject.org> - 1.1.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Tue Apr 02 2024 Rich Mattes <richmattes@gmail.com> - 1.1.1-1
- Update to release 1.1.1
