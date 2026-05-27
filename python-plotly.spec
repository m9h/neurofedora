Name:           python-plotly
Version:        6.7.0
Release:        2%{?dist}
# Fill in the actual package summary to submit package to Fedora
Summary:        An open-source interactive data visualization library for Python

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        MIT
URL:            https://plotly.com/python/
Source:         %{pypi_source plotly}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'plotly' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-plotly
Summary:        %{summary}

%description -n python3-plotly %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras
%pyproject_extras_subpkg -n python3-plotly dev,dev-build,dev-core,dev-optional,express,kaleido


%prep
%autosetup -p1 -n plotly.py-%{version}


%generate_buildrequires
# Drop all extras: their deps (anywidget, colorcet, kaleido, polars,
# plotly-geo) are not packaged in Fedora. Base plotly itself only needs
# the deps from pyproject.toml [project].
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# For official Fedora packages, including files with '*' +auto is not allowed
# Replace it with a list of relevant Python modules/globs and list extra files in %%files
%pyproject_save_files '*' +auto


%check
%_pyproject_check_import_allow_no_modules -t


%files -n python3-plotly -f %{pyproject_files}


%changelog

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 6.7.0-2
- Fix %%autosetup -n: upstream tarball expands to plotly.py-%{version},
  not plotly-%{version}.

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 6.7.0-
- Drop all -x extras: anywidget, colorcet, kaleido, polars not in Fedora.
%autochangelog
