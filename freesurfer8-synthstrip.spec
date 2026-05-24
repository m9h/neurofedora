%global fs_ver        8.2.0
%global fs_install    %{_prefix}/lib/freesurfer-%{fs_ver}
%global synth_data    %{_datadir}/freesurfer-%{fs_ver}/synthstrip

Name:           freesurfer8-synthstrip
Version:        %{fs_ver}
Release:        1%{?dist}
Summary:        SynthStrip skull-stripping tool from FreeSurfer 8.2.0

# Inherits FreeSurfer's custom non-OSI license.
License:        FreeSurfer
URL:            https://surfer.nmr.mgh.harvard.edu/docs/synthstrip/
Source0:        https://github.com/freesurfer/freesurfer/archive/refs/tags/v%{fs_ver}.tar.gz#/freesurfer-%{fs_ver}.tar.gz

BuildArch:      noarch
BuildRequires:  /bin/sh

# Runtime — Python env supplied via fspython, model weights fetched by user.
Requires:       freesurfer-fspython
Requires:       freesurfer8 = %{fs_ver}
# The synthstrip wrapper expects `surfa` and `torch` inside the venv; both
# are pulled in by freesurfer-synth-setup's pin files, so no explicit
# Python-dist Requires here.

# SynthStrip's model weights are git-annex'd in upstream and not in the
# GitHub tarball — installed separately by the user (see %post message).

%description
SynthStrip is a skull-stripping tool from FreeSurfer 8.2.0 that works
across MRI contrasts using a PyTorch deep-learning model.

This package installs only the wrapper script. Python runtime is provided
by freesurfer-fspython (run `freesurfer-synth-setup` once after install).
Model weights are not in the upstream source tarball; the wrapper
downloads them to ~/.cache/freesurfer on first use.

%prep
%setup -q -n freesurfer-%{fs_ver}
# Keep only the synthstrip directory; the rest of the tarball isn't needed.
# (We unpack the whole thing because GitHub doesn't support sparse exports,
# but everything else is unused and gets discarded at %install time.)

%build
# Nothing to build — the wrapper is a Python script.

%install
install -d %{buildroot}%{fs_install}/bin
install -p -m 0755 mri_synthstrip/mri_synthstrip \
    %{buildroot}%{fs_install}/bin/mri_synthstrip

# Patch the shebang so the script invokes our fspython launcher
sed -i '1s|^#!.*$|#!/usr/bin/fspython|' \
    %{buildroot}%{fs_install}/bin/mri_synthstrip

# Symlink into /usr/bin only when this is the default FS major (i.e., the
# only one installed). The freesurfer8 main package owns the version-
# qualified alternative; here we just install the script in-place.

# Data dir for any model weights the user later drops in
install -d %{buildroot}%{synth_data}

%post
cat <<'EOF'

freesurfer8-synthstrip installed at:
    %{fs_install}/bin/mri_synthstrip

Before first use, ensure the synth Python env is initialised:
    sudo freesurfer-synth-setup

Model weights are not bundled (git-annex in upstream). On first run,
mri_synthstrip will download synthstrip.*.pt to ~/.cache/freesurfer.

EOF

%files
%{fs_install}/bin/mri_synthstrip
%dir %{synth_data}

%changelog
* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-1
- Initial package — proof-of-concept synth subpackage for FreeSurfer 8.2.0.
- Ships only the wrapper script; Python runtime via freesurfer-fspython,
  model weights downloaded by the tool on first use (git-annex upstream).
