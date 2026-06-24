Name:           python-openflexure-microscope-client
Version:        0.1.8
Release:        1%{?dist}
Summary:        Python client for the OpenFlexure Microscope

# Upstream 0.1.8 pyproject metadata declares LGPL-3.0-or-later (the release
# ships no license file; upstream master has since relicensed to MIT, but that
# applies to future releases). Canonical LGPLv3 text shipped as Source1.
License:        LGPL-3.0-or-later
URL:            https://gitlab.com/openflexure/openflexure-microscope-pyclient
Source0:        %{pypi_source openflexure_microscope_client}
Source1:        lgpl-3.0.txt

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-poetry-core

%global _description %{expand:
openflexure-microscope-client is the Python client for the OpenFlexure
Microscope: it discovers a microscope on the network over zeroconf/mDNS and
drives it through the LabThings / Web-of-Things HTTP API — moving the stage,
capturing images (returned as PIL images / NumPy arrays), and reading and
setting properties. It is the connector used to bring OpenFlexure acquisitions
into Python tools such as napari.}

%description %{_description}

%package -n python3-openflexure-microscope-client
Summary:        %{summary}
%description -n python3-openflexure-microscope-client %{_description}

%prep
%autosetup -n openflexure_microscope_client-%{version}

# The release ships no license file; provide the LGPLv3 text it declares.
cp -p %{SOURCE1} LICENSE

# Upstream pyproject.toml has [tool.poetry] but NO [build-system] table — add
# one so the PEP 517 build uses poetry-core.
cat >> pyproject.toml <<'EOF'

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
EOF

# Relax Poetry caret upper-bounds (^x = >=x,<next-major). Fedora ships newer
# numpy (2.x), Pillow (12.x) and zeroconf (0.118) than the <2.0/<10.0/<0.40
# caps allow; the client's usage (image arrays, PIL open, mDNS discovery) is
# unaffected by those majors. Convert every caret to a bare lower bound.
sed -i 's/"\^/">=/g' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files openflexure_microscope_client

%check
%pyproject_check_import

%files -n python3-openflexure-microscope-client -f %{pyproject_files}
%license LICENSE
%doc README.md

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.8-1
- Initial package: openflexure-microscope-client 0.1.8.
- Add a [build-system] table (upstream omits it) and relax the Poetry caret
  caps on numpy/Pillow/zeroconf/requests so it builds against current Fedora.
- License per the 0.1.8 release metadata (LGPL-3.0-or-later); LGPLv3 text
  shipped as a Source since the release omits a license file.
