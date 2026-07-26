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
# poetry's exact/caret dep pins to bare names (Fedora ships one version each).
%{python3} - <<'EOF'
import re
p="pyproject.toml"; s=open(p).read()
s=s.replace('">=3.12,<3.14"', '">=3.12,<3.15"')
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
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license COPYING COPYING.LESSER
%doc README.md

%changelog
* Wed Jul 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.4-1
- Initial package (deps of NaviNIBS packaged alongside); relax <3.14 python cap
