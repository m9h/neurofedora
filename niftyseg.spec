%global commit      16cf56313e3e28a8e47acfd02fff456784d99161
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate    20220308

%global debug_package %{nil}

Name:           niftyseg
Version:        0.9.5
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        EM-based segmentation, label fusion and image maths for medical images

License:        BSD-3-Clause
URL:            https://github.com/KCL-BMEIS/NiftySeg
Source0:        %{url}/archive/%{commit}/NiftySeg-%{commit}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  zlib-devel
BuildRequires:  eigen3-devel

%description
NiftySeg is a set of command-line tools for segmentation and related image
processing of medical (NIfTI) images: expectation-maximisation tissue
segmentation (seg_EM), multi-atlas label fusion (seg_LabFusion), the LoAd
brain segmentation pipeline (seg_LoAd), lesion filling, PatchMatch, and the
seg_maths / seg_stats image-maths and statistics utilities. A companion to
NiftyReg from the same group.

%prep
%autosetup -n NiftySeg-%{commit}

%build
# Old CMake project (min 2.8) — allow it under modern CMake. Use the system
# Eigen (avoid the offline ExternalProject download) and do NOT pull NiftyReg.
# Relocate the prior images out of the non-FHS /usr/priors.
%cmake -GNinja \
    -DCMAKE_POLICY_VERSION_MINIMUM=3.5 \
    -DCMAKE_BUILD_TYPE=Release \
    -DINSTALL_NIFTYREG:BOOL=OFF \
    -DUSE_SYSTEM_EIGEN:BOOL=ON \
    -DEIGEN_INCLUDE_DIR:PATH=%{_includedir}/eigen3 \
    -DINSTALL_PRIORS:BOOL=ON \
    -DINSTALL_PRIORS_DIRECTORY:PATH=%{_datadir}/niftyseg/priors \
    -DBUILD_SHARED_LIBS:BOOL=OFF
%cmake_build

%install
%cmake_install
# CLI-tools package: drop all the dev headers the build installs (including the
# bundled nifti/Eigen ones) and any static libs.
rm -rf %{buildroot}%{_includedir}
find %{buildroot} -name '*.a' -delete 2>/dev/null || :
# The CMake hardcodes priors to ${prefix}/priors (a plain SET, so -D can't
# override). Relocate them to a proper datadir.
if [ -d %{buildroot}%{_prefix}/priors ]; then
    mkdir -p %{buildroot}%{_datadir}/niftyseg
    mv %{buildroot}%{_prefix}/priors %{buildroot}%{_datadir}/niftyseg/priors
fi

%files
%license LICENSE.txt
%{_bindir}/seg_CalcTopNCC
%{_bindir}/seg_EM
%{_bindir}/seg_FillLesions
%{_bindir}/seg_LabFusion
%{_bindir}/seg_LoAd
%{_bindir}/seg_maths
%{_bindir}/seg_PatchMatch
%{_bindir}/seg_stats
%{_bindir}/LoAd_brainonly.sh
%dir %{_datadir}/niftyseg
%{_datadir}/niftyseg/priors

%changelog
* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 0.9.5-0.1.20220308git16cf563
- Initial package: NiftySeg segmentation/label-fusion/image-maths tools (master
  snapshot 16cf563). System Eigen, no NiftyReg download, priors relocated to
  %{_datadir}/niftyseg. NITRC gap; companion to niftyreg.
