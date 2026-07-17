# Built from the m9h/sodecl fork's opencl3-modernize branch, which brings sodecl
# up to the OpenCL 3.0 API, unbundles pybind11, and makes the installed package
# resolve its kernels + Random123 from %%{_datadir}/sodecl (upstream avramidis/sodecl
# hardcoded them relative to CWD and shipped no install rules for the Python module).
%global commit      1d138bef442524f2ed68f0002fc4af45cd6c8f95
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate    20260710

# Random123 headers (BSD-3-Clause) are shipped as OpenCL kernel include data.
%global _description %{expand:
SODECL is a library of ordinary differential equation (ODE) and stochastic
differential equation (SDE) solvers in OpenCL. It integrates many orbits of an
ODE/SDE system in parallel across the cores of a CPU or a GPU, which is useful
for example when fitting biological ODE models to data over large parameter
sweeps. The Euler, Runge-Kutta, implicit Euler/midpoint and Euler-Maruyama
schemes are implemented.}

Name:           sodecl
Version:        0.2.1
Release:        1^%{snapdate}git%{shortcommit}%{?dist}
Summary:        OpenCL ODE and SDE solvers

# sodecl itself is MIT; the bundled Random123 headers shipped as kernel data are BSD-3-Clause
License:        MIT AND BSD-3-Clause
URL:            https://github.com/avramidis/sodecl
Source0:        https://github.com/m9h/sodecl/archive/%{commit}/sodecl-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  opencl-headers
BuildRequires:  ocl-icd-devel
BuildRequires:  pybind11-devel
BuildRequires:  python3-devel
BuildRequires:  python3-numpy
# chrpath strips the build-tree RUNPATH from the hand-installed Python module
BuildRequires:  chrpath
# %%check runs the Python test suite on a CPU OpenCL device
BuildRequires:  pocl

%description %_description

%package     -n python3-sodecl
Summary:        Python interface to the SODECL OpenCL ODE/SDE solvers
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-numpy
%description -n python3-sodecl
Python (pybind11) interface to SODECL. Provides the sodecl module for driving the
OpenCL ODE/SDE solvers from NumPy arrays.

%package        devel
Summary:        Development files for SODECL
Requires:       %{name}%{?_isa} = %{version}-%{release}
%description    devel
C++ headers and CMake package files for building against the SODECL library.

%prep
%autosetup -n sodecl-%{commit}

%build
# %%cmake selects the Ninja generator and prefix=/usr; SODECL_DATADIR then defaults
# to %{_datadir}/sodecl. WARNINGS_AS_ERRORS is OFF in the fork.
%cmake -DCMAKE_INSTALL_PREFIX=%{_prefix}
%cmake_build

%install
%cmake_install
# Upstream ships no install rule for the Python bits — place them by hand.
install -d %{buildroot}%{python3_sitearch}
install -m 0755 %{__cmake_builddir}/interfaces/python/sodecl_interface*.so %{buildroot}%{python3_sitearch}/
install -m 0644 interfaces/python/sodecl.py %{buildroot}%{python3_sitearch}/
# The module was linked with a build-tree RPATH; it isn't needed (libsodecl.so is
# in the default library path) and check-rpaths rejects it.
chrpath --delete %{buildroot}%{python3_sitearch}/sodecl_interface*.so

%check
# tests_python runs the solver suite on pocl's CPU device; the ctest ENVIRONMENT
# points SODECL_DATADIR at the build tree's kernels + Random123.
%ctest

%files
%license LICENSE
%doc README.md
# NOTE: unversioned .so — the library carries no SOVERSION upstream yet. Acceptable
# for this COPR; add VERSION/SOVERSION upstream to split a versioned runtime later.
%{_libdir}/libsodecl.so
%dir %{_datadir}/sodecl
%{_datadir}/sodecl/kernels
%{_datadir}/sodecl/Random123

%files -n python3-sodecl
%{python3_sitearch}/sodecl_interface*.so
%{python3_sitearch}/sodecl.py
%{python3_sitearch}/__pycache__/sodecl.cpython-3*.pyc

%files devel
%{_includedir}/*.hpp
%{_includedir}/sodecl_export.h
%{_libdir}/cmake/sodecl/

%changelog
* Fri Jul 10 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.1-1^20260710git1d138be
- Initial package from the OpenCL-3.0-modernized m9h/sodecl fork
- Builds against OpenCL 3.0 headers; system pybind11; installable kernel/Random123 data
