%global pypi_name connected-components-3d
%global dist_name connected_components_3d
%global import_name cc3d

Name:           python-%{pypi_name}
Version:        4.0.0
Release:        1%{?dist}
Summary:        Connected component labeling for 2D and 3D images

# The C++/Cython sources and the Python wrapper are LGPL-3.0-or-later.
License:        LGPL-3.0-or-later
URL:            https://github.com/seung-lab/connected-components-3d
Source0:        %{pypi_source %{dist_name}}
# The PyPI sdist omits the license files; take them from the upstream git tree.
Source1:        %{url}/raw/master/COPYING#/%{pypi_name}-COPYING
Source2:        %{url}/raw/master/COPYING.LESSER#/%{pypi_name}-COPYING.LESSER

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  gcc-c++

%global _description %{expand:
cc3d performs connected component labeling (CCL) on 2D and 3D binary and
multi-label images, using a 3D variant of the two-pass union-find algorithm
with decision trees. It handles 4/8-connectivity in 2D and 6/18/26-connectivity
in 3D, labels every distinct value of a multi-label volume in a single pass,
and provides helpers for extracting statistics, largest components and dust
removal.

The implementation is C++ with a Cython binding, so labeling large volumes
stays fast and memory-efficient.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{dist_name}-%{version}
cp -p %{SOURCE1} COPYING
cp -p %{SOURCE2} COPYING.LESSER

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{import_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license COPYING COPYING.LESSER
%doc README.md

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 4.0.0-1
- Initial package. Connected-component dependency of acvl-utils, part of the
  nnInteractive dependency chain.
