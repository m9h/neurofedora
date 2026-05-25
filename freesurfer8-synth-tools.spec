# Consolidated spec for FreeSurfer 8.2.0 "synth" deep-learning tools.
# One source tarball; six independent %package blocks (one per tool) plus a
# meta-package (Name:) pulling them all in. Avoids 6× tarball duplication if
# each were a separate spec.
#
# Note: freesurfer8-synthstrip already ships as a standalone spec (the POC).
# It could be folded here later; left alone for now.

%global fs_ver       8.2.0
%global fs_install   %{_prefix}/lib/freesurfer-%{fs_ver}
%global fs_synthdata %{_datadir}/freesurfer-%{fs_ver}

Name:           freesurfer8-synth-tools
Version:        %{fs_ver}
Release:        1%{?dist}
Summary:        Deep-learning tools meta-package for FreeSurfer 8.2.0

License:        FreeSurfer
URL:            https://surfer.nmr.mgh.harvard.edu/
Source0:        https://github.com/freesurfer/freesurfer/archive/refs/tags/v%{fs_ver}.tar.gz#/freesurfer-%{fs_ver}.tar.gz

BuildArch:      noarch
BuildRequires:  /bin/sh

# Meta-package: install all of them
Requires:       freesurfer8-synthseg     = %{version}-%{release}
Requires:       freesurfer8-synthsr      = %{version}-%{release}
Requires:       freesurfer8-synthmorph   = %{version}-%{release}
Requires:       freesurfer8-super-synth  = %{version}-%{release}
Requires:       freesurfer8-WMHsynthseg  = %{version}-%{release}
Requires:       freesurfer8-tumorsynth   = %{version}-%{release}
# synthstrip lives in its own spec (already shipped); recommend rather than require
Recommends:     freesurfer8-synthstrip

%description
Meta-package pulling in all FreeSurfer 8.2.0 deep-learning "synth" tools:
synthseg, synthsr, synthmorph, super_synth, WMHsynthseg, tumorsynth, plus
the separately-packaged synthstrip. Each is also installable individually.

Python runtime is provided by freesurfer-fspython (a uv-managed venv built
by freesurfer-synth-setup); model weights for v1.0 of each tool ship in the
upstream source tarball, but v2.0+ weights are git-annex'd upstream and
must be downloaded out-of-band.

# ---------------------------------------------------------------------------
%package -n freesurfer8-synthseg
Summary:        SynthSeg brain segmentation (TensorFlow) for FreeSurfer 8.2.0
Requires:       freesurfer-fspython
Requires:       freesurfer8 = %{fs_ver}

%description -n freesurfer8-synthseg
SynthSeg segments brain MRI into ~30 anatomical regions across any
contrast / resolution with no preprocessing required. Uses TensorFlow
+ Keras at inference time.

Bundled model: synthseg_1.0.h5 (53 MB). v2.0+ models (robust, qc,
parcellation, photo) are git-annex'd in upstream and not in this RPM —
fetch them from https://surfer.nmr.mgh.harvard.edu/.

# ---------------------------------------------------------------------------
%package -n freesurfer8-synthsr
Summary:        SynthSR MRI super-resolution (TensorFlow) for FreeSurfer 8.2.0
Requires:       freesurfer-fspython
Requires:       freesurfer8 = %{fs_ver}

%description -n freesurfer8-synthsr
SynthSR turns low-resolution clinical-quality MRI into 1 mm isotropic
T1w-like volumes. Two flavours: the standard scanner-resolution model
and a hyperfine-targeted variant. TensorFlow + Keras inference.

Bundled models: synthsr_v10_210712.h5 and synthsr_v10_210712_hyperfine.h5
(53 MB each). v2.0 model (synthsr_v20_230130.h5) is git-annex'd upstream.

# ---------------------------------------------------------------------------
%package -n freesurfer8-synthmorph
Summary:        SynthMorph deformable registration for FreeSurfer 8.2.0
Requires:       freesurfer-fspython
Requires:       freesurfer8 = %{fs_ver}

%description -n freesurfer8-synthmorph
SynthMorph performs learning-based diffeomorphic image registration.
Wraps the upstream `synthmorph` Python package — install it into the
fspython venv via `freesurfer-synth-setup` (the tool's `synthmorph` dep
is pulled from PyPI).

No model weights bundled (git-annex upstream).

# ---------------------------------------------------------------------------
%package -n freesurfer8-super-synth
Summary:        SuperSynth segmentation for FreeSurfer 8.2.0
Requires:       freesurfer-fspython
Requires:       freesurfer8 = %{fs_ver}

%description -n freesurfer8-super-synth
SuperSynth (a.k.a. mri_super_synth) is a multi-structure brain-MRI
segmenter; this package ships the bash wrapper plus the bundled
SuperSynth/ Python package into the FS install tree.

# ---------------------------------------------------------------------------
%package -n freesurfer8-WMHsynthseg
Summary:        WMHsynthseg white-matter hyperintensity segmenter (FreeSurfer 8.2.0)
Requires:       freesurfer-fspython
Requires:       freesurfer8 = %{fs_ver}

