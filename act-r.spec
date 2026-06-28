%global debug_package %{nil}
# ACT-R has no conventional release tarballs: CMU publishes a single rolling
# source archive (actr7.x.zip) whose real identity is the embedded SVN revision
# and release tag (see framework/version-string.lisp). We therefore snapshot
# that archive into a reproducible, versioned tarball. To regenerate Source0:
#
#   curl -L --ciphers 'DEFAULT@SECLEVEL=0' -o actr7.x.zip \
#       https://act-r.psy.cmu.edu/actr7.x/actr7.x.zip
#   unzip -q actr7.x.zip && mv actr7.x act-r-%%{version}
#   tar --sort=name --owner=0 --group=0 --numeric-owner \
#       --mtime='%%{reltag} 00:00:00' -cf - act-r-%%{version} \
#       | gzip -n -9 > act-r-%%{version}-svn%%{svnrev}.tar.gz
#
%global svnrev 3469
%global reltag 2025-08-11

Name:           act-r
Version:        7.31
Release:        1%{?dist}
Summary:        ACT-R cognitive architecture (Common Lisp implementation)

License:        LGPL-2.1-or-later
URL:            https://act-r.psy.cmu.edu/
# Snapshot of the official CMU actr7.x distribution, SVN r%%{svnrev} (%%{reltag}).
# See the comment above for the exact regeneration procedure.
Source0:        act-r-%{version}-svn%{svnrev}.tar.gz

BuildArch:      noarch
# ACT-R is interpreted/compiled at load time by a Common Lisp; SBCL is the
# free Lisp used by the launcher.
Requires:       sbcl
# The ACT-R Environment (GUI inspector/debugger) is Tcl/Tk based.
Recommends:     tcl
Recommends:     tk

%description
ACT-R (Adaptive Control of Thought-Rational) is a cognitive architecture: a
theory of human cognition and a Common Lisp framework for building and running
cognitive models. It includes declarative and procedural memory, perceptual
and motor modules, the sub-symbolic activation and utility equations, a
tutorial, extensive documentation, and the ACT-R Environment GUI.

This package installs the pristine ACT-R source tree under
%{_datadir}/%{name}. Because ACT-R writes compiled Lisp files into its own
tree at load time, the "act-r" launcher seeds a writable per-user working
copy (under $XDG_DATA_HOME/act-r, default ~/.local/share/act-r) on first run
and loads ACT-R from there with SBCL.

%prep
%autosetup -n %{name}-%{version}

%build
# Nothing to build: ACT-R is compiled by the Lisp at load time.

%install
install -d %{buildroot}%{_datadir}/%{name}
# Ship the full source tree (loader, modules, framework, tutorial, examples,
# environment GUI, docs). The license is handled via %%license below.
cp -a . %{buildroot}%{_datadir}/%{name}/

# Remove prebuilt platform launcher binaries so the package stays valid noarch.
# These are precompiled GUI launchers for the ACT-R Environment (macOS/Windows/
# Linux) and Node.js examples; the Tcl/Tk Environment can be started from its
# sources, and the core (Lisp) ACT-R does not need them.
find %{buildroot}%{_datadir}/%{name} -type f \
    \( -name 'start-environment-*' -o -name 'alternate-start-environment-*' \
       -o -name '*.exe' -o -name 'html-environment-*' \) -delete

# Launcher: maintain a writable working copy because ACT-R writes .fasl files
# into its own tree during load.
install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOF'
#!/bin/bash
# ACT-R launcher (Fedora package). ACT-R compiles .fasl files into its tree at
# load time, so we run from a writable per-user copy seeded from the pristine
# system install.
ACTR_SRC="%{_datadir}/act-r"
ACTR_HOME="${ACTR_HOME:-${XDG_DATA_HOME:-$HOME/.local/share}/act-r}"
if [ ! -f "$ACTR_HOME/load-act-r.lisp" ]; then
    mkdir -p "$ACTR_HOME"
    cp -rn "$ACTR_SRC/." "$ACTR_HOME/"
fi
exec sbcl --eval "(load \"$ACTR_HOME/load-act-r.lisp\")" "$@"
EOF
chmod 0755 %{buildroot}%{_bindir}/%{name}

%files
%license docs/LGPL.txt
# README and the reference manual are shipped inside the source tree under
# %%{_datadir}/%%{name} (docs/, readme.txt); not duplicated into %%_docdir.
%{_bindir}/%{name}
%{_datadir}/%{name}

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 7.31-1
- Update to ACT-R 7.31 (CMU actr7.x SVN r3469, 2025-08-11)
- Switch Source0 from the stale asmaloney GitHub mirror to a reproducible
  snapshot of the official CMU distribution
- Correct license to LGPL-2.1-or-later (per source headers) and ship the
  bundled docs/LGPL.txt as %%license

* Sun Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 7.27.7-1
- Initial package (CMU actr7.x via asmaloney mirror)
