%global pypi_name pyactr

Name:           python-%{pypi_name}
Version:        0.3.2
Release:        1%{?dist}
Summary:        ACT-R cognitive architecture implemented in Python

# Upstream classifies as GPLv3; the PyPI sdist omits the license text, so the
# upstream LICENSE (GPLv3) is shipped as Source1.
License:        GPL-3.0-only
URL:            https://github.com/jakdot/pyactr
Source0:        %{pypi_source}
Source1:        pyactr-LICENSE

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
pyactr is a Python implementation of the ACT-R cognitive architecture. It
allows you to create and run ACT-R models entirely in Python, including
declarative and procedural memory, buffers, and the sub-symbolic activation
equations, and to interface models with a simulated environment.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}
cp -p %{SOURCE1} LICENSE
# Docs ship with spurious executable bits in the sdist.
chmod 0644 README.txt docs/*.pdf

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.txt docs/book_manual.pdf docs/actrparameters.pdf

%changelog
* Sun Jun 21 2026 Morgan Hough <morgan.hough@gmail.com> - 0.3.2-1
- Initial package
