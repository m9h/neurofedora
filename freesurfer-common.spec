Name:           freesurfer-common
Version:        1.0.0
Release:        1%{?dist}
Summary:        Shared environment scripts and license tooling for FreeSurfer
License:        Apache-2.0
URL:            https://gitlab.com/morgan.hough/neurofedora

# Shell environment hooks loaded from /etc/profile.d. They pick which
# parallel-installed FreeSurfer version is active based on
#   $HOME/.freesurfer/version → /etc/freesurfer/default-version → newest installed.
Source0:        freesurfer.sh
Source1:        freesurfer.csh

# License install tool. Drops a user-provided FreeSurfer license at
# /etc/freesurfer/license.txt and sym-links it from every installed
# /usr/lib/freesurfer-<ver>/license.txt.
Source2:        freesurfer-license-install

BuildArch:      noarch

Requires:       /bin/bash

%description
freesurfer-common owns the system-level pieces shared by every parallel
FreeSurfer install:

  * /etc/profile.d/freesurfer.{sh,csh} — sets $FREESURFER_HOME and sources
    SetUpFreeSurfer per shell login, honouring per-user pins.

  * /etc/freesurfer/ — config dir holding default-version and license.txt.

  * /usr/bin/freesurfer-license-install — drop a FreeSurfer license file
    into the right place with the right perms (system-wide or per-user),
    with format validation.

This package contains no FreeSurfer code or data. Install it alongside
freesurfer7 and/or freesurfer8 (whichever parallel versions you need).

%prep
# Nothing to extract.

%build
# Nothing to compile.

%install
# Shell profile hooks
install -d -m 0755 %{buildroot}%{_sysconfdir}/profile.d
install -p -m 0644 %{SOURCE0} %{buildroot}%{_sysconfdir}/profile.d/freesurfer.sh
install -p -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/profile.d/freesurfer.csh

# License install tool
install -d -m 0755 %{buildroot}%{_bindir}
install -p -m 0755 %{SOURCE2} %{buildroot}%{_bindir}/freesurfer-license-install

# Config dir — empty; user populates license.txt and default-version
install -d -m 0755 %{buildroot}%{_sysconfdir}/freesurfer

%post
cat <<'EOF'

freesurfer-common installed.

Next steps:
  1) Install at least one FreeSurfer version (freesurfer7 and/or freesurfer8).
  2) Get a license from https://surfer.nmr.mgh.harvard.edu/registration.html
  3) Install the license once:
         sudo freesurfer-license-install ~/Downloads/license.txt
  4) (Optional) For synth tools, also:
         sudo dnf install freesurfer-fspython
         sudo freesurfer-synth-setup
  5) Open a new shell — $FREESURFER_HOME will be set automatically and
     SetUpFreeSurfer is sourced from /etc/profile.d/freesurfer.sh.

To pin a non-default version system-wide:
    echo 7.4.1 | sudo tee /etc/freesurfer/default-version
Per-user:
    mkdir -p ~/.freesurfer && echo 7.4.1 > ~/.freesurfer/version

EOF

%files
%{_bindir}/freesurfer-license-install
%{_sysconfdir}/profile.d/freesurfer.sh
%{_sysconfdir}/profile.d/freesurfer.csh
%dir %attr(0755, root, root) %{_sysconfdir}/freesurfer
# license.txt and default-version are NOT owned by the RPM — user-created.

%changelog
* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.0-1
- Initial package.
- /etc/profile.d/freesurfer.{sh,csh} set FREESURFER_HOME and source
  SetUpFreeSurfer per shell. Selection order: $HOME/.freesurfer/version,
  /etc/freesurfer/default-version, newest installed.
- /usr/bin/freesurfer-license-install drops a user-provided FS license
  at /etc/freesurfer/license.txt (or ~/.freesurfer/license.txt with --user)
  and sym-links every installed /usr/lib/freesurfer-*/license.txt to it.
- Validates the 4-line FreeSurfer-license format unless --force is given.
