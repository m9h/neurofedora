Name:           quit
Version:        3.4
Release:        1%{?dist}
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
export CXXFLAGS="%{optflags} -Wno-template-body -include cstdint"
# Build bundled fmt 9.1.0 first
cmake -S External/fmt -B External/fmt/build \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=%{_builddir}/QUIT-%{version}/External/fmt/install \
    -DFMT_DOC=OFF -DFMT_TEST=OFF
%make_build -C External/fmt/build
%make_build -C External/fmt/build install
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
* Mon Mar 30 2026 Morgan Hough <morgan.hough@gmail.com> - 3.4-1
- Initial package for Fedora
