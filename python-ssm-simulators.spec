%global pypi_name ssm-simulators
%global dist_name ssm_simulators

Name:           python-%{pypi_name}
Version:        0.12.3
Release:        1%{?dist}
Summary:        Simulators and training-data generators for sequential sampling models

License:        MIT
URL:            https://github.com/lnccbrown/ssm-simulators
Source0:        %{pypi_source %{dist_name}}

# Cython extension modules (the "cssm" package), so this build is arch specific.
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# Optional but recommended: GSL provides the validated Ziggurat RNG used by the
# parallel simulators; OpenMP (libgomp, shipped with gcc) enables threading.
BuildRequires:  gsl-devel

%global _description %{expand:
SSM-Simulators (ssms) is a collection of fast simulators and training-data
generators for sequential sampling models (SSMs) used in cognitive science,
neuroscience, and simulation-based ("likelihood-free") Bayesian inference. It
provides Cython implementations of drift-diffusion, race, leaky competing
accumulator, Levy, Ornstein-Uhlenbeck and related models, plus utilities for
generating large parameter-sweep datasets to train likelihood-approximation
networks. It is the simulator backend used by the HSSM toolbox.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{dist_name}-%{version}
# Upstream conservatively caps requires-python at <3.14; the Cython sources
# build and import fine on newer Python, so relax the upper bound to cover
# current Fedora (3.14) and rawhide (3.15).
sed -i 's/,<3.14"/,<3.16"/' pyproject.toml
# LICENSE and README ship with spurious executable bits in the sdist.
chmod 0644 LICENSE README.md

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
# The CLI module carries a "#!/usr/bin/env -S uv run --script" shebang but is
# imported via its console entry point, not executed directly; strip it so it
# is not treated as a non-executable script.
sed -i '1{/^#!/d}' %{buildroot}%{python3_sitearch}/ssms/cli/generate.py
# Two importable top-level packages: the pure-Python "ssms" and the compiled
# "cssm" extension package.
%pyproject_save_files ssms cssm

%check
%pyproject_check_import -t

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/generate

%changelog
* Sat Jun 27 2026 Morgan Hough <morgan.hough@gmail.com> - 0.12.3-1
- Initial package (HSSM simulator backend; partial HSSM dependency stack)
