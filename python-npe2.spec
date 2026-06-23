Name:           python-npe2
Version:        0.8.2
Release:        1%{?dist}
Summary:        napari plugin engine, version 2

License:        BSD-3-Clause
URL:            https://github.com/napari/npe2
Source0:        %{pypi_source npe2}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
npe2 is the second-generation napari plugin engine: a static, manifest-driven
(napari.yaml) contribution system for commands, readers, writers, widgets and
sample data, with a CLI for validating and inspecting plugin manifests.}

%description %{_description}

%package -n python3-npe2
Summary:        %{summary}
%description -n python3-npe2 %{_description}

%prep
%autosetup -n npe2-%{version}

%generate_buildrequires
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files npe2

%check
%pyproject_check_import

%files -n python3-npe2 -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/npe2

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.8.2-1
- Initial package: npe2 0.8.2 (napari plugin engine v2).
- Tier-2 of the napari packaging chain. All deps in Fedora; version caps
  (pydantic !=2.11.*, rich >=14, typer >=0.15.4) satisfied on F44 and rawhide.
