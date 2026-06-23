Name:           python-app-model
Version:        0.5.1
Release:        1%{?dist}
Summary:        Generic application model: commands, menus, keybindings, actions

License:        BSD-3-Clause
URL:            https://github.com/pyapp-kit/app-model
Source0:        %{pypi_source app_model}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
app-model is a declarative, backend-agnostic application model: a registry of
commands, menus, keybindings and actions with a typed, injectable execution
layer (via in-n-out). napari builds its command system on top of it.}

%description %{_description}

%package -n python3-app-model
Summary:        %{summary}

%description -n python3-app-model %{_description}

%prep
%autosetup -n app_model-%{version}

%generate_buildrequires
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files app_model

%check
# app_model.backends.qt is an optional Qt backend (needs the qtpy extra, not a
# core dependency) — exclude it from the smoke import.
%pyproject_check_import -e 'app_model.backends.qt'

%files -n python3-app-model -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.5.1-1
- Initial package: app-model 0.5.1.
- Tier-1 of the napari packaging chain; pinned to the 0.5.x line napari 0.7.x
  requires (app-model >=0.5.0,<0.6.0). Depends on in-n-out.
