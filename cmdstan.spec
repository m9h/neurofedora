Name:           cmdstan
Version:        2.38.0
Release:        2%{?dist}
Summary:        A command-line interface to the STAN library

License:        BSD
URL:            https://mc-stan.org/users/interfaces/cmdstan
Source0:        https://github.com/stan-dev/cmdstan/releases/download/v%{version}/cmdstan-%{version}.tar.gz
#https://github.com/stan-dev/cmdstan/releases/download/v2.20.0/cmdstan-2.20.0.tar.gz
#https://github.com/stan-dev/cmdstan/archive/v2.20.0.tar.gz
BuildRequires:  gcc-c++
BuildRequires:  boost-devel
# eigen3-devel intentionally NOT used: Stan Math's eigen_plugins.h relies on
# Eigen 3.4 macros (EIGEN_EMPTY_STRUCT_CTOR) and indexing semantics that
# Fedora's eigen3 5.0.1 (F44+) breaks. Bundled Stan eigen_3.4.0 is kept.
Provides:       bundled(eigen3) = 3.4.0
BuildRequires:  sundials-devel
BuildRequires:  tbb-devel
BuildRequires:  chrpath
BuildRequires:  rapidjson-devel
BuildRequires:  cli11-devel
BuildRequires:  gtest-devel
BuildRequires:  google-benchmark-devel

%description
Stan is a state-of-the-art platform for statistical modeling and\
 high-performance statistical computation.

%global debug_package %{nil}

%prep
%autosetup
# Patch for oneTBB compatibility
find . -type f \( -name "*.hpp" -o -name "*.cpp" -o -name "*.h" \) -exec sed -i 's|tbb/tbb_stddef.h|tbb/version.h|g' {} +

# Patch for system RapidJSON and CLI11
find . -type f \( -name "*.hpp" -o -name "*.cpp" -o -name "*.h" \) -exec sed -i 's|rapidjson_1.1.0/|rapidjson/|g' {} +
find . -type f \( -name "*.hpp" -o -name "*.cpp" -o -name "*.h" \) -exec sed -i 's|CLI11/CLI11.hpp|CLI/CLI.hpp|g' {} +
# Fix CLI11 2.x API mismatch (remove 4th bool argument from add_option)
sed -i 's|, *true)|)|g' src/cmdstan/stansummary.cpp
sed -i 's|, *false)|)|g' src/cmdstan/stansummary.cpp
# Sometimes it is on a new line
sed -i 'N;s|, *\n *true)|)|;P;D' src/cmdstan/stansummary.cpp
sed -i 'N;s|, *\n *false)|)|;P;D' src/cmdstan/stansummary.cpp

%build
# Use system libraries where possible. Keep Eigen bundled (3.4.0): system
# eigen3 on F44+ is 5.0.1 and breaks Stan Math's eigen_plugins.h.
cat <<EOF > make/local
BOOST = /usr/include
RAPIDJSON = /usr/include
CLI11 = /usr/include
# Use system oneTBB
TBB_INTERFACE_NEW = 1
TBB_INC = /usr/include
TBB_LIB = %{_libdir}
TBB_TARGETS =
# Unbundle SUNDIALS
SUNDIALS_INC = /usr/include
SUNDIALS_LIB = %{_libdir}
SUNDIALS_TARGETS =
LDLIBS_SUNDIALS = -lsundials_cvodes -lsundials_nvecserial -lsundials_idas -lsundials_kinsol
# Google Test and Benchmark
GTEST = /usr/include
BENCHMARK = /usr/include
EOF

make build %{?_smp_mflags}

%check
# Basic check
./bin/stanc --version
# Test building a model with our make/local
# We need to set STAN_NUM_THREADS=1 or similar to avoid TBB issues in some envs
make examples/bernoulli/bernoulli %{?_smp_mflags}

%install
# Install binaries
install -m0755 -d $RPM_BUILD_ROOT%{_bindir}
install -m0755 bin/stanc $RPM_BUILD_ROOT%{_bindir}
install -m0755 bin/stansummary $RPM_BUILD_ROOT%{_bindir}
install -m0755 bin/diagnose $RPM_BUILD_ROOT%{_bindir}

# Install the "source" tree needed to build models
# Users expect to run make inside this directory or point to it
install -m0755 -d $RPM_BUILD_ROOT%{_datadir}/%{name}
cp -r make src stan $RPM_BUILD_ROOT%{_datadir}/%{name}/

# Remove bundled libs from the installed tree to ensure system ones are used,
# EXCEPT for eigen_* which we keep (system eigen3 5.x is API-incompatible with
# Stan Math's eigen_plugins.h, see Provides: bundled(eigen3) above).
find $RPM_BUILD_ROOT%{_datadir}/%{name}/stan/lib/stan_math/lib -maxdepth 1 -type d \
    -not -path '*/lib' -not -name 'eigen_*' -exec rm -rf {} +
rm -rf $RPM_BUILD_ROOT%{_datadir}/%{name}/stan/lib/rapidjson_1.1.0

# Provide a default make/local in the installed tree
install -m0644 make/local $RPM_BUILD_ROOT%{_datadir}/%{name}/make/local

# Fix shebangs manually since macro expansion failed
find $RPM_BUILD_ROOT%{_datadir}/%{name} -type f -name "*.py" -exec sed -i 's|^#!/usr/bin/python$|#!/usr/bin/python3|' {} +
find $RPM_BUILD_ROOT%{_datadir}/%{name} -type f -name "*.py" -exec sed -i 's|^#!/usr/bin/env python$|#!/usr/bin/python3|' {} +
find $RPM_BUILD_ROOT%{_datadir}/%{name} -type f -name "*.py" -exec sed -i 's|^#!/usr/bin/env python3$|#!/usr/bin/python3|' {} +

# Remove RPATH if it persists
find $RPM_BUILD_ROOT%{_bindir} -type f -exec chrpath --delete {} \; || :

%files
%license LICENSE
%doc README.md
%{_bindir}/*
%{_datadir}/%{name}

%changelog
* Sat May 23 2026 Morgan G Hough <morgan.hough@gmail.com> - 2.38.0-2
- Keep bundled Stan eigen_3.4.0 instead of forcing system eigen3: Fedora 44+
  ships eigen3 5.0.1 which breaks Stan Math's eigen_plugins.h
  (EIGEN_EMPTY_STRUCT_CTOR macro + Eigen::all ambiguity, F44 FTBFS build 10504837)
- Drop eigen3-devel BuildRequires (no longer needed)
- Add Provides: bundled(eigen3) = 3.4.0

* Thu Feb 19 2026 Morgan G Hough <morgan.hough@gmail.com> - 2.38.0-1
- Update to 2.38.0

* Sat Sep 21 2019 Morgan G Hough <morgan.hough@gmail.com> - 2.24.0-1
- Initial package
