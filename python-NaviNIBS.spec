%global pypi_name NaviNIBS

Name:           python-NaviNIBS
Version:        0.2.4
Release:        1%{?dist}
Summary:        Software for neuronavigated non-invasive brain stimulation

License:        LGPL-3.0-only
URL:            https://github.com/PrecisionNeuroLab/NaviNIBS
Source0:        %{pypi_source %{pypi_name} %{version} tar.gz}
# The PyPI sdist (poetry) does not bundle the license text; take it from the repo.
Source1:        https://raw.githubusercontent.com/PrecisionNeuroLab/NaviNIBS/v%{version}/LICENSE.txt

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
# The upstream poetry pin caps Python at <3.14 (a conservative convention, no
# code reason). Relax it so the package builds and runs on Fedora's Python 3.14.
sed -i 's/">=3.12,<3.14"/">=3.12,<3.15"/' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}
install -Dpm0644 %{SOURCE1} -t %{buildroot}%{_licensedir}/python3-%{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license %{_licensedir}/python3-%{pypi_name}/LICENSE.txt
%doc README.md

%changelog
* Wed Jul 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.4-1
- Initial package (deps of NaviNIBS packaged alongside); relax <3.14 python cap
