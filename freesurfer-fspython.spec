Name:           freesurfer-fspython
Version:        1.0.0
Release:        1%{?dist}
Summary:        FreeSurfer Python (fspython) launcher and uv-venv setup tool
License:        Apache-2.0
URL:            https://gitlab.com/morgan.hough/neurofedora

# Bash launcher placed at /usr/bin/fspython. Resolves to the venv created
# by freesurfer-synth-setup.
Source0:        fspython
# Setup tool: detects host accelerator, picks the right requirements file,
# builds a uv-managed venv at /var/lib/freesurfer/synth-venv (overridable).
Source1:        freesurfer-synth-setup
# Per-accelerator pin lists installed by uv into the venv.
Source2:        freesurfer-synth-requirements-cpu.txt
Source3:        freesurfer-synth-requirements-cpu-avx2.txt
Source4:        freesurfer-synth-requirements-cuda121.txt
Source5:        freesurfer-synth-requirements-cuda124.txt
Source6:        freesurfer-synth-requirements-rocm60.txt

BuildArch:      noarch

# Runtime: the only hard dep is uv, which orchestrates the venv. Everything
# else is fetched into the venv at first run by `freesurfer-synth-setup`.
Requires:       uv
Requires:       /bin/bash
Requires(post): /bin/bash

# Suggested: at least one of the FreeSurfer major versions
Suggests:       freesurfer8
Suggests:       freesurfer7

%description
FreeSurfer Python (fspython) launcher and setup tool.

This package ships /usr/bin/fspython — a Bash launcher that runs FreeSurfer's
Python helper scripts (such as those backing mri_synthseg, mri_synthsr,
mri_synthstrip, mri_synthmorph, and other "synth" tools) against a
uv-managed virtual environment containing TensorFlow, PyTorch, surfa,
nibabel, and the rest of the neuroimaging ML stack.

The venv is built once, post-install, by running:

    sudo freesurfer-synth-setup

The setup tool detects the host's accelerator (NVIDIA CUDA 12.1 / 12.4,
AMD ROCm 6.0, CPU with AVX2, or plain CPU) and installs the matching
pinned wheels from PyPI and the appropriate pytorch.org index. Override
detection with --accel, or install per-user by setting FREESURFER_SYNTH_VENV.

This decoupling sidesteps Fedora's lack of native TensorFlow packaging
without coupling the FreeSurfer RPM set to a third-party Python stack.

%prep
# Nothing to extract — Sources are individual files copied straight to
# %{buildroot} in %install.

%build
# Nothing to compile.

%install
mkdir -p %{buildroot}%{_bindir}
install -p -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/fspython
install -p -m 0755 %{SOURCE1} %{buildroot}%{_bindir}/freesurfer-synth-setup

mkdir -p %{buildroot}%{_datadir}/freesurfer/synth
install -p -m 0644 %{SOURCE2} %{buildroot}%{_datadir}/freesurfer/synth/requirements-cpu.txt
install -p -m 0644 %{SOURCE3} %{buildroot}%{_datadir}/freesurfer/synth/requirements-cpu-avx2.txt
install -p -m 0644 %{SOURCE4} %{buildroot}%{_datadir}/freesurfer/synth/requirements-cuda121.txt
install -p -m 0644 %{SOURCE5} %{buildroot}%{_datadir}/freesurfer/synth/requirements-cuda124.txt
install -p -m 0644 %{SOURCE6} %{buildroot}%{_datadir}/freesurfer/synth/requirements-rocm60.txt

# Pre-create the system-wide venv directory; setup tool will populate it
install -d -m 0755 %{buildroot}%{_sharedstatedir}/freesurfer

# freesurfer-synth-setup expects requirements at /usr/lib/freesurfer/synth;
# the install lays them in %{_datadir}/freesurfer/synth and we symlink so
# the same path resolves on multilib hosts (/usr/lib vs /usr/lib64).
mkdir -p %{buildroot}%{_prefix}/lib/freesurfer
ln -s ../../share/freesurfer/synth %{buildroot}%{_prefix}/lib/freesurfer/synth

%post
# Friendly nudge — do not actually run setup at RPM-install time. Network
# fetches at %post would be a guideline violation, and root-only Anaconda-
# style installs surprise users. They opt in by running the setup tool.
cat <<'EOF'

freesurfer-fspython installed.

Before any synth tool (mri_synthseg, mri_synthsr, mri_synthstrip,
mri_synthmorph, etc.) will work, initialise the Python environment:

    sudo freesurfer-synth-setup            # system-wide, auto-detect hw

Or for a per-user install:

    FREESURFER_SYNTH_VENV=$HOME/.local/share/freesurfer/synth-venv \
        freesurfer-synth-setup

Run `freesurfer-synth-setup --help` for accelerator and pin options.

EOF

%files
%{_bindir}/fspython
%{_bindir}/freesurfer-synth-setup
%dir %{_datadir}/freesurfer
%dir %{_datadir}/freesurfer/synth
%{_datadir}/freesurfer/synth/requirements-cpu.txt
%{_datadir}/freesurfer/synth/requirements-cpu-avx2.txt
%{_datadir}/freesurfer/synth/requirements-cuda121.txt
%{_datadir}/freesurfer/synth/requirements-cuda124.txt
%{_datadir}/freesurfer/synth/requirements-rocm60.txt
%dir %{_prefix}/lib/freesurfer
%{_prefix}/lib/freesurfer/synth
%dir %attr(0755, root, root) %{_sharedstatedir}/freesurfer

%changelog
* Sun May 24 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.0-1
- Initial package — uv-venv fspython framework for FreeSurfer synth-tools.
- Ships fspython launcher, freesurfer-synth-setup hardware-detecting
  bootstrap tool, and per-accelerator pin files (CPU / CPU+AVX2 /
  CUDA 12.1 / CUDA 12.4 / ROCm 6.0).
- Sidesteps Fedora's lack of native TensorFlow without bundling a heavy
  ML stack in the RPM; first-run setup downloads wheels.
