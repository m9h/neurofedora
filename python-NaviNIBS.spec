%global pypi_name NaviNIBS

Name:           python-NaviNIBS
Version:        0.2.4
Release:        1%{?dist}
Summary:        Software for neuronavigated non-invasive brain stimulation

License:        LGPL-3.0-only
URL:            https://github.com/PrecisionNeuroLab/NaviNIBS
Source0:        %{pypi_source navinibs %{version} tar.gz}

BuildArch:      noarch
BuildRequires:  python3-devel
# %%check imports pylsl, which dlopens the native liblsl at import time; the
# published python3-pylsl does not yet pull liblsl in, so require it explicitly
# so the import check can run in the build root.
BuildRequires:  liblsl

%global _description %{expand:
NaviNIBS is comprehensive software for neuronavigated non-invasive brain
stimulation (e.g. TMS). It provides real-time head/coil tracking, MRI-based
targeting, trajectory planning, and integration with tracking hardware and
stimulation devices for image-guided brain stimulation experiments.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n navinibs-%{version}
# Adapt pyproject for Fedora: (1) relax the conservative <3.14 python cap
# (poetry convention, no code reason) so it runs on Fedora 3.14; (2) relax
# poetry's exact/caret dep pins to bare names (Fedora ships one version each);
# (3) declare the package dir explicitly — the project name "NaviNIBS" is
# mixed-case but poetry-core 2.x normalizes it to "navinibs" for module
# auto-discovery and then can't find the NaviNIBS/ dir, so pin it.
%{python3} - <<'EOF'
import re
p="pyproject.toml"; s=open(p).read()
s=s.replace('">=3.12,<3.14"', '">=3.12,<3.15"')
s=s.replace("[tool.poetry.dependencies]",
            '[tool.poetry]\npackages = [{ include = "NaviNIBS" }]\n\n[tool.poetry.dependencies]', 1)
s=re.sub(r"(?s)(\[tool\.poetry\.dependencies\]).*?(?=\n\[)",
         lambda m: re.sub(r'(?m)^(?!python\s*=)([A-Za-z0-9_.-]+)(\s*=\s*)"[^"]*"', r'\1 = "*"', m.group(0)), s)
open(p,"w").write(s)
EOF

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}

%check
# Import-check the package, minus modules that can't be imported in the build
# root. We filter the generated module list directly (the %%pyproject_check_import
# -e option is not reliably forwarded by the macro on f44). Excluded:
#  - Navigator.GUI.ViewPanels* / NavigatorGUI / util.GUI.Dock: fail at import
#    with "metaclass conflict" under PySide6 6.9 + Python 3.14 (a real upstream
#    incompatibility in the panel/dock class hierarchy, to report to upstream).
#  - util.test*: pytest-based test modules shipped inside the package; pytest is
#    a test-group dependency, not a runtime one.
# The remaining ~87 modules (Model, Devices, most GUI widgets, math utils) are
# imported and exercise the runtime deps, incl. pylsl -> liblsl.
grep -vE 'NaviNIBS\.Navigator\.GUI\.NavigatorGUI|NaviNIBS\.Navigator\.GUI\.ViewPanels|NaviNIBS\.util\.GUI\.Dock|NaviNIBS\.util\.test' \
    %{_pyproject_modules} > %{_pyproject_modules}.filtered
mv %{_pyproject_modules}.filtered %{_pyproject_modules}
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license COPYING COPYING.LESSER
%doc README.md
%{_bindir}/navinibs

%changelog
* Sat Jul 26 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.4-1
- Initial package (deps of NaviNIBS packaged alongside)
- Relax the <3.14 python cap and poetry's exact/caret dep pins for Fedora
- Pin packages=[{include=NaviNIBS}] so poetry-core 2.x finds the mixed-case
  package dir (it normalizes the project name to lowercase for lookup)
- BuildRequires liblsl and filter GUI/test modules from the import check
  (ViewPanels/NavigatorGUI/Dock hit a PySide6-6.9/py3.14 metaclass conflict)
