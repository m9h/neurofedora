Name:           tclap
Version:        1.2.5
Release:        1%{?dist}
Summary:        Templatized C++ Command Line Parser Library (header-only)

License:        MIT
URL:            https://tclap.sourceforge.net/
Source0:        https://downloads.sourceforge.net/project/tclap/tclap-%{version}.tar.gz

BuildArch:      noarch

%description
TCLAP is a small, flexible, header-only C++ library that provides a simple
interface for defining and accessing command-line arguments.

%package        devel
Summary:        Header files for the TCLAP command-line parser library
Provides:       tclap-static = %{version}-%{release}

%description    devel
Header files for TCLAP, a header-only templatized C++ command-line argument
parser library.

%prep
%autosetup

%build
# Header-only: nothing to compile.

%install
# Install the headers directly (avoids the autotools doc/example build).
mkdir -p %{buildroot}%{_includedir}
cp -a include/tclap %{buildroot}%{_includedir}/
# pkg-config file.
mkdir -p %{buildroot}%{_libdir}/pkgconfig
cat > %{buildroot}%{_libdir}/pkgconfig/tclap.pc <<EOF
prefix=%{_prefix}
includedir=%{_includedir}

Name: tclap
Description: Templatized C++ Command Line Parser
Version: %{version}
Cflags: -I\${includedir}
EOF

%files devel
%license COPYING
%doc README
%{_includedir}/tclap/
%{_libdir}/pkgconfig/tclap.pc

%changelog
* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 1.2.5-1
- Initial package: header-only TCLAP command-line parser (Anima dependency).
