Name:           python-rmsd
Version:        1.6.5
Release:        %autorelease
# Fill in the actual package summary to submit package to Fedora
Summary:        Calculate Root-mean-square deviation _RMSD_ of two molecules, using rotation, in xyz or pdb format

# No license information obtained, it's up to the packager to fill it in
License:        ...
URL:            https://github.com/charnley/rmsd
Source:         %{pypi_source rmsd}

BuildArch:      noarch
BuildRequires:  python3-devel


# Fill in the actual package description to submit package to Fedora
%global _description %{expand:
This is package 'rmsd' generated automatically by pyp2spec.}

%description %_description

%package -n     python3-rmsd
Summary:        %{summary}

%description -n python3-rmsd %_description

# For official Fedora packages, review which extras should be actually packaged
# See: https://docs.fedoraproject.org/en-US/packaging-guidelines/Python/#Extras


%prep
%autosetup -p1 -n rmsd-%{version}


%generate_buildrequires
# Keep only those extras which you actually want to package or use during tests
%pyproject_buildrequires


%build
%pyproject_wheel


%install
%pyproject_install
# Automatically extracted from wheel
%pyproject_save_files -l rmsd


%check
%pyproject_check_import


%files -n python3-rmsd -f %{pyproject_files}
%{_bindir}/calculate_rmsd


%changelog
%autochangelog
