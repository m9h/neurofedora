%global debug_package %{nil}
%global commit 65057f9fd64043bd4759f23051297f7e0cfccd7e
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate 20230304

Name:           python-cc3dext
Version:        0.3.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        CompuCell3D extension modules (MaBoSS Boolean-network solver)

# CompuCell3DExtensions is MIT; it vendors the MaBoSS engine (sysbio-curie, BSD-3).
License:        MIT AND BSD-3-Clause
URL:            https://github.com/CompuCell3D/CompuCell3DExtensions
Source0:        %{url}/archive/%{commit}/CompuCell3DExtensions-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  swig
BuildRequires:  python3-devel
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  patchelf

%description
Extension modules that integrate with CompuCell3D. This package provides the
cc3dext.MaBoSSCC3DPy module — CompuCell3D's bundled MaBoSS Boolean-network
simulation engine — used by cc3d.core.MaBoSSCC3D for discrete logical models.

%package -n python3-cc3dext
Summary:        %{summary}
%description -n python3-cc3dext
%{description}

%prep
%autosetup -n CompuCell3DExtensions-%{commit}

# GCC 15 no longer transitively includes <cstdint>; the bundled MaBoSS engine
# uses uint64_t/uint32_t without including it. Inject the header where needed.
# Use <stdint.h> (global ::uint64_t), not <cstdint> (std::uint64_t only) — the
# engine uses the type unqualified.
for f in $(grep -rlE "uint(8|16|32|64)_t" cc3dext/MaBoSS/cpp 2>/dev/null); do
    grep -qE "include <stdint.h>" "$f" || sed -i '1i #include <stdint.h>' "$f"
done

%build
export SP_DIR=%{python3_sitearch}
pushd cc3dext/MaBoSS
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCC3D_EXT_NAME=cc3dext \
    -DMABOSS_MAXNODES=64 \
    -DCMAKE_INSTALL_PREFIX=%{_prefix}
%cmake_build
popd

%install
export SP_DIR=%{python3_sitearch}
pushd cc3dext/MaBoSS
%cmake_install
popd

# The engine libs install to %%{_prefix}/lib; make them private to the python
# module dir and wire $ORIGIN so the SWIG module finds them without RPATH/ldconfig.
moddir=%{buildroot}%{python3_sitearch}/cc3dext
mv %{buildroot}%{_prefix}/lib/libcc3deMaBoSS*.so* $moddir/ 2>/dev/null || :
rmdir %{buildroot}%{_prefix}/lib 2>/dev/null || :
for so in $moddir/*.so; do patchelf --set-rpath '$ORIGIN' "$so" 2>/dev/null || :; done
# Drop the installed C++ headers (no -devel consumer).
rm -rf %{buildroot}%{_includedir}/cc3dext

%files -n python3-cc3dext
%license LICENSE
%{python3_sitearch}/cc3dext/

%changelog
* Sat Jun 20 2026 Morgan Hough <morgan.hough@gmail.com> - 0.3.0-0.1.20230304git65057f9
- Initial package: CompuCell3DExtensions cc3dext.MaBoSSCC3DPy (bundled MaBoSS
  engine) — enables CompuCell3D's MaBoSS Boolean-network demos.
