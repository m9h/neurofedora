%global commit      538f80794c7d736afc0a452d21313606cc5538fc
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate    20220807

Name:           xlnt
Version:        1.5.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        C++ library for reading and writing XLSX (Excel) spreadsheets

License:        MIT
URL:            https://github.com/tfussell/xlnt
# Pinned to the post-1.5.0 master commit (142 commits ahead of the v1.5.0 tag)
# that ShapeWorks builds against — there has been no newer xlnt release.
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
# xlnt bundles libstudxml as a git SUBMODULE (codesynthesis), which a GitHub
# archive tarball does not include — ship its pinned commit separately and drop
# it into third-party/libstudxml. (MIT; compiled into libxlnt.)
%global libstudxml_commit e729667b0f34a39ce4a61339843af4154648667b
%global libstudxml_short  e729667
Source1:        https://github.com/codesynthesis-com/libstudxml/archive/%{libstudxml_commit}/libstudxml-%{libstudxml_short}.tar.gz

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++

# Bundled third-party shipped in-tree (libstudxml is compiled into libxlnt;
# miniz and utfcpp are header-only). Unbundling is a future cleanup.
Provides:       bundled(libstudxml)
Provides:       bundled(miniz)
Provides:       bundled(utf8cpp)

%description
xlnt is a modern C++14 library for manipulating spreadsheets in memory and
reading/writing them from/to XLSX (Office Open XML) files, with an API modeled
on openpyxl. Used by ShapeWorks to read and write its .xlsx project files.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
Headers, CMake package config and pkg-config file for developing against %{name}.

%prep
%autosetup -n %{name}-%{commit}
# Populate the empty libstudxml submodule dir (missing from the GitHub archive).
tar -xzf %{SOURCE1} --strip-components=1 -C third-party/libstudxml

%build
# xlnt 1.5.0-era sources use fixed-width ints (uint32_t ...) without <cstdint>,
# which GCC 13+ no longer pulls in transitively (the same fix ShapeWorks applies).
export CXXFLAGS="%{optflags} -include cstdint"
%cmake -GNinja \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DSTATIC:BOOL=OFF \
    -DTESTS:BOOL=OFF \
    -DSAMPLES:BOOL=OFF \
    -DBENCHMARKS:BOOL=OFF \
    -DPYTHON:BOOL=OFF
%cmake_build

%install
%cmake_install

%files
%license LICENSE.md
%doc README.md
%{_libdir}/libxlnt.so.1.5*

%files devel
%{_includedir}/xlnt/
%{_libdir}/libxlnt.so
%{_libdir}/cmake/xlnt/
%{_libdir}/pkgconfig/xlnt.pc
%{_mandir}/man3/xlnt.3*

%changelog
* Wed Jun 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.5.0-0.1.20220807git538f807
- Initial package (xlnt master snapshot 538f807, the version ShapeWorks pins).
  Shared lib only, tests/python off, -include cstdint for the GCC 13+ fixed-width
  int fix. Second prerequisite of the ShapeWorks dependency chain.
