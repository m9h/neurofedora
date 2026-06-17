## 4.9.0 release candidate: built from the release/4.9.0 branch tip
## (no upstream 4.9.0 tag yet). Bump %%commit0 + changelog when it advances;
## switch back to the tag and Release 1 once 4.9.0 is tagged.
%global commit0 f54bc7f3f45c8a314215566abbafb451705431d7
%global shortcommit0 %(c=%{commit0}; echo ${c:0:7})

Name:           cc3d-twedit5
Version:        4.9.0
Release:        0.2.rc.20260617git%{shortcommit0}%{?dist}
Summary:        Twedit++ — model/Python editor (IDE) for CompuCell3D

# LICENSE.txt is the GNU LGPL.
License:        LGPL-3.0-or-later
URL:            https://compucell3d.org
Source0:        https://github.com/CompuCell3D/%{name}/archive/%{commit0}/%{name}-%{commit0}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

# Companion GUI to the CompuCell3D engine. It installs into the cc3d.* python
# namespace, whose root (%%{python3_sitelib}/cc3d/) is owned by
# python3-compucell3d — so we depend on it and drop our duplicate namespace
# marker (see %%install).
Requires:       python3-compucell3d
# setup.py declares no install_requires; the editor imports these directly.
Requires:       %{py3_dist pyqt5}
Requires:       %{py3_dist numpy}
# Twedit++ is a QScintilla-based editor (from PyQt5.Qsci import *) — hard need.
Requires:       python3-qscintilla-qt5
# Encoding detection (twedit/utils/encoding_detector.py: import chardet). The
# tree also carries a stale vendored copy under Encoding/EncodingDetector/.
Requires:       %{py3_dist chardet}

# A legacy chardet copy ships under Encoding/EncodingDetector/chardet/.
Provides:       bundled(python3-chardet)

%description
Twedit++ is the CompuCell3D integrated editor for authoring CC3D models,
Python steppables, and MorpheusML/CC3DML. It ships CC3D-aware plugins
(project wizard, snippet/template helpers, CC3DML and C++/Python helpers)
and is part of the CompuCell3D desktop experience alongside the Player.

Launch it from the command line with the "cc3d-twedit5" command.

%prep
%autosetup -n %{name}-%{commit0}

# --- Python 3.14 removed the distutils stdlib module ---
# Twedit's project-wizard plugin (PluginCCDProject.py) and the C++ helper import
# distutils, so without this the New Simulation Wizard fails to load. Replace the
# handful of uses with stdlib equivalents (os.makedirs / open / sysconfig).
sed -i -e '/^from distutils\.file_util import write_file$/d' \
       -e '/^from distutils\.dir_util import mkpath$/d' \
       -e 's#write_file(os.path.join(full_location, name), "")#open(os.path.join(full_location, name), "w").close()#' \
       -e 's#mkpath(fullDirPath)#os.makedirs(fullDirPath, exist_ok=True)#' \
    cc3d/twedit5/Plugins/PluginCCDProject.py
sed -i -e '/^from distutils\.dir_util import mkpath$/d' \
       -e 's#mkpath(fullDirPath)#os.makedirs(fullDirPath, exist_ok=True)#' \
    cc3d/twedit5/Plugins/PluginCCDCPPHelper.py
sed -i -e 's#^    import distutils.sysconfig#    import sysconfig#' \
       -e 's#^    return distutils.sysconfig.get_python_lib(True)#    return sysconfig.get_path("platlib")#' \
    cc3d/twedit5/Encoding/__init__.py
# Fail the build if any distutils import survived in the modules we patched.
! grep -rn '^\s*\(import\|from\) distutils' \
    cc3d/twedit5/Plugins/PluginCCDProject.py \
    cc3d/twedit5/Plugins/PluginCCDCPPHelper.py \
    cc3d/twedit5/Encoding/__init__.py

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

# twedit_plus_plus.py is an imported module, not an executable, but ships a
# spurious "#!/usr/bin/env python" shebang (wrong interpreter + non-exec bit).
# Strip the shebang so rpmlint does not flag non-executable-script.
sed -i '1{/^#!.*\bpython/d}' \
    %{buildroot}%{python3_sitelib}/cc3d/twedit5/twedit_plus_plus.py

%files
%license LICENSE.txt
%doc README.rst ReleaseNotes.rst
%{_bindir}/cc3d-twedit5
# Own only our namespace subpackage + dist metadata, NOT the cc3d/ root.
%{python3_sitelib}/cc3d/twedit5/
%{python3_sitelib}/cc3d_twedit5-%{version}.dist-info/

%changelog
* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9.0-0.2.rc.20260617gitf54bc7f
- Rebuild to deliver the qscintilla-qt5 + chardet Requires and the distutils
  removal patch (New Simulation Wizard); 0.1 was never bumped across rebuilds
  so dnf would not upgrade past the first incomplete build (which launched
  straight into ModuleNotFoundError). No source change (same commit).

* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 4.9.0-0.1.rc.20260615gitf54bc7f
- Update to 4.9.0 release candidate (release/4.9.0 branch, commit f54bc7f;
  no upstream 4.9.0 tag yet, so packaged as a pre-release snapshot)
- Require python3-qscintilla-qt5 (editor widget, from PyQt5.Qsci) and
  python3-chardet (encoding detection) — both were missing, Twedit would not
  even launch without QScintilla
- Patch out distutils (removed in Python 3.14) in PluginCCDProject.py,
  PluginCCDCPPHelper.py and Encoding/__init__.py so the New Simulation Wizard
  and C++ helper load; use os.makedirs / open / sysconfig instead
- Provides: bundled(python3-chardet) for the vendored copy under Encoding/
- Note the cc3d-twedit5 launch command in the package description

* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 4.8.0-1
- Initial package: Twedit++ editor companion for CompuCell3D 4.8.0.
- noarch Python app installing into the cc3d.twedit5 namespace; depends on
  python3-compucell3d for the cc3d namespace root and drops the duplicate
  cc3d/__init__.py marker to avoid file-ownership conflict.
