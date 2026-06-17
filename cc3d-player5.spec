## 4.9.0 release candidate: built from the release/4.9.0 branch tip
## (no upstream 4.9.0 tag yet). Bump %%commit0 + changelog when it advances;
## switch back to the tag and Release 1 once 4.9.0 is tagged.
%global commit0 b45b0433b198381370227864b17f15f9826d9646
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           cc3d-player5
Version:        4.9.0
Release:        0.3.rc.20260617git%{shortcommit0}%{?dist}
Summary:        CC3D Player — interactive CompuCell3D simulation viewer

# LICENSE.txt is the GNU LGPL.
License:        LGPL-3.0-or-later
URL:            https://compucell3d.org
Source0:        https://github.com/CompuCell3D/%{name}/archive/%{commit0}/%{name}-%{commit0}.tar.gz
# Helper that copies a bundled demo to a writable workspace and opens it (the
# installed demos live in a read-only dir; the Player writes a settings DB next
# to the project). Downstream addition, not from upstream.
Source1:        cc3d-demo

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

# Companion GUI to the CompuCell3D engine. It installs into the cc3d.* python
# namespace, whose root (%%{python3_sitelib}/cc3d/) is owned by
# python3-compucell3d — so we depend on it and drop our duplicate namespace
# marker (see %%install). The Player drives the engine + VTK rendering, both
# pulled in transitively by python3-compucell3d (which Requires python3-vtk).
Requires:       python3-compucell3d
# setup.py declares no install_requires; the player imports these directly.
Requires:       %{py3_dist pyqt5}
Requires:       %{py3_dist pyqtgraph}
Requires:       %{py3_dist numpy}
Requires:       %{py3_dist pandas}
Requires:       %{py3_dist deprecated}
# UserInterface imports anyio at startup; the web-fetch utility imports requests.
Requires:       %{py3_dist anyio}
Requires:       %{py3_dist requests}
Requires:       python3-vtk

%description
The CompuCell3D Player is the real-time, interactive graphical front end for
running and visualizing Cellular Potts Model simulations. It renders cell
fields, concentration fields, and vector fields via VTK, with playback
controls, configuration panels, and parameter-scan launching. It is part of
the CompuCell3D desktop experience alongside the Twedit++ editor.

Run it from the command line with the "cc3d-player5" command. Open a
simulation directly by passing its .cc3d project file with -i, e.g. the
Angiogenesis demo shipped by python3-compucell3d under the Demos subdir
BookChapterDemos_ComputationalMethodsInCellBiology/Angiogenesis/:

  cc3d-player5 -i <demo-dir>/Angiogenesis.cc3d

Without -i the Player opens an empty window (use File, Open Simulation).
Useful flags for automated runs: --numSteps N, --exitWhenDone, and
-o/--screenshotOutputDir DIR to write screenshots. A parameter-scan
launcher is also installed as cc3d-player5ParamScan.

To run a bundled demo, use the cc3d-demo helper: it copies the demo to a
writable workspace (~/cc3d-demos) and opens it, e.g.

  cc3d-demo BookChapterDemos_ComputationalMethodsInCellBiology/Angiogenesis

Run "cc3d-demo --list" to see available demos. This is needed because the
installed demos are read-only but the Player writes a per-simulation settings
file next to the project.

%prep
%autosetup -n %{name}-%{commit0}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install

# The cc3d namespace root and its (empty) cc3d/__init__.py marker are owned by
# python3-compucell3d. Remove the copy our wheel drops so the two packages do
# not both own cc3d/__init__.py.
rm -f %{buildroot}%{python3_sitelib}/cc3d/__init__.py

# The gui_scripts entry point invokes main() with no arguments, so main()'s
# `argv=None -> argv=[]` fallback made the installed `cc3d-player5` binary
# ignore ALL command-line arguments (notably -i/--input). Only `python -m
# cc3d.player5` worked, because that path calls main(sys.argv[1:]). Default the
# fallback to sys.argv[1:] so the console script honours its own arguments.
sed -i 's/^        argv = \[\]$/        argv = sys.argv[1:]/' \
    %{buildroot}%{python3_sitelib}/cc3d/player5/__main__.py
