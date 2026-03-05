%global pypi_name samseg
%global commit ccb17cbcdad707fbbf65e5e934fc89b95cc8529a
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           python-%{pypi_name}
Version:        0.4a0
Release:        1%{?dist}
Summary:        Sequence Adaptive Multimodal SEGmentation

License:        GPL-3.0-only
URL:            https://github.com/freesurfer/samseg
Source0:        %{url}/archive/%{commit}/%{pypi_name}-%{shortcommit}.tar.gz
Patch0:         samseg-system-deps.patch

BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
BuildRequires:  python3-pip
BuildRequires:  python3-versioneer
BuildRequires:  python3-nibabel
BuildRequires:  python3-scipy
BuildRequires:  python3-pybind11
BuildRequires:  pybind11-devel
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  InsightToolkit6-devel
BuildRequires:  gtest-devel

%description
SAMSEG (Sequence Adaptive Multimodal SEGmentation) is a tool for robustly
segmenting various brain structures from head MRI scans without requiring
extensive preprocessing.

%package -n     python3-%{pypi_name}
Summary:        %{summary}
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-nibabel

%description -n python3-%{pypi_name}
SAMSEG (Sequence Adaptive Multimodal SEGmentation) is a tool for robustly
segmenting various brain structures from head MRI scans without requiring
extensive preprocessing.

%prep
%setup -q -n %{pypi_name}-%{commit}
%patch -P 0 -p1

# Remove bundled dirs to ensure we use system libraries
rm -rf pybind11 ITK

%build
# Set CONDA_PREFIX to /usr to bypass the check in some build scripts
# although samseg's CMakeLists.txt doesn't seem to use it, it's a good practice here.
export CXXFLAGS="%{optflags}"
%pyproject_wheel \
    -Ccmake.define.pybind11_DIR=%{_datadir}/cmake/pybind11 \
    -Ccmake.define.ITK_DIR=%{_libdir}/cmake/ITK-6.0

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}

%changelog
* Wed Feb 25 2026 Morgan Hough <morgan.hough@gmail.com> - 0.4a0-1
- Initial package for SimNIBS dependency
