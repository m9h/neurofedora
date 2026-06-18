Name:           quit
Version:        3.4
Release:        5%{?dist}
Summary:        Quantitative Imaging Tools for MRI data processing

License:        MPL-2.0
URL:            https://github.com/spinicist/QUIT
Source0:        %{url}/archive/v%{version}/QUIT-%{version}.tar.gz
# Header-only argument parser library (not packaged in Fedora)
Source1:        https://github.com/Taywee/args/archive/refs/tags/6.4.8.tar.gz#/args-6.4.8.tar.gz
# CMake find module for bundled args library
Source2:        Findargs.cmake

BuildRequires:  cmake >= 3.12
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  InsightToolkit5-devel >= 5.3.0
BuildRequires:  eigen3-devel
BuildRequires:  ceres-solver-devel
BuildRequires:  suitesparse-devel
BuildRequires:  blas-devel
BuildRequires:  lapack-devel
# fmt v9 is bundled because QUIT relies on implicit ostream formatting removed in fmt v11
Source3:        https://github.com/fmtlib/fmt/archive/refs/tags/9.1.0.tar.gz#/fmt-9.1.0.tar.gz
BuildRequires:  json-devel

Requires:       InsightToolkit5%{?_isa}

Provides:       bundled(fmt) = 9.1.0
Provides:       bundled(args) = 6.4.8
Provides:       bundled(NumericalIntegration)

%description
QUIT (QUantitative Imaging Tools) is a collection of programs for processing
quantitative MRI data, including DESPOT, relaxometry, magnetization transfer,
perfusion, susceptibility mapping, and more. All tools are accessed via the
single 'qi' command with subcommands, similar to git or bart.

QUIT processes NIfTI format neuroimaging files and accepts sequence parameters
via JSON input.

%prep
%autosetup -n QUIT-%{version}

# Install bundled args header
tar xf %{SOURCE1}
install -p -m 0644 args-6.4.8/args.hxx External/include/

# Install cmake find module for args
install -p -m 0644 %{SOURCE2} cmake/Findargs.cmake

# Bundle fmt 9.1.0 (QUIT relies on implicit ostream formatting removed in fmt v11)
tar xf %{SOURCE3}
mv fmt-9.1.0 External/fmt

# Fix ambiguous format_to with Eigen expression templates in C++20
# Replace the custom formatter with a simple ostream-based one
sed -i '/template <typename FormatContext>/,/};/c\
    template <typename FormatContext> auto format(const QI::SSFPSequence \&s, FormatContext \&ctx) const {\
        std::ostringstream oss;\
        oss << "SSFP:\\n\\tTR: " << s.TR << "\\n\\tFA: " << (s.FA * 180. / M_PI).transpose() << "\\n\\tPhaseInc: " << (s.PhaseInc * 180. / M_PI).transpose();\
        return fmt::format_to(ctx.out(), "{}", oss.str());\
    }\
};' Source/Sequences/SSFPSequence.h
sed -i '1i #include <sstream>' Source/Sequences/SSFPSequence.h

%build
# Suppress GCC 15 -Wtemplate-body diagnostics in QUIT's own template code
export CFLAGS="%{optflags} -std=gnu17"
export CXXFLAGS="%{optflags} -Wno-template-body -include cstdint -fpermissive"
# Build bundled fmt 9.1.0 first (plain CXXFLAGS — fmt must NOT force-include Eigen)
cmake -S External/fmt -B External/fmt/build \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_builddir}/QUIT-%{version}/External/fmt/install \
    -DFMT_DOC=OFF -DFMT_TEST=OFF
%make_build -C External/fmt/build
%make_build -C External/fmt/build install
# QUIT compiles against BOTH the system Eigen (/usr/include/eigen3, 3.4) for its
# own code and ITK 5.4's bundled itkeigen (3.3.x) via ITK headers. The two Eigen
# copies share include-guard macros (EIGEN_MACROS_H etc.), so when a TU pulls ITK
# (itkeigen) before system Eigen, itkeigen 3.3.x's Quaternion.h gets compiled and
# its EIGEN_NOEXCEPT_IF(std::is_nothrow_move_*<Scalar>::value) is rejected by
# GCC 16 + -std=c++20. Force-include system Eigen first so its guards win and
# itkeigen's headers are guard-skipped (Eigen then resolves to the correct 3.4
# headers). Absolute path + added only for QUIT's own build (not fmt). Replaces
# the old _itk_eigen_patch shadow, which never overrode ITK's relative includes.
export CXXFLAGS="$CXXFLAGS -include /usr/include/eigen3/Eigen/Dense"
%cmake \
    -DCMAKE_MODULE_PATH:PATH="%{_builddir}/QUIT-%{version}/cmake" \
    -DExternal_Include_DIR:PATH="%{_builddir}/QUIT-%{version}/External/include" \
    -DBUILD_PARMESAN:BOOL=OFF \
    -Dfmt_DIR:PATH="%{_builddir}/QUIT-%{version}/External/fmt/install/lib64/cmake/fmt"
%cmake_build

%install
%cmake_install

%files
%license LICENSE.txt
%doc README.md CHANGELOG.md
%{_bindir}/qi

%changelog
* Wed Jun 18 2026 Morgan Hough <morgan.hough@gmail.com> - 3.4-5
- Actually fix the GCC16/C++20 FTBFS. Root cause: QUIT mixes system Eigen 3.4
  (its own code) and ITK 5.4's bundled itkeigen 3.3.x (via ITK headers) in the
  same TUs; their shared include-guards let itkeigen 3.3.x Quaternion.h compile
  with EIGEN_NOEXCEPT_IF(...::value), rejected by GCC 16 + c++20. Force-include
  system Eigen first (-include /usr/include/eigen3/Eigen/Dense, QUIT build only),
  so itkeigen is guard-skipped. The old _itk_eigen_patch shadow + typename sed
  were no-ops (deployed Quaternion.h has no literal typename; the shadow path
  never overrode ITK's relative includes); removed.

* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 3.4-4
- Shadow-patch ITK 5.4's bundled itkeigen/Eigen/src/Geometry/Quaternion.h:
  copy it into _itk_eigen_patch/ in %build, strip the invalid
  `typename std::is_nothrow_move_*<T>::value` typename keyword, prepend the
  patched dir to -I so it wins over /usr/include/ITK-5.4/itkeigen/.
  Add -fpermissive belt-and-suspenders. GCC 16 now enforces what was
  always invalid C++ (typename used on a non-type ::value member).

* Sat May 23 2026 Morgan Hough <morgan.hough@gmail.com> - 3.4-2
- Add missing Source2 Findargs.cmake (was referenced but never committed,
  blocking SRPM rebuild). Simple header-only find module providing
  args::args INTERFACE target.

* Mon Mar 30 2026 Morgan Hough <morgan.hough@gmail.com> - 3.4-1
- Initial package for Fedora
