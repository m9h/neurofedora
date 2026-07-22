%global pypi_name hdf5plugin

Name:           python-hdf5plugin
Version:        7.0.0
Release:        1%{?dist}
Summary:        HDF5 compression filters (Blosc, LZ4, Zstd, BitShuffle, …) for h5py

# hdf5plugin itself is BSD/MIT; it bundles several filter libraries under their
# own licenses (Blosc/BSD, LZ4/BSD, Zstd/BSD, bzip2/BSD-like, zfp/BSD, SZ, …).
License:        MIT AND BSD-3-Clause AND BSD-2-Clause AND Zlib
URL:            https://github.com/silx-kit/hdf5plugin
Source0:        %{pypi_source %{pypi_name}}

BuildRequires:  python3-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  hdf5-devel

%global _description %{expand:
hdf5plugin provides a set of HDF5 compression filters (Blosc, Blosc2, BitShuffle,
LZ4, FciDecomp, SZ, SZ3, Zfp, Zstandard) and makes them usable from h5py. It
ships the compiled filter plugins so they can be registered with the HDF5 library
at runtime.}

%description %_description

%package -n python3-hdf5plugin
Summary:        %{summary}
%description -n python3-hdf5plugin %_description

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{pypi_name}

%files -n python3-hdf5plugin -f %{pyproject_files}
%doc README.rst
%license LICENSE

%changelog
* Mon Jul 20 2026 Morgan Hough <morgan.hough@gmail.com> - 7.0.0-1
- Reconstructed spec; update to 7.0.0
