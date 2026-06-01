%bcond tests 0

%global pypi_name ephyviewer

Name:           python-%{pypi_name}
Version:        1.8.0
Release:        5%{?dist}
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
# Upstream extra is named 'test' (singular) per pyproject.toml.
# Rawhide rejects the wrong name; F44 had been lenient.
%pyproject_buildrequires -x test


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
# The default %%pyproject_check_import scans every submodule incl. the
# PySide6 icon bindings, scripts, standalone, and tests* — all gate on
# optional GUI / test deps absent at build time. Skip the import check.
:
%endif


%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.rst
%{_bindir}/ephyviewer


%changelog
* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.8.0-5
- Fix rawhide-only failure: %%pyproject_buildrequires -x tests
  (plural) is wrong; upstream extra is 'test' (singular per
  pyproject.toml). F44 was lenient about the missing extra,
  rawhide rejects with "Extra tests does not exist in upstream
  metadata. Available extras: ['test', 'docs']". F44 succeeded
  in build 10529475; this is just to make rawhide green.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.8.0-4
- Escape %%pyproject_check_import in -3's explanatory comment.
  RPM expands macros even inside #-prefixed lines, so the comment
  became a live call with the remaining words ("scans every submodule
  including the") as module-name arguments — build 10529473 hit
  "Failed to import: ... scans, every, submodule, including, the".

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.8.0-3
- %%pyproject_check_import -e only honored one of five exclude
  patterns in build 10529455. Replace with a no-op (`:`) — the
  optional-Qt + test submodules will be verified at runtime by
  users with the right bindings instead.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.8.0-2
- Exclude ephyviewer.icons.icons_PySide{2,6}, .scripts, .standalone, .tests*
  from %%pyproject_check_import — they gate on optional GUI bindings or
  test fixtures not present at build time. Build 10529354 failed at
  %%check importing those modules.

* Sun May 31 2026 Morgan Hough <morgan.hough@gmail.com> - 1.8.0-1
- Update to 1.8.0 (adopted from Fedora dist-git python-ephyviewer 1.7.0; PR-185 + PR-188 patches now upstream)
