%global gh_owner davisking
%global gh_name dlib

# Tests are very memory-heavy (single-thread peak ~12GiB at -O, ~17GiB at
# -O2 on the 19.x series, and v20 adds more deep-learning tests).  COPR
# x86_64 builders rarely have that headroom, so they are off by default.
# Enable explicitly with `--with ctest`.
%bcond ctest 0

Name:           dlib
Version:        20.0.1
Release:        1%{?dist}
Summary:        A modern C++ toolkit containing machine learning algorithms

# Library + bindings + bundled cblas/zlib stubs + documentation are all
# BSL-1.0 (LICENSE.txt at repo root, identical headers in examples).
# Note: the bundled examples/video_frames/ JPEG frames are CC-BY-SA-3.0
# (BoBoT dataset) — covered separately by the -doc subpackage.
License:        BSL-1.0
URL:            http://dlib.net
Source0:        https://github.com/%{gh_owner}/%{gh_name}/archive/v%{version}/%{gh_name}-%{version}.tar.gz

# Upstream forbids i686 and tests fail / coredump on s390x.
ExcludeArch:    %{ix86} s390x

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  gcc-gfortran
BuildRequires:  cmake(pybind11)
BuildRequires:  pkgconfig(fftw3)
# Fedora uses FlexiBLAS as the BLAS/LAPACK switchboard.  Linking
# against flexiblas (rather than cblas/lapack directly) is the
# packaging policy.
BuildRequires:  pkgconfig(flexiblas)
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavdevice)
BuildRequires:  pkgconfig(libavfilter)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libswresample)
BuildRequires:  pkgconfig(libswscale)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(python3)
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  pkgconfig(x11)
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
%if %{with ctest}
BuildRequires:  python3dist(pytest)
BuildRequires:  python3dist(more-itertools)
BuildRequires:  time
%endif

%description
Dlib is a general purpose cross-platform open source software library written
in the C++ programming language. Its design is heavily influenced by ideas from
design by contract and component-based software engineering. It contains
components for dealing with networking, threads, graphical user interfaces,
data structures, linear algebra, machine learning, image processing, data
mining, XML and text parsing, numerical optimization, Bayesian networks, and
numerous other tasks.


%package devel
Summary:        Development files for dlib
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Dlib is a general purpose cross-platform open source software library written
in the C++ programming language. This package contains development files for
the library.


%package -n python3-%{name}
Summary:        Python 3 interface to %{name}

%description -n python3-%{name}
Dlib is a general purpose cross-platform open source software library written
in the C++ programming language. This package contains the Python 3 API for
the library.


%package doc
Summary:        Documentation for dlib
License:        CC0-1.0 AND CC-BY-SA-3.0
Requires:       %{name} = %{version}-%{release}
BuildArch:      noarch

%description doc
Dlib is a general purpose cross-platform open source software library written
in the C++ programming language. This package contains the library
documentation and example programs.


%prep
%autosetup -n %{gh_name}-%{version} -p1

# Sanitize permissions on tree contents the upstream archive ships +x.
find docs -type f -exec chmod 644 {} +
find examples -type f -exec chmod 644 {} +

# Remove empty doc files (cause rpmlint zero-length-file warnings).
find docs/docs -size 0 -print -delete

# Move license / attribution files out of examples/ so %%license picks
# them up from the spec root rather than via %%doc examples/.
mv -v examples/LICENSE_FOR_EXAMPLE_PROGRAMS.txt .
mv -v examples/video_frames/license.txt video_frames_license.txt

# Unbundle pybind11 — use the system pybind11-devel via cmake config.
# https://bugzilla.redhat.com/2098694
rm -r dlib/external/pybind11
sed -i 's@add_subdirectory(../../dlib/external/pybind11 pybind11_build)@find_package(pybind11 CONFIG REQUIRED)@' tools/python/CMakeLists.txt

# Do not treat warnings as errors when compiling tests.  Several -W
# diagnostics fire on Fedora's hardening flags and would otherwise abort
# the unit-test build.
sed -r -i 's/[[:space:]]+-Werror//' dlib/test/CMakeLists.txt


