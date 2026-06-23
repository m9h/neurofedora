Name:           python-cachey
Version:        0.2.1
Release:        1%{?dist}
Summary:        Caching based on computation/storage cost and recency

License:        BSD-3-Clause
URL:            https://github.com/dask/cachey
Source0:        %{pypi_source cachey}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
cachey is a small caching library that scores cached objects by a mix of
computation cost, storage cost and recency, evicting the least valuable. napari
uses it to cache rendered/loaded data.}

%description %{_description}

%package -n python3-cachey
Summary:        %{summary}

%description -n python3-cachey %{_description}

%prep
%autosetup -n cachey-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files cachey

%check
%pyproject_check_import

%files -n python3-cachey -f %{pyproject_files}
%license LICENSE.txt
%doc README.md

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.2.1-1
- Initial package: cachey 0.2.1 (cost/recency-scored cache).
- Tier-0 leaf of the napari packaging chain (sole dep heapdict, already in Fedora).
