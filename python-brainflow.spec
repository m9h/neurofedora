%global pypi_name brainflow

Name:           python-%{pypi_name}
Version:        5.22.2
Release:        1%{?dist}
Summary:        Python bindings for BrainFlow

License:        MIT
URL:            https://brainflow.org/
# PyPI ships ONLY a binary wheel for brainflow (no sdist), and that wheel
# bundles prebuilt native libs we must not ship. Build the pure-Python
# bindings from the GitHub source archive (python_package/) instead and
# link them to the system libs from our brainflow C++ package.
Source0:        https://github.com/brainflow-dev/brainflow/archive/refs/tags/%{version}.tar.gz#/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# Provides /usr/lib64/lib{BoardController,DataHandler,MLModule}.so so we can
# resolve the real versioned soname to symlink into the python package.
BuildRequires:  brainflow-devel = %{version}

%description
Python bindings for BrainFlow, intended to obtain, parse and analyze
EEG, EMG, ECG and other kinds of data from biosensors.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
# The python modules dlopen the native libs at runtime (BoardController,
# DataHandler, MLModule), which the runtime brainflow package ships.
Requires:       brainflow%{?_isa} = %{version}
Requires:       python3-numpy
%{?python_provide:%python_provide python3-%{pypi_name}}

%description -n python3-%{pypi_name}
Python bindings for BrainFlow.

%prep
%autosetup -n %{pypi_name}-%{version}

# The python bindings live in python_package/. Its setup.py carries a
# placeholder version that BrainFlow's CI rewrites at release time; pin it
# to the real version so the wheel/dist metadata is correct.
sed -i "s/version='0.0.1'.*/version='%{version}',/" python_package/setup.py

%generate_buildrequires
cd python_package
%pyproject_buildrequires

%build
cd python_package
%pyproject_wheel

%install
cd python_package
%pyproject_install
%pyproject_save_files %{pypi_name}

# The bindings load lib/libBoardController.so, lib/libDataHandler.so and
# lib/libMLModule.so *relative to the installed package* (board_shim.py,
# data_filter.py, ml_model.py hardcode these paths and raise if missing).
# We do not bundle the native libs (Fedora policy) — instead symlink the
# package's lib/ entries to the system libraries from the brainflow C++
# package. Resolve to the real versioned file so the runtime dependency is
# the (versioned) brainflow package, not brainflow-devel.
mkdir -p %{buildroot}%{python3_sitearch}/%{pypi_name}/lib
for l in libBoardController libDataHandler libMLModule; do
    target=$(readlink -f %{_libdir}/$l.so)
    ln -s "$target" %{buildroot}%{python3_sitearch}/%{pypi_name}/lib/$l.so
done

%check
# Confirm the bindings import and resolve the system native libs (the
# symlinks above + ldconfig). board_shim's loader raises FileNotFoundError
# if the lib path can't be resolved, so a clean import proves the wiring.
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license python_package/LICENSE.txt
%doc python_package/README.md
%dir %{python3_sitearch}/%{pypi_name}/lib
%{python3_sitearch}/%{pypi_name}/lib/lib*.so

%changelog
* Sun Jun 14 2026 Morgan Hough <morgan.hough@gmail.com> - 5.22.2-1
- Update to 5.22.2 (current upstream; freshness sweep 2026-06-14).
- PyPI dropped the sdist (wheel-only, with bundled native libs). Switch
  Source0 to the GitHub release archive and build the pure-Python bindings
  from python_package/. Pin the CI-placeholder setup.py version.
- Symlink the package's lib/{libBoardController,libDataHandler,libMLModule}.so
  to the system libraries (resolved to their real versioned soname) instead
  of bundling: the modules dlopen these paths relative to the package.

* Wed Jan 07 2026 Morgan Hough <morgan.hough@gmail.com> - 5.19.0-1
- Initial Python bindings for BrainFlow linked against system libs
