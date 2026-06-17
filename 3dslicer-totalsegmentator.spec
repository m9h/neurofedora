# SlicerTotalSegmentator — fully automatic whole-body/organ CT (and more)
# segmentation in 3D Slicer using the TotalSegmentator nnU-Net AI models.
# PURE-SCRIPTED (Python) module: replicate slicerMacroBuildScriptedModule (drop
# the module + resources into qt-scripted-modules), no find_package(Slicer), no
# foundation -devel. The heavy runtime deps (torch, TotalSegmentator, nnunetv2)
# are pip-installed by the module on first use — not packaged here — so this is
# a small noarch package, independent of the C++ extension-build work.
#
# This is the agent-drivable AI segmentation: an LLM agent can invoke it through
# the Slicer Web Server (see python3-mcp-slicer).

%global commit      519af9cbd306a35c87b7d804350d3343b200cd2e
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260528

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.11
%global qtsm          %{slicer_inst}/lib/%{slicer_subdir}/qt-scripted-modules

Name:           3dslicer-totalsegmentator
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        TotalSegmentator automatic AI segmentation extension for 3D Slicer

License:        Apache-2.0
URL:            https://github.com/lassoan/SlicerTotalSegmentator
Source0:        %{url}/archive/%{commit}/SlicerTotalSegmentator-%{shortcommit}.tar.gz

BuildArch:      noarch

Requires:       3dslicer
# Scripted modules need the bug#9 scriptability layer to load.
Requires:       ctk-python
Requires:       python3-vtkAddon

%description
SlicerTotalSegmentator brings fully automatic AI segmentation to 3D Slicer using
the TotalSegmentator nnU-Net models (whole-body CT organs, vertebrae, ribs,
cardiac/muscle/vessel structures, and more). The module installs the AI runtime
(torch, TotalSegmentator, nnunetv2) on first use via pip from within Slicer, so
those large dependencies are not packaged here; only the Slicer-side module and
resources are shipped.

Because it runs in Slicer's Python, it can be driven by an LLM agent through the
Slicer Web Server interface (see python3-mcp-slicer).

%prep
%autosetup -n SlicerTotalSegmentator-%{commit}

%build
# Pure-scripted: nothing to compile.

%install
mkdir -p %{buildroot}%{qtsm}/Resources/Icons
mkdir -p %{buildroot}%{qtsm}/Resources/UI

install -m0644 TotalSegmentator/TotalSegmentator.py %{buildroot}%{qtsm}/
install -m0644 TotalSegmentator/Resources/*.csv TotalSegmentator/Resources/*.json \
        %{buildroot}%{qtsm}/Resources/
install -m0644 TotalSegmentator/Resources/UI/*.ui %{buildroot}%{qtsm}/Resources/UI/
install -m0644 TotalSegmentator/Resources/Icons/*.png %{buildroot}%{qtsm}/Resources/Icons/

%files
%license LICENSE
%doc README.md
# Individual files dropped into the shared qt-scripted-modules / Resources dirs
# (owned by the 3dslicer package); nothing TotalSegmentator-specific to %%dir-own.
%{qtsm}/TotalSegmentator.py
%{qtsm}/Resources/totalsegmentator_snomed_mapping.csv
%{qtsm}/Resources/SegmentationCategoryTypeModifier-TotalSegmentator.term.json
%{qtsm}/Resources/UI/TotalSegmentator.ui
%{qtsm}/Resources/Icons/TotalSegmentator.png

%changelog
* Tue Jun 16 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260528git519af9cb
- Initial package. SlicerTotalSegmentator as a pure-scripted 3D Slicer extension:
  install the TotalSegmentator module + resources into qt-scripted-modules, no
  compilation / no foundation -devel. The torch/TotalSegmentator AI runtime is
  pip-installed by the module on first use, not packaged.
