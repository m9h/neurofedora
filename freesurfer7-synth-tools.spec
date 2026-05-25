# Consolidated spec for FreeSurfer 7.4.1 "synth" deep-learning tools.
# FS 7.4.1 ships fewer synth tools than 8.2.0 — synthstrip, synthsr, synthseg
# only. (synthmorph, super_synth, WMHsynthseg, tumorsynth are 8.x additions.)

%global fs_ver       7.4.1
%global fs_install   %{_prefix}/lib/freesurfer-%{fs_ver}
%global fs_synthdata %{_datadir}/freesurfer-%{fs_ver}

Name:           freesurfer7-synth-tools
Version:        %{fs_ver}
Release:        1%{?dist}
Summary:        Deep-learning tools meta-package for FreeSurfer 7.4.1

License:        FreeSurfer
URL:            https://surfer.nmr.mgh.harvard.edu/
Source0:        https://github.com/freesurfer/freesurfer/archive/refs/tags/v%{fs_ver}.tar.gz#/freesurfer-%{fs_ver}.tar.gz

BuildArch:      noarch
BuildRequires:  /bin/sh

Requires:       freesurfer7-synthstrip = %{version}-%{release}
Requires:       freesurfer7-synthsr    = %{version}-%{release}
Requires:       freesurfer7-synthseg   = %{version}-%{release}

%description
Meta-package pulling in all FreeSurfer 7.4.1 deep-learning "synth" tools:
synthstrip (PyTorch), synthsr (TensorFlow), synthseg (TensorFlow).

Python runtime is provided by freesurfer-fspython.

# ---------------------------------------------------------------------------
%package -n freesurfer7-synthstrip
Summary:        SynthStrip skull-stripping (PyTorch) for FreeSurfer 7.4.1
Requires:       freesurfer-fspython
Requires:       freesurfer7 = %{fs_ver}

%description -n freesurfer7-synthstrip
SynthStrip removes non-brain voxels from MRI across contrasts using a
PyTorch model. Model weights are not in the upstream tarball; the tool
downloads them to ~/.cache/freesurfer on first run.

# ---------------------------------------------------------------------------
%package -n freesurfer7-synthsr
Summary:        SynthSR MRI super-resolution (TensorFlow) for FreeSurfer 7.4.1
Requires:       freesurfer-fspython
Requires:       freesurfer7 = %{fs_ver}

%description -n freesurfer7-synthsr
SynthSR (FreeSurfer 7.4.1) turns low-resolution clinical MRI into
1 mm isotropic T1w-like volumes via TensorFlow + Keras.

# ---------------------------------------------------------------------------
%package -n freesurfer7-synthseg
Summary:        SynthSeg brain segmentation (TensorFlow) for FreeSurfer 7.4.1
Requires:       freesurfer-fspython
Requires:       freesurfer7 = %{fs_ver}

%description -n freesurfer7-synthseg
SynthSeg (FreeSurfer 7.4.1) segments brain MRI into anatomical regions
across contrasts and resolutions via TensorFlow + Keras.

# ===========================================================================
%prep
%setup -q -n freesurfer-%{fs_ver}

%build

%install
install -d %{buildroot}%{fs_install}/bin
install -d %{buildroot}%{fs_synthdata}

# ---- SynthStrip ----
if [ -f mri_synthstrip/mri_synthstrip ]; then
    install -m 0755 mri_synthstrip/mri_synthstrip %{buildroot}%{fs_install}/bin/
    sed -i '1s|^#!.*$|#!/usr/bin/fspython|' %{buildroot}%{fs_install}/bin/mri_synthstrip
fi

# ---- SynthSR ----
if [ -f mri_synthsr/mri_synthsr ]; then
    install -d %{buildroot}%{fs_synthdata}/synthsr
    install -m 0755 mri_synthsr/mri_synthsr %{buildroot}%{fs_install}/bin/
    sed -i '1s|^#!.*$|#!/usr/bin/fspython|' %{buildroot}%{fs_install}/bin/mri_synthsr
    for f in mri_synthsr/*.h5; do
        [ -e "$f" ] && [ ! -L "$f" ] && install -m 0644 -p "$f" \
            %{buildroot}%{fs_synthdata}/synthsr/
    done
fi

# ---- SynthSeg ----
if [ -f mri_synthseg/mri_synthseg ]; then
    install -d %{buildroot}%{fs_synthdata}/synthseg
    install -m 0755 mri_synthseg/mri_synthseg %{buildroot}%{fs_install}/bin/
    sed -i '1s|^#!.*$|#!/usr/bin/fspython|' %{buildroot}%{fs_install}/bin/mri_synthseg
    for f in mri_synthseg/*.h5 mri_synthseg/*.npy; do
        [ -e "$f" ] && [ ! -L "$f" ] && install -m 0644 -p "$f" \
            %{buildroot}%{fs_synthdata}/synthseg/
    done
fi

# ===========================================================================
%files
# Meta — owns no files

%files -n freesurfer7-synthstrip
%{fs_install}/bin/mri_synthstrip

%files -n freesurfer7-synthsr
%{fs_install}/bin/mri_synthsr
%dir %{fs_synthdata}
%{fs_synthdata}/synthsr/

%files -n freesurfer7-synthseg
%{fs_install}/bin/mri_synthseg
%{fs_synthdata}/synthseg/

%changelog
* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 7.4.1-1
- Initial consolidated synth-tools spec for FreeSurfer 7.4.1.
- Three subpackages: synthstrip (PyTorch), synthsr (TF), synthseg (TF).
- Model weights: where present in the tarball, bundled. Synthstrip model
  is git-annex'd upstream so its subpackage ships only the wrapper.
