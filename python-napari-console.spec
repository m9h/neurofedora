Name:           python-napari-console
Version:        0.1.4
Release:        2%{?dist}
Summary:        Embedded IPython/Qt console for napari

License:        BSD-3-Clause
URL:            https://github.com/napari/napari-console
Source0:        %{pypi_source napari_console}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# A Qt binding must be importable for the %check (qtconsole/qtpy).
BuildRequires:  python3-pyqt6

%global _description %{expand:
napari-console provides the embedded interactive IPython/Qt console used by the
napari viewer, giving access to the running viewer, layers and namespace from a
REPL inside the GUI.}

%description %{_description}

%package -n python3-napari-console
Summary:        %{summary}
%description -n python3-napari-console %{_description}

%prep
%autosetup -n napari_console-%{version}

# Relax the conservative `ipykernel<7` upper cap: Fedora rawhide ships
# ipykernel 7.x and upstream main has already dropped this bound (the code is
# ipykernel-7 compatible). Without this, the package FTBFS on rawhide.
sed -i 's/ipykernel>=5.2.0,<7/ipykernel>=5.2.0/' pyproject.toml

%generate_buildrequires
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files napari_console

# No %check: napari-console imports `napari` at module top level, but napari
# (the chain root) depends back on napari-console — a build-time circular
# dependency. napari is always present at runtime (napari-console is only ever
# imported from within the napari viewer), so the missing build-time import
# check is safe. The import is exercised by the napari package's own smoke test.

%files -n python3-napari-console -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.4-2
- Relax the ipykernel<7 cap so the package builds on rawhide (ipykernel 7.x);
  upstream main already dropped the bound.

* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.4-1
- Initial package: napari-console 0.1.4 (napari embedded IPython/Qt console).
- Tier-1 of the napari packaging chain. Deps (IPython, ipykernel, qtconsole,
  qtpy) all in Fedora; ipykernel 6.29 satisfies the <7 cap.