grep -q 'argv = sys.argv\[1:\]' %{buildroot}%{python3_sitelib}/cc3d/player5/__main__.py

# Force the Qt xcb (X11) platform when an X display is available. On Wayland,
# Qt picks the wayland backend while VTK still creates an X11/GLX render window;
# the two disagree and Qt dies with "X Error: BadWindow (X_ConfigureWindow)".
# Aligning Qt on xcb fixes it. This must apply to EVERY launch path, including
# Twedit's `python -m cc3d.player5 ...` handoff, so patch main() itself (the
# cc3d-demo wrapper sets it too, but the -m path bypasses the wrapper).
# Respects an explicit QT_QPA_PLATFORM and a headless (no DISPLAY) setup.
sed -i 's|^    app = CQApplication(argv)|    import os as _os\n    if _os.environ.get("DISPLAY") and "QT_QPA_PLATFORM" not in _os.environ:\n        _os.environ["QT_QPA_PLATFORM"] = "xcb"\n    app = CQApplication(argv)|' \
    %{buildroot}%{python3_sitelib}/cc3d/player5/__main__.py
grep -q 'QT_QPA_PLATFORM' %{buildroot}%{python3_sitelib}/cc3d/player5/__main__.py

# Install the cc3d-demo helper, baking in the real demos directory path.
install -Dpm0755 %{SOURCE1} %{buildroot}%{_bindir}/cc3d-demo
sed -i 's|@DEMOS_ROOT@|%{_datadir}/compucell3d/Demos|' %{buildroot}%{_bindir}/cc3d-demo

%files
%license LICENSE.txt
%doc README.rst ReleaseNotes.rst
%{_bindir}/cc3d-player5
%{_bindir}/cc3d-player5ParamScan
%{_bindir}/cc3d-demo
# Own only our namespace subpackage + dist metadata, NOT the cc3d/ root.
%{python3_sitelib}/cc3d/player5/
%{python3_sitelib}/cc3d_player5-%{version}.dist-info/

%changelog
* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9.0-0.3.rc.20260617gitb45b043
- Force Qt xcb platform when an X display is present: on Wayland, Qt used the
  wayland backend while VTK created an X11/GLX window, killing the Player with
  "X Error: BadWindow (X_ConfigureWindow)" (notably when Twedit launched it via
  python -m cc3d.player5). Patch main() so all launch paths get xcb.

* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9.0-0.2.rc.20260617gitb45b043
- Rebuild to deliver the -i entry-point fix, anyio+requests Requires, and the
  cc3d-demo launcher; 0.1 was never bumped across rebuilds so dnf would not
  upgrade past the first incomplete build. No source change (same commit).

* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9.0-0.1.rc.20260615gitb45b043
- Update to 4.9.0 release candidate (release/4.9.0 branch, commit b45b043;
  no upstream 4.9.0 tag yet, so packaged as a pre-release snapshot)
- Fix the installed cc3d-player5 entry point ignoring all command-line args:
  the gui_scripts wrapper calls main() with no argv, so main()'s argv=[] fallback
  dropped -i/--input (sim never loaded -> "Not A Valid Simulation File" on Run).
  Default the fallback to sys.argv[1:].
- Require anyio + requests (imported at startup / by the web-fetch utility)
- Add cc3d-demo helper: copies a bundled demo to a writable workspace and opens
  it (installed demos are read-only; the Player writes a per-sim settings DB
  next to the project). Sets QT_QPA_PLATFORM=xcb when an X display is present to
  avoid a harmless X BadWindow from the Qt5-player + Qt6-VTK combination.
- Document the command-line invocation (cc3d-player5 -i <project>.cc3d) and
  the Angiogenesis example path in the package description

* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 4.8.0-1
- Initial package: CC3D Player visualization companion for CompuCell3D 4.8.0.
- noarch Python app installing into the cc3d.player5 namespace; depends on
  python3-compucell3d for the cc3d namespace root (and transitive VTK) and
  drops the duplicate cc3d/__init__.py marker to avoid file-ownership conflict.
