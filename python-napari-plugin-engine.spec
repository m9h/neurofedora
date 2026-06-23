Name:           python-napari-plugin-engine
Version:        0.2.1
Release:        1%{?dist}
Summary:        Plugin discovery and hook-call manager for napari (v1 engine)

License:        MIT
URL:            https://github.com/napari/napari-plugin-engine
Source0:        %{pypi_source napari_plugin_engine}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
napari-plugin-engine is napari's original (v1) pluggy-style plugin manager:
hook specifications, implementations and call ordering. Current napari still
ships it alongside the newer npe2 engine, so both are required to run napari.}

%description %{_description}

%package -n python3-napari-plugin-engine
Summary:        %{summary}

%description -n python3-napari-plugin-engine %{_description}

%prep
%autosetup -n napari_plugin_engine-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files napari_plugin_engine

%check
%pyproject_check_import

%files -n python3-napari-plugin-engine -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.1-1
- Initial package: napari-plugin-engine 0.2.1 (napari v1 plugin manager).
- Tier-0 leaf of the napari packaging chain; still required by current napari
  in addition to npe2.
