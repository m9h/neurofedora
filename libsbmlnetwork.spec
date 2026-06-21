%global debug_package %{nil}
%global srcname SBMLNetwork

Name:           libsbmlnetwork
Version:        0.5.12
Release:        1%{?dist}
Summary:        Library for reading, writing, and creating SBML layout and render information

# Upstream sys-bio/SBMLNetwork is MIT.
License:        MIT
URL:            https://github.com/sys-bio/SBMLNetwork
# tarball of the v%{version} tag (extracts to %{srcname}-%{version})
Source0:        %{name}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  libsbml-devel
BuildRequires:  expat-devel
BuildRequires:  zlib-ng-compat-devel
BuildRequires:  chrpath

%description
libSBMLNetwork is a C++ library, with a C API, for reading, writing, manipulating,
and autogenerating the Layout and Render extension information of SBML models —
the graphical network representation used by SBML reaction/regulatory diagrams.
This Fedora build links the system libSBML, expat, and zlib (no superbuild).

%package devel
Summary:        Development files for libsbmlnetwork
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libsbml-devel%{?_isa}

%description devel
Headers and the unversioned shared-object symlink for building against
libSBMLNetwork.

%prep
%autosetup -n %{srcname}-%{version}

# The v0.5.12 release tag ships a stale VERSION.txt (0.5.11) — upstream forgot to
# bump it. Sync it to the release version so the soname full-version matches.
echo -n "%{version}" > VERSION.txt

# Link the SHARED system libSBML (Fedora ships no static libsbml-static.a).
sed -i 's/NAMES libsbml-static.a libsbml-staticd.a/NAMES sbml libsbml-static.a libsbml-staticd.a/' CMakeLists.txt

# Fedora's libSBML is GLOBAL-namespace (built without LIBSBML_USE_CPP_NAMESPACE),
# so `using namespace libsbml;` fails ("libsbml is not a namespace-name"). The code
# carries no `libsbml::` qualifiers, so simply dropping the using-directives lets the
# unqualified libSBML types resolve from the global namespace.
find src -type f \( -name '*.h' -o -name '*.cpp' \) -print0 \
  | xargs -0 sed -i '/using namespace libsbml;/d'

# Drop the upstream-forced -O0 / -std=gnu++11 / old-dtags overrides so Fedora's
# %%{optflags} (optimization + hardening) govern the build.
sed -i 's/ -O0 -fPIC -std=gnu++11 -Wl,--disable-new-dtags -Wno-deprecated/ -fPIC -Wno-deprecated/' CMakeLists.txt
sed -i 's/ -O0 -Wall -Wno-inline -Wno-deprecated/ -Wall -Wno-inline -Wno-deprecated/' CMakeLists.txt

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DDEPENDENCIES_INSTALL_PREFIX=%{_prefix} \
    -DLIBSBML_INSTALL_PREFIX=%{_prefix} \
    -DEXPAT_INSTALL_PREFIX=%{_prefix} \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_STATIC_LIBS=OFF \
    -DWITH_PYTHON=OFF \
    -DWITH_SWIG=OFF
%cmake_build

%install
%cmake_install
# Upstream installs the runtime .so under %%{_prefix}/lib via DESTINATION lib.
# Normalise to %%{_libdir} when CMake didn't pick lib64.
if [ -d %{buildroot}%{_prefix}/lib -a "%{_libdir}" != "%{_prefix}/lib" ]; then
    mkdir -p %{buildroot}%{_libdir}
    mv %{buildroot}%{_prefix}/lib/libsbmlnetwork.so* %{buildroot}%{_libdir}/ 2>/dev/null || :
    rmdir %{buildroot}%{_prefix}/lib 2>/dev/null || :
fi
# Strip the $ORIGIN RPATH upstream bakes in.
chrpath --delete %{buildroot}%{_libdir}/libsbmlnetwork.so.* 2>/dev/null || :

%ldconfig_scriptlets

%files
%license LICENSE
%doc README.md
%{_libdir}/libsbmlnetwork.so.*

%files devel
%{_includedir}/sbmlnetwork/
%{_libdir}/libsbmlnetwork.so

%changelog
* Fri Jun 19 2026 Morgan Hough <morgan.hough@gmail.com> - 0.5.12-1
- Initial package: libSBMLNetwork 0.5.12 (sys-bio fork), system libs, no superbuild.
- Dependency of antimony 3.1.3 (SBML layout/render support).
