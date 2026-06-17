Name:           python-simservice
Version:        0.1.1
Release:        1%{?dist}
Summary:        Library for building simulation services in Python

License:        MIT
URL:            https://github.com/tjsego/simservice
Source0:        %{pypi_source simservice}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
simservice is a small pure-Python framework for wrapping a simulation as a
service: it provides process/thread service containers, a function registry
and messaging so a simulation can be driven programmatically. CompuCell3D uses
it for service-mode simulations; it is otherwise engine-agnostic.}

%description %{_description}

%package -n python3-simservice
Summary:        %{summary}

%description -n python3-simservice %{_description}

%prep
%autosetup -n simservice-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
# Upstream's package_data ships ../LICENSE into site-packages root; drop the
# stray (we install it properly via %%license).
rm -f %{buildroot}%{python3_sitelib}/LICENSE
%pyproject_save_files simservice

%check
%pyproject_check_import

%files -n python3-simservice -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.1-1
- Initial package: simservice 0.1.1 (pure-Python simulation-service framework).
- Removes the "simservice could not be imported" warning from CompuCell3D's
  engine/Player; part of the CC3D SBML/service dependency chain.
