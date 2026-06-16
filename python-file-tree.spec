%global pypi_name file_tree

Name:           python-file-tree
Version:        1.6.1
Release:        1%{?dist}
Summary:        Describe and manipulate structured directories of files in Python

License:        MIT
URL:            https://git.fmrib.ox.ac.uk/fsl/file-tree
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%description
file-tree provides a way to describe a structured directory of files using a
simple text "tree" format, and then to read, query and create those files
from Python. It is used by FSL tools (e.g. pyfix) to manage their inputs and
outputs.

%package -n python3-file-tree
Summary:        %{summary}

%description -n python3-file-tree
file-tree describes and manipulates structured directories of files.

%prep
%autosetup -n %{pypi_name}-%{version}
# Upstream pins uv_build <0.9.0; Fedora ships 0.11.x (API-compatible for this
# simple package). Relax the upper bound so the build backend resolves.
sed -i 's/uv_build>=0.8.7,<0.9.0/uv_build>=0.8.7/' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files file_tree

%check
%pyproject_check_import

%files -n python3-file-tree -f %{pyproject_files}
%doc README.md

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 1.6.1-1
- Initial package (pyfix dependency).
