# SlicerMONAILabel — 3D Slicer client for MONAI Label, an intelligent
# open-source image-labeling/learning tool (interactive AI annotation with
# active learning). PURE-SCRIPTED (Python) plugin from the MONAILabel repo's
# plugins/slicer tree: two modules, MONAILabel and MONAILabelReviewer. Like the
# other scripted extensions we replicate slicerMacroBuildScriptedModule directly
# (no find_package(Slicer), no foundation -devel).
#
# The MONAI Label server + its heavy deps (monai, torch) are NOT packaged here:
# the Slicer module is a thin client that talks to a running MONAI Label server
# over HTTP (the user runs `monailabel start_server ...` separately).

%global commit      6ed8f8c6113db723cc79ad71ac51b952bb860fac
%global shortcommit %(c=%{commit}; echo ${c:0:8})
%global snapdate    20260204

%global slicer_inst   %{_prefix}/lib/slicer
%global slicer_subdir Slicer-5.11
%global qtsm          %{slicer_inst}/lib/%{slicer_subdir}/qt-scripted-modules

Name:           3dslicer-monailabel
Version:        1.0
Release:        0.1.%{snapdate}git%{shortcommit}%{?dist}
Summary:        MONAI Label interactive AI annotation client for 3D Slicer

License:        Apache-2.0
URL:            https://github.com/Project-MONAI/MONAILabel
Source0:        %{url}/archive/%{commit}/MONAILabel-%{shortcommit}.tar.gz

BuildArch:      noarch

Requires:       3dslicer
# Scripted modules need the bug#9 scriptability layer to load.
Requires:       ctk-python
Requires:       python3-vtkAddon

%description
SlicerMONAILabel is the 3D Slicer client for MONAI Label — an open-source tool
for AI-assisted, interactive image annotation with active learning. It provides
the MONAILabel module (segment/annotate against a MONAI Label server, submit
labels, trigger training) and the MONAILabelReviewer module (review and curate
the resulting label store).

This package ships only the Slicer-side client modules. The MONAI Label server
and its deep-learning dependencies (monailabel, monai, torch) are installed and
run separately (e.g. `pip install monailabel`); the modules talk to the server
over HTTP.

%prep
%autosetup -n MONAILabel-%{commit}

%build
# Pure-scripted: nothing to compile.

%install
mkdir -p %{buildroot}%{qtsm}/MONAILabelLib \
         %{buildroot}%{qtsm}/MONAILabelReviewerLib \
         %{buildroot}%{qtsm}/Resources/Icons \
         %{buildroot}%{qtsm}/Resources/UI
_sp=plugins/slicer

install -m0644 $_sp/MONAILabel/MONAILabel.py                    %{buildroot}%{qtsm}/
install -m0644 $_sp/MONAILabel/MONAILabelLib/*.py              %{buildroot}%{qtsm}/MONAILabelLib/
install -m0644 $_sp/MONAILabelReviewer/MONAILabelReviewer.py    %{buildroot}%{qtsm}/
install -m0644 $_sp/MONAILabelReviewer/MONAILabelReviewerLib/*.py %{buildroot}%{qtsm}/MONAILabelReviewerLib/
# Resources (icons + UI) from both modules into the shared dirs
install -m0644 $_sp/MONAILabel/Resources/Icons/*           %{buildroot}%{qtsm}/Resources/Icons/
install -m0644 $_sp/MONAILabel/Resources/UI/*.ui           %{buildroot}%{qtsm}/Resources/UI/
install -m0644 $_sp/MONAILabelReviewer/Resources/Icons/*   %{buildroot}%{qtsm}/Resources/Icons/
install -m0644 $_sp/MONAILabelReviewer/Resources/UI/*.ui   %{buildroot}%{qtsm}/Resources/UI/

# Generate the file list: own every installed file (incl. those dropped into the
# shared Resources dirs), but %%dir only our own Lib dirs — the qt-scripted-modules
# / Resources / Icons / UI dirs are owned by the 3dslicer package.
( cd %{buildroot} && find ".%{qtsm}" \( -type f -o -type l \) | sed 's|^\.||' ) \
    > %{_builddir}/monai.files
echo "%dir %{qtsm}/MONAILabelLib"         >> %{_builddir}/monai.files
echo "%dir %{qtsm}/MONAILabelReviewerLib" >> %{_builddir}/monai.files

%files -f %{_builddir}/monai.files
%license LICENSE
%doc plugins/slicer/README.md

%changelog
* Wed Jun 17 2026 Morgan Hough <morgan.hough@gmail.com> - 1.0-0.1.20260204git6ed8f8c6
- Initial package. SlicerMONAILabel (MONAILabel + MONAILabelReviewer modules)
  as a pure-scripted 3D Slicer extension installed into qt-scripted-modules.
  Client only; the MONAI Label server + monai/torch are run separately.
