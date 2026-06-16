%global pypi_name line_profiler

Name:           python-line-profiler
Version:        5.0.2
Release:        1%{?dist}
Summary:        Line-by-line profiler for Python

License:        BSD-3-Clause
URL:            https://github.com/pyutils/line_profiler
Source0:        %{pypi_source %{pypi_name}}

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  python3-Cython

%description
line_profiler is a module for doing line-by-line profiling of functions,
measuring the time spent on each individual line of code.

%package -n python3-line-profiler
Summary:        %{summary}

%description -n python3-line-profiler
line_profiler is a module for doing line-by-line profiling of functions.

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name} kernprof

%check
%pyproject_check_import -e '*ipython*'

%files -n python3-line-profiler -f %{pyproject_files}
%doc README.rst
%{_bindir}/kernprof

%changelog
* Mon Jun 15 2026 Morgan Hough <morgan.hough@gmail.com> - 5.0.2-1
- Initial package (pyfix dependency chain).
