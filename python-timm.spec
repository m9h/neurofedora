%global pypi_name timm
%global import_name timm

Name:           python-%{pypi_name}
Version:        1.0.22
Release:        1%{?dist}
Summary:        PyTorch image models, layers, and utilities

License:        Apache-2.0
URL:            https://github.com/huggingface/pytorch-image-models
Source0:        %{pypi_source %{pypi_name}}

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros

%global _description %{expand:
timm (PyTorch Image Models) is a large collection of image models, layers,
optimizers, schedulers and data-loading utilities, with pretrained weights
distributed through the Hugging Face Hub.

In this repository it is present as a dependency of
dynamic-network-architectures, which uses timm layers to build the transformer
based (EVA / Primus / DINOv2) segmentation architectures of the nnU-Net stack.}

%description %_description

%package -n python3-%{pypi_name}
Summary:        %{summary}
%description -n python3-%{pypi_name} %_description

%prep
%autosetup -n %{pypi_name}-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files %{import_name}

%check
# The Hugging Face `datasets` and TensorFlow dataset readers are optional
# integrations; neither backing library is a dependency of this package (and
# tensorflow is not packaged for Fedora), so their reader modules cannot import
# in the buildroot. Exclude them from the import check.
%pyproject_check_import -e '*.readers.reader_hfds' -e '*.readers.reader_hfids' -e '*.readers.reader_tfds' -e '*.data.tf_preprocessing'

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Sat Jul 18 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0.22-1
- Initial package. Held at 1.0.22 rather than the newer 1.0.28 because
  dynamic-network-architectures declares timm < 1.0.23; packaging the capped
  version keeps that dependency satisfiable without patching upstream metadata.
