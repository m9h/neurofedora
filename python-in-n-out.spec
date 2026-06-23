Name:           python-in-n-out
Version:        0.2.1
Release:        1%{?dist}
Summary:        Type-based dependency injection for Python

License:        BSD-3-Clause
URL:            https://github.com/pyapp-kit/in-n-out
Source0:        %{pypi_source in_n_out}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
in-n-out is a small, dependency-free type-based dependency-injection and
provider/processor registry. It is the injection container underneath
app-model (and thus napari's command system).}

%description %{_description}

%package -n python3-in-n-out
Summary:        %{summary}

%description -n python3-in-n-out %{_description}

%prep
%autosetup -n in_n_out-%{version}

%generate_buildrequires
# hatch-vcs derives the version from git; the sdist has no .git, so pin it.
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files in_n_out

%check
%pyproject_check_import

%files -n python3-in-n-out -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.1-1
- Initial package: in-n-out 0.2.1 (dependency-free DI container).
- Tier-0 leaf of the napari packaging chain (required by app-model).
