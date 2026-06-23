Name:           python-magicgui
Version:        0.10.2
Release:        1%{?dist}
Summary:        Build GUIs from type annotations

License:        MIT
URL:            https://github.com/pyapp-kit/magicgui
Source0:        %{pypi_source magicgui}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# A Qt binding must be importable for the %check import of the qtpy backend.
BuildRequires:  python3-pyqt6

%global _description %{expand:
magicgui builds graphical user interfaces from Python type annotations: decorate
a function and get a Qt widget whose controls are inferred from the argument
types. It is the widget layer used by napari and napari plugins.}

%description %{_description}

%package -n python3-magicgui
Summary:        %{summary}
%description -n python3-magicgui %{_description}

%prep
%autosetup -n magicgui-%{version}

%generate_buildrequires
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export HATCH_VCS_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files magicgui

%check
# Headless Qt for the backend import. Exclude optional integrations not pulled
# as core deps: _ipynb (Jupyter) and tqdm (progress-bar extra).
export QT_QPA_PLATFORM=offscreen
%pyproject_check_import -e 'magicgui.backends._ipynb*' -e 'magicgui.tqdm'

%files -n python3-magicgui -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.10.2-1
- Initial package: magicgui 0.10.2.
- Tier-1 of the napari packaging chain. Deps (docstring-parser, psygnal, qtpy,
  superqt[iconify]) all already in Fedora.
