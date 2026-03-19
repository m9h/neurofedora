Name:           gifticlib-cmake-devel
Version:        1.0.9
Release:        2%{?dist}
Summary:        CMake config files for system gifticlib
BuildArch:      noarch

License:        MIT
URL:            http://www.nitrc.org/projects/gifti/

# The cmake config files are maintained in this COPR repository.
# They wrap the system gifticlib-devel package (version 1.0.9 in Fedora).
Source0:        gifticlib-config.cmake
Source1:        gifticlib-config-version.cmake
Source2:        gifticlib-cmake-LICENSE
# GIFTI namespace config for consumers that do find_package(GIFTI)
# (e.g. AFNI expects GIFTI::giftiio target)
Source3:        GIFTI-config.cmake
Source4:        GIFTI-config-version.cmake

Requires:       gifticlib-devel

%description
CMake find_package() config files for the system gifticlib library.
Fedora's gifticlib-devel package does not ship CMake config files,
which prevents packages that use find_package(gifticlib) from
finding it. This package installs config files providing both:
  - gifticlib::gifticlib target (via find_package(gifticlib))
  - GIFTI::giftiio target (via find_package(GIFTI))

%prep
cp %{SOURCE2} LICENSE

%build
# Nothing to build.

%install
install -d %{buildroot}%{_datadir}/cmake/gifticlib
install -m 644 %{SOURCE0} %{buildroot}%{_datadir}/cmake/gifticlib/gifticlib-config.cmake
install -m 644 %{SOURCE1} %{buildroot}%{_datadir}/cmake/gifticlib/gifticlib-config-version.cmake

install -d %{buildroot}%{_datadir}/cmake/GIFTI
install -m 644 %{SOURCE3} %{buildroot}%{_datadir}/cmake/GIFTI/GIFTIConfig.cmake
install -m 644 %{SOURCE4} %{buildroot}%{_datadir}/cmake/GIFTI/GIFTIConfigVersion.cmake

%check
# Verify cmake config files are findable
test -f %{buildroot}%{_datadir}/cmake/gifticlib/gifticlib-config.cmake
test -f %{buildroot}%{_datadir}/cmake/GIFTI/GIFTIConfig.cmake

%files
%license LICENSE
%{_datadir}/cmake/gifticlib/
%{_datadir}/cmake/GIFTI/

%changelog
* Sun Mar 15 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.9-2
- Add GIFTI namespace: find_package(GIFTI) now provides GIFTI::giftiio target
- Required by AFNI cmake build system

* Mon Feb 23 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.9-1
- Initial packaging: CMake config files for gifticlib 1.0.9
- Renamed to gifticlib-cmake-devel (devel dep on gifticlib-devel is correct)
- Provides gifticlib::gifticlib imported target for find_package(gifticlib)
