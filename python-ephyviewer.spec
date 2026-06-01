%bcond tests 0

%global pypi_name ephyviewer

Name:           python-%{pypi_name}
Version:        1.8.0
Release:        2%{?dist}
Summary:        Simple viewers for ephys signals, events, video and more

# SPDX
License:        MIT
URL:            https://ephyviewer.readthedocs.io/
Source0:        https://github.com/NeuralEnsemble/%{pypi_name}/archive/%{version}/%{pypi_name}-%{version}.tar.gz

# python-pyedflib does not support s390x
ExcludeArch:    s390x %{ix86}
BuildArch:      noarch

BuildRequires:  python3-devel
%if %{with tests}
BuildRequires:  %{py3_dist pytest-xvfb}
%endif

%global _description %{expand:
ephyviewer is a Python library based on pyqtgraph for building custom viewers
for electrophysiological signals, video, events, epochs, spike trains, data
tables, and time-frequency representations of signals. It also provides an
epoch encoder for creating annotations.

Documentation is available at https://ephyviewer.readthedocs.io/.}

%description %{_description}


%package -n python3-%{pypi_name}
Summary:        %{summary}

%description -n python3-%{pypi_name} %{_description}


%prep
%autosetup -n %{pypi_name}-%{version} -p1

# spikeinterface and av optional and not yet packaged
# remove pytest-cov and coveralls
sed -i \
  -e '/spikeinterface/ d' \
  -e '/av/ d' \
  -e '/pytest-cov/ d' \
  -e '/coveralls/ d' \
  requirements-tests.txt


%generate_buildrequires
%pyproject_buildrequires -x tests


%build
%pyproject_wheel


%install
%pyproject_install
%pyproject_save_files -l %{pypi_name}


%check
%if %{with tests}
# These require network access
k="${k-}${k+ and }not test_neo_rawio_sources"
k="${k-}${k+ and }not test_neoviewer"
# These require python3dist(av), not packaged
k="${k-}${k+ and }not test_VideoMultiFileSource"
k="${k-}${k+ and }not test_mainviewer2"
k="${k-}${k+ and }not test_videoviewer"
# These require python3dist(spikeinterface), not packaged
k="${k-}${k+ and }not test_spikeinterface_sources"
k="${k-}${k+ and }not test_spikeinterface_viewer"
%pytest -r fEs ${k+-k "${k-}"}
%else
# Skip modules that require optional deps (PySide2/PySide6 icon bindings,
# CLI entry-point scripts, standalone runner, tests). The core ephyviewer
# library imports cleanly; the rest gate on optional GUI bindings or test
# fixtures.
%pyproject_check_import -e 'ephyviewer.icons.icons_PySide2' \
                        -e 'ephyviewer.icons.icons_PySide6' \
                        -e 'ephyviewer.scripts' \
                        -e 'ephyviewer.standalone' \
                        -e 'ephyviewer.tests*'
%endif


%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.rst
%{_bindir}/ephyviewer


%changelog
* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.8.0-2
- Exclude ephyviewer.icons.icons_PySide{2,6}, .scripts, .standalone, .tests*
  from %%pyproject_check_import — they gate on optional GUI bindings or
  test fixtures not present at build time. Build 10529354 failed at
  %%check importing those modules.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.8.0-1
- Update to 1.8.0 (adopted from Fedora dist-git python-ephyviewer 1.7.0; PR-185 + PR-188 patches now upstream)
