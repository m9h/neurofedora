%global pypi_name yacs
%global import_name yacs

Name:           python-%{pypi_name}
Version:        0.1.8
Release:        1%{?dist}
Summary:        Lightweight YAML-based configuration system for research projects

License:        Apache-2.0
URL:            https://github.com/rbgirshick/yacs
Source0:        %{pypi_source %{pypi_name}}
# The PyPI sdist omits the license file; take it from the upstream git tree.
Source1:        %{url}/raw/master/LICENSE#/%{pypi_name}-LICENSE

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
YACS (Yet Another Configuration System) provides a lightweight, YAML-backed
configuration layer for reproducible research code. Experiments are defined by
a set of default parameters in code plus a small YAML file recording only the
deviations from those defaults, so a run is fully described by the pair.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}
cp -p %{SOURCE1} LICENSE

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{import_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.8-1
- Initial package. Configuration dependency of nnU-Net v2, part of the
  nnInteractive dependency chain.
