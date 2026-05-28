Name:           python-py-undo-stack
Version:        1.1.0
Release:        1%{?dist}
Summary:        Pure-Python undo / redo command stack

License:        BSD-3-Clause
URL:            https://pypi.org/project/py-undo-stack/
Source:         %{pypi_source py_undo_stack}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
py-undo-stack is a small pure-Python library implementing a generic
undo/redo command stack. Used by trame-slicer for action history and
by other Kitware trame-based applications.}

%description %_description

%package -n     python3-py-undo-stack
Summary:        %{summary}

%description -n python3-py-undo-stack %_description

%prep
%autosetup -p1 -n py_undo_stack-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files undo_stack

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-py-undo-stack -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Thu May 28 2026 Morgan Hough <morgan.hough@gmail.com> - 1.1.0-1
- Initial package for the trame-slicer dependency chain.
