%global srcdir Soar-releases-%{version}

Name:           soar
Version:        9.6.5
Release:        1%{?dist}
Summary:        General cognitive architecture for intelligent systems

License:        BSD-2-Clause
URL:            https://soar.eecs.umich.edu/
Source0:        https://github.com/SoarGroup/Soar/archive/refs/tags/releases/%{version}.tar.gz#/Soar-%{version}.tar.gz

BuildRequires:  cmake >= 3.26
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  sqlite-devel
BuildRequires:  swig >= 4.2
BuildRequires:  python3-devel
BuildRequires:  chrpath

%description
Soar is a general cognitive architecture for developing systems that exhibit
intelligent behavior. It integrates knowledge-intensive reasoning, reactive
execution, hierarchical reasoning, planning, and learning from experience
(reinforcement learning, chunking, episodic and semantic memory). This package
provides the Soar runtime library and the command-line interface.

%package devel
Summary:        Development files for Soar
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and CMake package configuration for building C++ applications against
the Soar SML (Soar Markup Language) client library.

%package -n python3-soar
Summary:        Python bindings for Soar
Requires:       %{name}%{?_isa} = %{version}-%{release}
%{?python_provide:%python_provide python3-soar}

%description -n python3-soar
SWIG-generated Python bindings for the Soar SML client interface, allowing
Python programs to create Soar kernels and agents and exchange working-memory
structures with them.

%prep
%autosetup -n %{srcdir}
# Upstream ships libSoar with no versioned SONAME; inject one so the library
# satisfies Fedora's shared-library policy.
cat >> CMakeLists.txt <<'EOF'
set_target_properties(${SOAR_LIB} PROPERTIES VERSION %{version} SOVERSION 9)
EOF

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_SHARED_LIBS=ON \
    -DCLI=ON \
    -DSWIG_PYTHON=ON \
    -DBUILD_TESTS=OFF \
    -DSVS=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH=ON
%cmake_build

%install
%cmake_install

# Relocate the Python module from the upstream's hardcoded <prefix>/python
# into the proper Python site-packages directory.
install -d %{buildroot}%{python3_sitearch}
mv %{buildroot}%{_prefix}/python/* %{buildroot}%{python3_sitearch}/
rmdir %{buildroot}%{_prefix}/python
# Drop the upstream test script from the importable package.
rm -f %{buildroot}%{python3_sitearch}/TestPythonSML.py

# Relocate the runtime settings file out of %%{_prefix} root.
install -d %{buildroot}%{_datadir}/%{name}
mv %{buildroot}%{_prefix}/settings.soar %{buildroot}%{_datadir}/%{name}/settings.soar
# The Java debugger launcher is installed unconditionally upstream but we do
# not build the Java components.
rm -f %{buildroot}%{_prefix}/SoarJavaDebugger.sh %{buildroot}%{_prefix}/SoarJavaDebugger.bat

# Belt-and-suspenders RPATH strip (libSoar is in the default loader path).
find %{buildroot}%{python3_sitearch} %{buildroot}%{_bindir} -type f \
    \( -name '*.so' -o -name '*.abi3.so' -o -name soar \) \
    -exec chrpath --delete {} + 2>/dev/null || :

%ldconfig_scriptlets

%files
%license LICENSE.md
%doc README.md
%{_bindir}/soar
%{_libdir}/libSoar.so.*
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/settings.soar

%files devel
%{_includedir}/*.h
%{_includedir}/*.hpp
%{_includedir}/msvc/
%{_libdir}/libSoar.so
%{_libdir}/cmake/soar/

%files -n python3-soar
%{python3_sitearch}/Python_sml_ClientInterface.py
%{python3_sitearch}/*Python_sml_ClientInterface*.so
%{python3_sitearch}/__pycache__/Python_sml_ClientInterface*.pyc

%changelog
* Sun Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 9.6.5-1
- Initial package (CMake build: runtime lib, CLI, Python SWIG bindings)
