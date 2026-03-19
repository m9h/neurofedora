Name:           bart
Version:        1.0.00
Release:        1%{?dist}
Summary:        The Berkeley Advanced Reconstruction Toolbox (BART)

License:        BSD-3-Clause
URL:            https://github.com/mrirecon/bart
Source0:        %{url}/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  fftw-devel
BuildRequires:  openblas-devel
BuildRequires:  lapack-devel
BuildRequires:  libpng-devel
BuildRequires:  execstack
# The Makefile says it requires make 4.0 or newer. Fedora has it.

%description
The Berkeley Advanced Reconstruction Toolbox (BART) is a free and open-source
image-reconstruction framework for Computational Magnetic Resonance Imaging.
It consists of a library and a toolbox with many command-line algorithms
for MRI reconstruction, such as SENSE, POCS-enhanced SPIRiT, and 
compressed sensing.

%prep
%autosetup -n %{name}-%{version}
# Remove hardcoded rpath and -L/usr/lib which causes issues on Fedora
sed -i 's|BLAS_L := -Wl,-rpath $(BLAS_BASE)/lib -L$(BLAS_BASE)/lib|BLAS_L :=|' Makefile
sed -i 's|FFTW_L :=  -Wl,-rpath $(FFTW_BASE)/lib -L$(FFTW_BASE)/lib -lfftw3f|FFTW_L := -lfftw3f|' Makefile
# Include assert.h in nested.h for NOEXEC_STACK support
sed -i '1i #include <assert.h>' src/misc/nested.h

%build
# BART's Makefile uses PREFIX for install, but not necessarily for build.
# We can use Makefile.local to configure.
cat > Makefile.local <<EOF
PREFIX=%{_prefix}
PARALLEL=1
OPENBLAS=1
FFTWTHREADS=1
NOEXEC_STACK=1
CPPFLAGS += -I%{_includedir}/openblas
EOF
%make_build

%install
%make_install PREFIX=%{_prefix}

# Clear executable stack flag. BART has a workaround for non-executable stack (NOEXEC_STACK=1)
# but GCC still marks objects as needing it because of nested functions.
execstack -c %{buildroot}%{_bindir}/bart

# The install target in the Makefile seems a bit incomplete for Fedora standards
# It doesn't install the man page.
mkdir -p %{buildroot}%{_mandir}/man1
install -p -m 644 doc/bart.1 %{buildroot}%{_mandir}/man1/

# The Makefile installs to %{_prefix}/share/doc/bart/ which is not where we want it in Fedora.
# Fedora uses %{_docdir}/%{name} which %doc takes care of.
# Let's remove the one installed by Makefile
rm -rf %{buildroot}%{_prefix}/share/doc/bart/

%check
# Basic sanity check
# We need to make sure it doesn't segfault without executable stack
./bart version

%files
%license LICENSE
%doc README README.md doc/*.txt
%{_bindir}/bart
%{_mandir}/man1/bart.1*
%dir %{_prefix}/lib/bart
%dir %{_prefix}/lib/bart/commands

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.00-1
- Initial BART package
