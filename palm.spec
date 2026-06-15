%global commit      d937704489cc8ae8a7dafb273e421536f8b1e1a5
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate    20260608

# Pure Octave/MATLAB .m sources — nothing to compile.
%global debug_package %{nil}

Name:           palm
Version:        0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        PALM - Permutation Analysis of Linear Models

# palm.m and all sources carry a GPLv3-or-later header (Copyright 2015
# Anderson M. Winkler, FMRIB/Oxford). Upstream ships no separate LICENSE file.
License:        GPL-3.0-or-later
URL:            https://github.com/andersonwinkler/PALM
Source0:        %{url}/archive/%{commit}/PALM-%{commit}.tar.gz

BuildArch:      noarch
Requires:       octave
Requires:       bash

%description
PALM (Permutation Analysis of Linear Models) is a tool for permutation-based
inference on neuroimaging and other data. It supports voxelwise, vertexwise
(surface) and other data types, complex experimental designs, exchangeability
blocks, multiple modalities and contrasts, spatial statistics (TFCE, cluster
extent/mass), and FWER/FDR correction — making it well suited to mesh/surface
shape analysis (e.g. FSL FIRST vertex analysis).

This package runs PALM under GNU Octave; no MATLAB licence is required.

%prep
%autosetup -n PALM-%{commit}

%build
# Nothing to build (interpreted .m sources).

%install
# Ship the whole PALM tree under a private datadir.
install -d %{buildroot}%{_datadir}/palm
cp -rp *.m palm lib colourmaps %{buildroot}%{_datadir}/palm/

# Remove all prebuilt MATLAB MEX binaries (and stray .o objects). They are
# foreign-architecture MATLAB binaries that carry the upstream build machine's
# absolute rpaths (/usr/local/{FFTW,LAPACK,HDF5,gl2ps}/...) — rejected by
# Fedora's rpath check — and they do not load under Octave anyway. PALM ships
# pure-.m implementations alongside them (e.g. xml_findstr.m), which Octave uses.
find %{buildroot}%{_datadir}/palm -type f \( -name '*.mex*' -o -name '*.o' \) -delete

# Point the launcher at the system Octave and force the Octave path
# (WHICH_TO_RUN=1). The launcher resolves its own directory by following the
# symlink we install in %{_bindir}, so PALMDIR ends up at %{_datadir}/palm.
sed -i \
    -e 's|^WHICH_TO_RUN=.*|WHICH_TO_RUN=1|' \
    -e 's|^OCTAVEBIN=.*|OCTAVEBIN=%{_bindir}/octave|' \
    %{buildroot}%{_datadir}/palm/palm
chmod 0755 %{buildroot}%{_datadir}/palm/palm

# Absolute symlink so the launcher's readlink resolution sets PALMDIR correctly.
install -d %{buildroot}%{_bindir}
ln -s %{_datadir}/palm/palm %{buildroot}%{_bindir}/palm

%check
test -x %{buildroot}%{_datadir}/palm/palm
test -f %{buildroot}%{_datadir}/palm/palm.m
grep -q '^OCTAVEBIN=%{_bindir}/octave' %{buildroot}%{_datadir}/palm/palm

%files
%doc README.md
%{_bindir}/palm
%{_datadir}/palm/

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 0-0.1.20260608gitd937704
- Initial package: PALM permutation inference (master snapshot d937704), run
  under GNU Octave. Launcher patched to use the system octave; installed under
  %%{_datadir}/palm with a /usr/bin/palm symlink. Enables vertex-wise
  permutation statistics for the FSL FIRST mesh shape-analysis workflow.