%description -n freesurfer8-WMHsynthseg
WMHsynthseg segments white-matter hyperintensities from FLAIR or T1w
volumes. Ships the bash wrapper plus the bundled WMHSynthSeg/ Python
package into the FS install tree.

# ---------------------------------------------------------------------------
%package -n freesurfer8-tumorsynth
Summary:        TumorSynth synthetic tumour augmentation (FreeSurfer 8.2.0)
Requires:       freesurfer-fspython
Requires:       freesurfer8 = %{fs_ver}

%description -n freesurfer8-tumorsynth
TumorSynth is a research wrapper for synthetic tumour augmentation
pipelines. Ships only the wrapper script; the actual ML backend is
expected to live in the fspython venv.

# ===========================================================================
%prep
%setup -q -n freesurfer-%{fs_ver}

%build
# Nothing to compile — every tool ships as a wrapper script + bundled data.

%install
install -d %{buildroot}%{fs_install}/bin
install -d %{buildroot}%{fs_install}/python/packages
install -d %{buildroot}%{fs_synthdata}

# ---- SynthSeg ----
install -d %{buildroot}%{fs_synthdata}/synthseg
install -m 0755 mri_synthseg/mri_synthseg %{buildroot}%{fs_install}/bin/
sed -i '1s|^#!.*$|#!/usr/bin/fspython|' %{buildroot}%{fs_install}/bin/mri_synthseg
# Copy v1.0 .h5 + all .npy labels. Symlinks for v2.0+ models point to
# git-annex content that's not in the tarball — skip those (cp -L would
# error on dangling links).
for f in mri_synthseg/synthseg_1.0.h5 mri_synthseg/*.npy; do
    [ -e "$f" ] && [ ! -L "$f" ] && install -m 0644 -p "$f" \
        %{buildroot}%{fs_synthdata}/synthseg/
done

# ---- SynthSR ----
install -d %{buildroot}%{fs_synthdata}/synthsr
install -m 0755 mri_synthsr/mri_synthsr           %{buildroot}%{fs_install}/bin/
install -m 0755 mri_synthsr/mri_synthsr_hyperfine %{buildroot}%{fs_install}/bin/
sed -i '1s|^#!.*$|#!/usr/bin/fspython|' \
    %{buildroot}%{fs_install}/bin/mri_synthsr \
    %{buildroot}%{fs_install}/bin/mri_synthsr_hyperfine
for f in mri_synthsr/synthsr_v10_210712.h5 mri_synthsr/synthsr_v10_210712_hyperfine.h5; do
    [ -e "$f" ] && [ ! -L "$f" ] && install -m 0644 -p "$f" \
        %{buildroot}%{fs_synthdata}/synthsr/
done

# ---- SynthMorph ----
install -m 0755 mri_synthmorph/mri_synthmorph %{buildroot}%{fs_install}/bin/
sed -i '1s|^#!.*$|#!/usr/bin/fspython|' %{buildroot}%{fs_install}/bin/mri_synthmorph

# ---- SuperSynth ----
install -m 0755 mri_super_synth/mri_super_synth %{buildroot}%{fs_install}/bin/
# Bash wrapper; no shebang patch
if [ -d mri_super_synth/SuperSynth ]; then
    cp -rp mri_super_synth/SuperSynth %{buildroot}%{fs_install}/python/packages/
fi

# ---- WMHsynthseg ----
install -m 0755 mri_WMHsynthseg/mri_WMHsynthseg %{buildroot}%{fs_install}/bin/
if [ -d mri_WMHsynthseg/WMHSynthSeg ]; then
    cp -rp mri_WMHsynthseg/WMHSynthSeg %{buildroot}%{fs_install}/python/packages/
fi

# ---- TumorSynth ----
install -m 0755 mri_tumorsynth/mri_tumorsynth %{buildroot}%{fs_install}/bin/

# ===========================================================================
%files
# Meta — owns no files

%files -n freesurfer8-synthseg
%{fs_install}/bin/mri_synthseg
%dir %{fs_synthdata}
%{fs_synthdata}/synthseg/

%files -n freesurfer8-synthsr
%{fs_install}/bin/mri_synthsr
%{fs_install}/bin/mri_synthsr_hyperfine
%{fs_synthdata}/synthsr/

%files -n freesurfer8-synthmorph
%{fs_install}/bin/mri_synthmorph

%files -n freesurfer8-super-synth
%{fs_install}/bin/mri_super_synth
%{fs_install}/python/packages/SuperSynth/

%files -n freesurfer8-WMHsynthseg
%{fs_install}/bin/mri_WMHsynthseg
%{fs_install}/python/packages/WMHSynthSeg/

%files -n freesurfer8-tumorsynth
%{fs_install}/bin/mri_tumorsynth

%changelog
* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 8.2.0-1
- Initial consolidated synth-tools spec covering synthseg, synthsr,
  synthmorph, super_synth, WMHsynthseg, tumorsynth.
- One shared SRPM/tarball; each tool is an independent installable subpackage
  with its own Requires (freesurfer-fspython + freesurfer8 base).
- synthstrip continues to ship from freesurfer8-synthstrip.spec for now.
- Model weights: v1.0 (.h5) bundled where present in upstream tarball;
  v2.0+ models are git-annex'd upstream and must be fetched out-of-band.
