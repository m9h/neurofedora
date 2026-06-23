Name:           python-napari-svg
Version:        0.2.1
Release:        1%{?dist}
Summary:        SVG reader/writer plugin for napari

License:        BSD-3-Clause
URL:            https://github.com/napari/napari-svg
Source0:        %{pypi_source napari_svg}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
napari-svg is napari's built-in SVG layer reader and writer: it serialises image,
shapes, points and vector layers to SVG and reads them back. It is a required
plugin for a working napari install.}

%description %{_description}

%package -n python3-napari-svg
Summary:        %{summary}
%description -n python3-napari-svg %{_description}

%prep
%autosetup -n napari_svg-%{version}

%generate_buildrequires
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files napari_svg

%check
%pyproject_check_import

%files -n python3-napari-svg -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.1-1
- Initial package: napari-svg 0.2.1 (napari SVG layer I/O plugin).
- Tier-1 of the napari packaging chain. Depends on vispy.
