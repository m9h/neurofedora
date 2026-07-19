%global pypi_name nnunetv2
%global import_name nnunetv2

Name:           python-%{pypi_name}
Version:        2.8.1
Release:        1%{?dist}
Summary:        Self-configuring framework for medical image segmentation

License:        Apache-2.0
URL:            https://github.com/MIC-DKFZ/nnUNet
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
nnU-Net is a self-configuring framework for biomedical image segmentation: from
a dataset fingerprint it derives the preprocessing, network topology, training
schedule and post-processing automatically, without manual architecture tuning.
It remains a standard baseline in medical segmentation and is the engine
underneath nnInteractive.

This package provides the library and the nnUNetv2_* command line tools.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}

# Fedora ships torch 2.9.1, which upstream excludes via `torch>=2.1.2,!=2.9.*`.
# That exclusion is a PERFORMANCE guard, not a correctness one: torch 2.9 shipped
# with a cuDNN bug that made the torch developers disable many fast convolution
# implementations, so 3D convolutions with AMP run several times slower
# (pytorch/pytorch#166122, now closed; MIC-DKFZ/nnUNet#3002, where upstream states
# "2.9 is just slow"). It is a CUDA/cuDNN code-path problem, and Fedora's torch is
# built without CUDA, so the regression does not apply to this package's users.
# Relax the exclusion so the dependency is satisfiable against Fedora's torch.
sed -i 's/"torch>=2\.1\.2,!=2\.9\.\*"/"torch>=2.1.2"/' pyproject.toml
grep -q '!=2.9' pyproject.toml && exit 1 || :

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{import_name}

%check
%pyproject_check_import

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc readme.md
%{_bindir}/nnUNetv2_*

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 2.8.1-1
- Initial package. Segmentation engine underneath nnInteractive. Relaxes the
  upstream torch != 2.9.* exclusion, which is a CUDA/cuDNN performance guard
  that does not apply to Fedora's CPU-only torch (see the comment in %%prep).