%generate_buildrequires
%pyproject_buildrequires


%build
# Cap parallelism — the C++ deep-learning code (especially the loss layer
# unit tests and the python bindings) is very memory-heavy at link time.
# COPR builders OOM at the default %%_smp_mflags.  See
# CLAUDE.md notes on Legion local builds (16c/32G).
%global _smp_mflags -j4

%cmake -GNinja \
  -DCMAKE_BUILD_TYPE:STRING=RelWithDebInfo \
  -DDLIB_USE_CUDA:BOOL=OFF \
  -DDLIB_JXL_SUPPORT:BOOL=ON \
  -DDLIB_USE_BLAS:BOOL=ON \
  -DDLIB_USE_LAPACK:BOOL=ON
%cmake_build

%if %{with ctest}
# Reduce optimization and debuginfo level so the unit-test binary
# (which links the whole library plus every test) fits in COPR
# memory.  17GiB -> ~6GiB peak per the Fedora dist-git notes.
CXXFLAGS="${CXXFLAGS/-O2/-O}"
CXXFLAGS="${CXXFLAGS/-g /-g1 }"

# Constrain the build to 7GiB per core so a 32GiB box runs at most 4
# parallel link jobs.  RHEL macros lack %%constrain_build / %%limit_build.
MAX_CPUS="$(($(grep MemTotal /proc/meminfo | awk '{print $2}') / $((7168 * 1024))))"
%global _smp_mflags "-j${MAX_CPUS}"

pushd dlib/test
%cmake -GNinja \
  -DDLIB_USE_CUDA:BOOL=OFF \
  -DDLIB_JXL_SUPPORT:BOOL=ON
%cmake_build
popd
%endif

# Python bindings — setup.py drives its own cmake invocation internally
# but honours CMAKE_ARGS / CFLAGS from the environment.
export CMAKE_ARGS="-DDLIB_USE_CUDA=OFF -DDLIB_JXL_SUPPORT=ON"
%pyproject_wheel


%install
%cmake_install

%pyproject_install
%pyproject_save_files %{?fedora:-l} %{name}

# Strip hidden dot-files that occasionally leak from %%pyproject_install.
find %{buildroot} -name '.*' -exec rm -rf {} +


%check
%if %{with ctest}
pushd dlib/test/redhat-linux-build
# test_ffmpeg is flaky on COPR (network probing).
./dtest --runall --no_test_ffmpeg
popd
%pytest -v
%endif


%files
%license LICENSE.txt
# dlib v20.x produces libdlib.so.20.0.1 with no SOVERSION chain — only
# the X.Y.Z symlink is shipped.  Glob the major-version stream so the
# package keeps building if upstream adds a SONAME later in 20.x.
%{_libdir}/libdlib.so.20*

%files devel
%{_libdir}/libdlib.so
%{_includedir}/dlib/
%{_libdir}/cmake/dlib/
%{_libdir}/pkgconfig/*.pc

%files -n python3-%{name} -f %{pyproject_files}
%{python3_sitearch}/_%{name}_pybind11%{python3_ext_suffix}
%doc README.md

%files doc
%doc docs/docs/
%doc examples
%license LICENSE_FOR_EXAMPLE_PROGRAMS.txt
%license video_frames_license.txt


%changelog
* Wed Jun 03 2026 Morgan Hough <morgan.hough@gmail.com> - 20.0.1-1
- Revive dlib for neurofedora COPR at upstream v20.0.1.
- Adopted from retired Fedora dist-git dlib.spec (last build 19.24.8-3
  on the F43 mass rebuild before retirement under releng/12871).
- Drop the GCC 15 patch (PR #3067 merged 2025-03; in v20 tree).
- Tests off by default (%%bcond ctest 0) — they need ~6GiB/core and
  OOM on standard COPR builders.  Enable with `--with ctest`.
- Cap %%{_smp_mflags} to -j4 to avoid OOM during the python-binding
  link stage on COPR.
