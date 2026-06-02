Name:           python-trame-slicer
Version:        1.11.0
Release:        1%{?dist}
Summary:        3D Slicer-powered medical image viewer for trame web applications

License:        Apache-2.0
URL:            https://github.com/KitwareMedical/trame-slicer
Source:         %{pypi_source trame_slicer}

BuildArch:      noarch
BuildRequires:  python3-devel
# Runtime deps re-stated as BR so %%pyproject_buildrequires / import check resolve.
# NOTE: python3-itk (PyPI "itk", the ITK Python wrappings) is NOT yet packaged on
# Fedora or in this COPR. ITK_WRAP_PYTHON is disabled in our InsightToolkit5/6
# specs, so trame-slicer cannot build or install until python3-itk exists. This
# spec is staged ahead of that blocker; see the changelog.
BuildRequires:  python3-itk
BuildRequires:  python3-lxml
BuildRequires:  python3-pillow
BuildRequires:  python3-pillow-avif-plugin
BuildRequires:  python3-py-undo-stack
BuildRequires:  python3-pydicom
BuildRequires:  python3-trame
BuildRequires:  python3-trame-client
BuildRequires:  python3-trame-rca
BuildRequires:  python3-trame-server
BuildRequires:  python3-trame-vtk
BuildRequires:  python3-trame-vuetify
BuildRequires:  python3-webcolors

%global _description %{expand:
trame-slicer embeds 3D Slicer's MRML scene, display, and segmentation logic
inside a trame web application, streaming 2D/3D slice and volume-rendering
views to a browser via trame-rca. It lets Slicer-based medical imaging
workflows run as remote web services.}

%description %_description

%package -n     python3-trame-slicer
Summary:        %{summary}
Requires:       python3-itk
Requires:       python3-lxml
Requires:       python3-pillow
Requires:       python3-pillow-avif-plugin
Requires:       python3-py-undo-stack
Requires:       python3-pydicom
Requires:       python3-trame
Requires:       python3-trame-client
Requires:       python3-trame-rca
Requires:       python3-trame-server
Requires:       python3-trame-vtk
Requires:       python3-trame-vuetify
Requires:       python3-webcolors

%description -n python3-trame-slicer %_description

%prep
%autosetup -p1 -n trame_slicer-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files trame_slicer

%check
%_pyproject_check_import_allow_no_modules -t

%files -n python3-trame-slicer -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Mon Jun 01 2026 Morgan Hough <morgan.hough@gmail.com> - 1.11.0-1
- Initial package: top of the trame-slicer web-viewer dependency chain.
- BLOCKED on python3-itk (PyPI "itk" ITK Python wrappings), which is not yet
  packaged. InsightToolkit5/6 specs build with ITK_WRAP_PYTHON disabled; a
  python3-itk subpackage (or a separate ITKPythonPackage build) is required
  before this can build/install. Spec staged so the rest of the chain (trame*,
  py-undo-stack, pillow-avif-plugin, all already in COPR) is wired and ready.
