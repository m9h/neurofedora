Name:           gifticlib-cmake-devel
Version:        1.0.9
Release:        1%{?dist}
Summary:        CMake config files for system gifticlib
BuildArch:      noarch

License:        MIT
URL:            http://www.nitrc.org/projects/gifti/

# The cmake config files are maintained in this COPR repository.
# They wrap the system gifticlib-devel package (version 1.0.9 in Fedora).
Source0:        gifticlib-config.cmake
Source1:        gifticlib-config-version.cmake
Source2:        gifticlib-cmake-LICENSE

Requires:       gifticlib-devel

%description
CMake find_package() config files for the system gifticlib library.
Fedora's gifticlib-devel package does not ship CMake config files,
which prevents packages that use find_package(gifticlib) from
finding it. This package installs gifticlib-config.cmake and
gifticlib-config-version.cmake, providing the imported target
gifticlib::gifticlib.

%prep
cp %{SOURCE2} LICENSE

%build
# Nothing to build.

%install
install -d %{buildroot}%{_datadir}/cmake/gifticlib
install -m 644 %{SOURCE0} %{buildroot}%{_datadir}/cmake/gifticlib/gifticlib-config.cmake
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/cmake/gifticlib/gifticlib-config-version.cmake

%files
%license LICENSE
%{_datadir}/cmake/gifticlib/

%changelog
* Mon Feb 23 2026 Morgan Hough <morgan@example.com> - 1.0.9-1
- Initial packaging: CMake config files for gifticlib 1.0.9
- Renamed to gifticlib-cmake-devel (devel dep on gifticlib-devel is correct)
- Provides gifticlib::gifticlib imported target for find_package(gifticlib)
