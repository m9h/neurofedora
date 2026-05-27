Name:           python-narwhals
Version:        2.21.2
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        Extremely lightweight compatibility layer between dataframe libraries

# Check if the automatically generated License and its spelling is correct for Fedora
# https://docs.fedoraproject.org/en-US/packaging-guidelines/LicensingGuidelines/
License:        MIT
URL:            https://github.com/narwhals-dev/narwhals
Source:         %{pypi_source narwhals}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'narwhals' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-narwhals
Summary:        %{summary}

%description -n python3-narwhals %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras
%pyproject_extras_subpkg -n python3-narwhals cudf,dask,duckdb,ibis,modin,pandas,polars,pyarrow,pyspark,pyspark-connect,sql,sqlframe


%prep
%autosetup -p1 -n narwhals-%{version}


%generate_buildrequires
# Only enable extras whose deps are actually packaged in Fedora.
# Dropped: cudf (NVIDIA), duckdb, ibis, modin, polars, pyspark, pyspark-connect,
# sql, sqlframe — none of these python3-<x> exist in Fedora F44/rawhide.
%pyproject_buildrequires -x dask,pandas,pyarrow


%build
%pyproject_wheel


%install
%pyproject_install
# For official Fedora packages, including files with '*' +auto is not allowed
# Replace it with a list of relevant Python modules/globs and list extra files in %%files
%pyproject_save_files '*' +auto


%check
%_pyproject_check_import_allow_no_modules -t


%files -n python3-narwhals -f %{pyproject_files}


%changelog

* Wed May 27 2026 Morgan Hough <morgan.hough@gmail.com> - 2.21.2-
- Trim -x extras to dask,pandas,pyarrow (only ones packaged in Fedora).
  Dropped polars, cudf, duckdb, ibis, modin, pyspark, sql, sqlframe.
%autochangelog
