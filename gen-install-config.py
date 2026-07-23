#!/usr/bin/env python3
"""
Generate a relocatable install-tree SlicerConfig.cmake (+ SlicerTargets.cmake)
from the build-tree SlicerConfig.cmake that Slicer installs verbatim.

Upstream's SlicerGenerateSlicerConfig.cmake only ever configures the build-tree
variant (configure_file -> ${Slicer_BINARY_DIR}); the install-tree half its own
header promises was never implemented, and there is no install(EXPORT) for
Slicer's own libraries. So the installed config points every path at the
(vanished) COPR build tree and ships no imported targets.

This script fixes both, purely at packaging time:
  * scalar build-tree paths  -> install-tree paths under the computed root
  * per-component include dirs -> the matching installed include/ dirs
  * unmapped build-tree paths -> neutralized (set to "") — these are headers
    Slicer never installs (loadable-module internals), which extensions don't need
  * a generated SlicerTargets.cmake with IMPORTED targets for every installed lib

Usage:
  gen-install-config.py <orig SlicerConfig.cmake> <out dir> [--root <abs prefix>]

Without --root the emitted config derives the prefix from its own location at
load time (${CMAKE_CURRENT_LIST_DIR}/../..) — fully relocatable, the prod form.
With --root it hardcodes an absolute prefix — used for dev-testing against the
already-installed /usr/lib/slicer without sudo.
"""
import os
import re
import sys

def _detect_slicer_subdir():
    # Derive the versioned subdir (Slicer-X.Y) from the <out dir> positional arg
    # the spec passes (<prefix>/lib/Slicer-X.Y) so this never has to be hand-bumped
    # on a Slicer version change. Falls back to the current stable series.
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(pos) >= 2:
        b = os.path.basename(os.path.normpath(pos[1]))
        if b.startswith("Slicer-"):
            return b
    return "Slicer-5.12"

SLICER_SUBDIR = _detect_slicer_subdir()

# ---- scalar path variables: var name -> install-relative path (under root), or None to neutralize
SCALAR_MAP = {
    "Slicer_CMAKE_DIR":             "lib/%s/CMake" % SLICER_SUBDIR,
    "Slicer_EXTENSIONS_CMAKE_DIR":  "lib/%s/CMake" % SLICER_SUBDIR,
    "Slicer_EXTENSION_GENERATE_CONFIG": "lib/%s/CMake/SlicerExtensionGenerateConfig.cmake" % SLICER_SUBDIR,
    "Slicer_EXTENSION_CPACK":       "lib/%s/CMake/SlicerExtensionCPack.cmake" % SLICER_SUBDIR,
    "Slicer_EXTENSION_CPACK_BUNDLE_FIXUP": "lib/%s/CMake/SlicerExtensionCPackBundleFixup.cmake.in" % SLICER_SUBDIR,
    "Slicer_EXPORT_HEADER_TEMPLATE": "lib/%s/CMake/qSlicerExport.h.in" % SLICER_SUBDIR,
    "Slicer_USE_FILE":              "lib/%s/UseSlicer.cmake" % SLICER_SUBDIR,
    "Slicer_HOME":                  "",          # = root
    "Slicer_BINARY_DIR":            "",          # = root
    "Slicer_LAUNCHER_EXECUTABLE":   "Slicer",
    # neutralized (not installed / not needed for C++ extension builds):
    "vtkAddon_CMAKE_DIR":           None,
    "Slicer_LICENSE_FILE":          None,
    "Slicer_README_FILE":           None,
    "Slicer_QRCC_SCRIPT":           None,
    "Slicer_LOGOS_RESOURCE":        None,
    "Slicer_CXX_MODULE_TEST_TEMPLATES_DIR":    None,
    "Slicer_PYTHON_MODULE_TEST_TEMPLATES_DIR": None,
    # VTK wrap-hierarchy files for python-wrapping extension VTK classes; the
    # foundation -43 %install ships the build-tree hierarchy files here.
    "Slicer_VTK_WRAP_HIERARCHY_DIR": "lib/%s/hierarchy" % SLICER_SUBDIR,
}

# special: launch commands are "<launcher>;--launch"
LAUNCH_VARS = {"Slicer_LAUNCH_COMMAND", "SEM_LAUNCH_COMMAND"}

# ---- include-dir variables: var name -> list of install-relative include dirs
def _inc(*parts):
    return ["include/" + p for p in parts]

INCLUDE_MAP = {
    "MRMLCore_INCLUDE_DIRS":            _inc("MRMLCore"),
    "MRMLLogic_INCLUDE_DIRS":           _inc("MRMLLogic"),
    "MRMLCLI_INCLUDE_DIRS":             _inc("MRMLCLI"),
    "qMRMLWidgets_INCLUDE_DIRS":        _inc("qMRMLWidgets"),
    "RemoteIO_INCLUDE_DIRS":            _inc("RemoteIO"),
    "vtkITK_INCLUDE_DIRS":              _inc("vtkITK"),
    "vtkTeem_INCLUDE_DIRS":             _inc("vtkTeem"),
    "vtkSegmentationCore_INCLUDE_DIRS": _inc("vtkSegmentationCore"),
    "ITKFactoryRegistration_INCLUDE_DIRS": _inc("ITKFactoryRegistration"),
    "Slicer_Libs_INCLUDE_DIRS": _inc("MRMLCore", "MRMLLogic", "MRMLCLI",
                                     "MRMLDisplayableManager", "qMRMLWidgets",
                                     "RemoteIO", "vtkITK", "vtkTeem",
                                     "vtkSegmentationCore", "ITKFactoryRegistration"),
    "Slicer_Base_INCLUDE_DIRS": _inc(SLICER_SUBDIR,
                                     "%s/qSlicerApp" % SLICER_SUBDIR,
                                     "%s/qSlicerBaseQTApp" % SLICER_SUBDIR,
                                     "%s/qSlicerBaseQTCLI" % SLICER_SUBDIR,
                                     "%s/qSlicerBaseQTCore" % SLICER_SUBDIR,
                                     "%s/qSlicerBaseQTGUI" % SLICER_SUBDIR,
                                     "%s/qSlicerModulesCore" % SLICER_SUBDIR),
    # vtkAddon is a separate system package; let find_package(vtkAddon) supply it
    "vtkAddon_INCLUDE_DIRS": [],
}

# Installed libraries that get IMPORTED targets. Names are the bare target names
# Slicer extension macros link against (target_link_libraries(... qSlicerBaseQTGUI)).
# Excludes bundled openssl (libcrypto/libssl*) and the *Python / *PythonQt wrappers.
TARGET_LIBS = [
    "SlicerBaseLogic", "SlicerBaseCLI",
    "MRMLCore", "MRMLCLI", "MRMLLogic", "MRMLDisplayableManager",
    "qMRMLWidgets", "RemoteIO", "ITKFactoryRegistration",
    "vtkITK", "vtkSegmentationCore", "vtkTeem",
    "qSlicerApp", "qSlicerBaseQTApp", "qSlicerBaseQTCLI",
    "qSlicerBaseQTCore", "qSlicerBaseQTGUI", "qSlicerModulesCore",
]

# The Qt-based ("q"-prefixed) Slicer libs. Their public headers pull in Qt, and
# (the -53 fix) their object code references symbols across the whole Slicer GUI
# stack + CTK — in the in-tree build those were carried as each target's
# INTERFACE_LINK_LIBRARIES. We split TARGET_LIBS into Qt / non-Qt so a pure CLI
# extension linking MRMLCLI doesn't drag in Qt/CTK, while a GUI module linking
# qSlicerBaseQTGUI inherits the full closure transitively.
QT_TARGET_LIBS = {
    "qMRMLWidgets", "qSlicerApp", "qSlicerBaseQTApp", "qSlicerBaseQTCLI",
    "qSlicerBaseQTCore", "qSlicerBaseQTGUI", "qSlicerModulesCore",
}
NONQT_TARGET_LIBS = [t for t in TARGET_LIBS if t not in QT_TARGET_LIBS]
ALLQT_TARGET_LIBS = [t for t in TARGET_LIBS if t in QT_TARGET_LIBS]

BUILD_PATH_RE = re.compile(r'/builddir/build/BUILD/')

# System external-project cmake-config dirs whose directory name does NOT match
# the find_package() name (so plain search can't locate them) — Slicer's build
# passed these as explicit *_DIR. They live at fixed system locations (/usr),
# unrelated to the relocatable Slicer prefix, so absolute paths are correct.
# Guarded with EXISTS so a packaging move just silently skips the stale hint.
EP_DIR_HINTS = {
    "CTKAppLauncherLib_DIR": "/usr/lib64/cmake/CTKAppLauncher",
    "CTKAppLauncher_DIR":    "/usr/lib64/cmake/CTKAppLauncher",
    "Teem_DIR":              "/usr/lib64/cmake",
    "QtTesting_DIR":         "/usr/lib64/cmake/qttesting",
    "qRestAPI_DIR":          "/usr/lib64/cmake/qRestAPI",
}


def detect_build_root(text):
    """Find the build-tree path prefix(es) so we can recognize broken values."""
    m = re.search(r'set\(Slicer_BINARY_DIR "([^"]+)"\)', text)
    return m.group(1) if m else None


def is_broken(value):
    return bool(BUILD_PATH_RE.search(value))


def root_expr(root):
    """The CMake expression for the install prefix in emitted set() values.
    Private name to avoid colliding with upstream's own Slicer_INSTALL_ROOT
    (which is later reset to "./" for CPack-relative install dirs)."""
    return "${_SLICER_RELOC_ROOT}"


def map_value(varname, value, root):
    """Return the replacement value (a CMake string list) for a broken set()."""
    rexpr = root_expr(root)
    if varname == "SlicerExecutionModel_CLI_LIBRARY_WRAPPER_CXX":
        # Slicer's generated CLI wrapper (Base/CLI/SEMCommandLineLibraryWrapper.cxx);
        # the foundation %install ships it into the CMake dir. CLI-module
        # extensions (e.g. SlicerDMRI) need it via SEMMacroBuildCLI.
        return "%s/lib/%s/CMake/SEMCommandLineLibraryWrapper.cxx" % (rexpr, SLICER_SUBDIR)
    if varname == "SlicerExecutionModel_EXTRA_INCLUDE_DIRECTORIES":
        # Base/CLI headers (flattened into include/Slicer-5.11 by -46+) + the
        # installed ITKFactoryRegistration include dir.
        return "%s/include/%s;%s/include/ITKFactoryRegistration" % (
            rexpr, SLICER_SUBDIR, rexpr)
    if varname == "Slicer_VTK_WRAP_HIERARCHY_DIR":
        # OUTPUT dir for the consuming extension's own wrap-hierarchy files — must
        # be the extension's (writable) build dir, not the read-only install. The
        # dependency hierarchy files are referenced by explicit install paths via
        # the per-target *_WRAP_HIERARCHY_FILE vars, so they still resolve.
        return "${CMAKE_BINARY_DIR}"
    if varname in LAUNCH_VARS:
        return "%s/Slicer;--launch" % rexpr
    if varname in SCALAR_MAP:
        rel = SCALAR_MAP[varname]
        if rel is None:
            return ""
        if rel == "":
            return rexpr
        return "%s/%s" % (rexpr, rel)
    if varname in INCLUDE_MAP:
        dirs = INCLUDE_MAP[varname]
        return ";".join("%s/%s" % (rexpr, d) for d in dirs)
    # Per-target VTK wrap-hierarchy files: remap the build-tree
    # <Target>Hierarchy.txt to the dir the foundation -43 %install ships them in,
    # so python-wrapped extension modules can resolve their link hierarchy.
    if varname.endswith("_WRAP_HIERARCHY_FILE"):
        m = re.search(r'/([^/"\s]+Hierarchy\.txt)', value)
        if m:
            return "%s/lib/%s/hierarchy/%s" % (rexpr, SLICER_SUBDIR, m.group(1))
        return ""
    # Unknown broken var (loadable-module internals etc.) -> neutralize
    return ""


SET_RE = re.compile(r'^(\s*)set\((\S+)\s+"([^"]*)"(.*)$', re.DOTALL)


def transform(text, root):
    out_lines = []
    lines = text.splitlines(keepends=False)
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Re-join a multi-line set(...) call: accumulate from the line containing
        # 'set(' until parentheses balance (value may start on a following line).
        if re.match(r'\s*set\(', line):
            j = i
            buf = line
            while (buf.count('(') > buf.count(')')) and j + 1 < n:
                j += 1
                buf += "\n" + lines[j]
            block = buf
            i = j
        else:
            block = line

        hm = re.match(r'(\s*)set\(\s*(\S+)', block)
        if hm and is_broken(block):
            indent, var = hm.groups()
            newval = map_value(var, block, root)
            up = block.upper()
            if 'CACHE' in up:
                # preserve the CACHE ... FORCE) clause verbatim
                cache_part = block[up.index('CACHE'):]
                out_lines.append('%sset(%s "%s" %s' % (indent, var, newval, cache_part))
            else:
                out_lines.append('%sset(%s "%s")' % (indent, var, newval))
        else:
            out_lines.append(block)
        i += 1

    body = "\n".join(out_lines) + "\n"

    # Inject the install-root definition right after the cmake_minimum_required line
    if root:
        rootdef = 'set(_SLICER_RELOC_ROOT "%s")\n' % root
    else:
        rootdef = ('get_filename_component(_SLICER_RELOC_ROOT\n'
                   '  "${CMAKE_CURRENT_LIST_DIR}/../.." ABSOLUTE)\n')
    header = ("\n# --- install-tree prefix (injected by gen-install-config.py) ---\n"
              + rootdef +
              "# --------------------------------------------------------------\n")
    anchor = re.search(r'cmake_minimum_required\([^)]*\)\n', body)
    if anchor:
        pos = anchor.end()
        body = body[:pos] + header + body[pos:]
    else:
        body = header + body

    # Drop the hard compiler-path pin: it FATAL-errors when an extension is later
    # built with a compatible-but-different-path gcc (ccache/cc realpath mismatch).
    # Distro packages must not pin the exact compiler binary. (C++ standard /
    # required / extensions pins are kept — those are genuinely useful.)
    body = re.sub(r'set\((Slicer_CMAKE_C(?:XX)?_COMPILER)\s+"[^"]*"\)',
                  r'set(\1 "")', body)
    body = re.sub(r'slicer_config_set_compiler_ep\(\s*(CMAKE_C(?:XX)?_COMPILER)\s+"[^"]*"',
                  r'slicer_config_set_compiler_ep( \1 ""', body)

    # Inject explicit *_DIR hints for system externals whose cmake-config dir
    # name doesn't match the find_package() name, right before the EP loop.
    hint_lines = ["", "# install-tree external-project hints (injected) "
                  "— dir name != package name"]
    for var, path in EP_DIR_HINTS.items():
        hint_lines.append(
            'if(NOT DEFINED %s AND EXISTS "%s")' % (var, path))
        hint_lines.append('  set(%s "%s")' % (var, path))
        hint_lines.append('endif()')
    hint_block = "\n".join(hint_lines) + "\n"
    body = re.sub(r'(\n# Include external projects\n)',
                  hint_block + r'\1', body, count=1)

    # Teem has no TeemUse.cmake in Fedora, so UseSlicer's include(${Teem_USE_FILE})
    # fails — add Teem to the NO_USEFILE list (modern CMake needs no use-file).
    body = re.sub(r'(set\(Slicer_EXTERNAL_PROJECTS_NO_USEFILE )([^)]*)\)',
                  lambda m: m.group(1) + m.group(2) +
                  ('' if 'Teem' in m.group(2) else ';Teem') + ')',
                  body, count=1)

    # Point the targets-file include at our generated SlicerTargets.cmake
    body = re.sub(r'if\(EXISTS "[^"]*SlicerTargets\.cmake"',
                  'if(EXISTS "${CMAKE_CURRENT_LIST_DIR}/SlicerTargets.cmake"',
                  body)
    body = re.sub(r'include\("[^"]*SlicerTargets\.cmake"\)',
                  'include("${CMAKE_CURRENT_LIST_DIR}/SlicerTargets.cmake")',
                  body)
    return body


def gen_targets(root, module_dir=None):
    L = ["# Generated by gen-install-config.py — IMPORTED targets for installed Slicer libs.",
         "# Replaces the missing install(EXPORT SlicerTargets) upstream never wired up.",
         "# This file lives at <prefix>/lib/Slicer-5.11/ alongside the .so libraries.",
         'get_filename_component(_slicer_libdir "${CMAKE_CURRENT_LIST_DIR}" ABSOLUTE)',
         ""]
    # Public headers of these libs (e.g. MRMLCore's vtkMRMLNode.h) #include vtkAddon
    # headers (vtkLoggingMacros.h, ...) and Slicer base headers in subdirs (e.g.
    # qSlicerBaseQTGUI/qSlicerAbstractModuleWidget.h). The in-tree build propagated
    # these via the real targets' interface includes; carry them on the imported
    # targets so an extension linking them inherits the dirs. The include base is
    # <prefix>/include/Slicer-5.11 (libdir is <prefix>/lib/Slicer-5.11).
    L += [
        'get_filename_component(_slicer_prefix "${_slicer_libdir}/../.." ABSOLUTE)',
        'set(_slicer_incbase "${_slicer_prefix}/include/%s")' % SLICER_SUBDIR,
        'set(_slicer_iface_inc',
        '    "/usr/include/vtkAddon"',
        '    "${_slicer_incbase}"',
        '    "${_slicer_incbase}/qSlicerApp"',
        '    "${_slicer_incbase}/qSlicerBaseQTApp"',
        '    "${_slicer_incbase}/qSlicerBaseQTCLI"',
        '    "${_slicer_incbase}/qSlicerBaseQTCore"',
        '    "${_slicer_incbase}/qSlicerBaseQTGUI"',
        '    "${_slicer_incbase}/qSlicerModulesCore")',
        '',
        '# VTK closure: the in-tree build propagated VTK includes AND libraries',
        '# through the real Slicer targets. Linking the VTK:: imported targets here',
        '# carries both (each VTK module target exports its own include dir), so an',
        '# extension linking a Slicer lib (e.g. MRMLCore) inherits VTK without the',
        '# install(EXPORT) upstream never wired up. find_package(VTK) ran in the',
        '# including SlicerConfig, so these targets exist.',
        'set(_slicer_vtk_ifacelibs "")',
        'foreach(_m CommonCore CommonExecutionModel CommonDataModel CommonMath',
        '          CommonMisc CommonSystem CommonTransforms CommonColor',
        '          CommonComputationalGeometry FiltersCore FiltersGeneral',
        '          FiltersSources FiltersGeometry FiltersModeling FiltersExtraction',
        '          ImagingCore ImagingGeneral ImagingStencil ImagingStatistics',
        '          IOCore IOXML IOImage IOLegacy IOGeometry InteractionStyle',
        '          RenderingCore RenderingFreeType RenderingOpenGL2)',
        '  if(TARGET VTK::${_m})',
        '    list(APPEND _slicer_vtk_ifacelibs VTK::${_m})',
        '  endif()',
        'endforeach()',
        '',
        '# -53 fix: CTK closure. The Slicer GUI libs (qSlicerBaseQTGUI, qMRMLWidgets)',
        '# reference CTK symbols (ctkCollapsibleButton -> CTKWidgets,',
        '# ctkVTKObjectEventsObserver -> CTKVisualizationVTKCore). The in-tree build',
        '# carried these via the targets\' interface; our imported targets must too.',
        '# Glob the system CTK .so set (ctk-devel ships the unversioned dev symlinks',
        '# at build time; runtime DT_NEEDED resolves to ctk-widgets\' .so.N) rather',
        '# than hardcode the module list. Empty glob (CTK absent) -> empty list.',
        'file(GLOB _slicer_ctk_libs "/usr/lib64/libCTK*.so")',
        '',
        '# -54 fix: ITK closure. The Slicer C++ libs (vtkITK, MRMLCore, MRMLLogic,',
        '# SlicerBaseLogic, vtkTeem, vtkSegmentationCore, ITKFactoryRegistration) are',
        '# built on ITK and the in-tree build propagated the ITK libraries through',
        '# their interface. Without it, a CLI/loadable module that links a Slicer lib',
        '# and uses ITK itself (e.g. SlicerDMRI FiberBundleLabelSelect reading images)',
        '# fails with undefined itk::Object::GetDebug / itk::InvalidRequestedRegionError',
        '# — SEM\'s ${ITK_LIBRARIES} resolves empty against the install tree. Glob the',
        '# Fedora ITK .so set (InsightToolkit5-devel ships the unversioned symlinks at',
        '# build time; runtime DT_NEEDED resolves to the versioned .so). --as-needed',
        '# prunes the unused ones from the consumer\'s DT_NEEDED. Both casings: the',
        '# uppercase ITK modules (libITKCommon-*) and the lowercase third-party',
        '# (libitkvnl-*, libitksys-*). Empty glob (ITK absent) -> empty list.',
        'file(GLOB _slicer_itk_libs "/usr/lib64/libITK*.so" "/usr/lib64/libitk*.so")',
        '',
    ]
    for t in TARGET_LIBS:
        # The Qt-based libs (Slicer's "q"-prefixed targets, qSlicer*/qMRMLWidgets)
        # have public headers that #include <QObject>/<QWidget>, and the in-tree
        # build propagated Qt via their interface. Carry that so extensions
        # linking them inherit the Qt include dirs (and Qt libs) — otherwise a
        # consumer (e.g. PlusRemote logic using qSlicerCoreApplication) fails on
        # "QObject: No such file or directory".
        # -53 fix: carry the inter-Slicer link closure on each imported target so
        # an extension linking one Slicer lib inherits the siblings it depended on
        # in the in-tree build (e.g. a module Widgets lib links qMRMLWidgets and
        # needs qSlicerBaseQTGUI/qSlicerBaseQTCore + CTK transitively). Qt libs get
        # the full Slicer set + Qt + CTK; non-Qt libs get only the other non-Qt
        # Slicer libs + VTK, so a pure-CLI extension isn't forced to drag in Qt/CTK.
        _qt = t in QT_TARGET_LIBS
        if _qt:
            _siblings = [x for x in (NONQT_TARGET_LIBS + ALLQT_TARGET_LIBS) if x != t]
            _ifacelibs = ('Qt6::Core;Qt6::Gui;Qt6::Widgets;Qt6::Core5Compat;'
                          + (';'.join(_siblings) + ';' if _siblings else '')
                          + '${_slicer_vtk_ifacelibs};${_slicer_ctk_libs};${_slicer_itk_libs}')
        else:
            _siblings = [x for x in NONQT_TARGET_LIBS if x != t]
            _ifacelibs = ((';'.join(_siblings) + ';' if _siblings else '')
                          + '${_slicer_vtk_ifacelibs};${_slicer_itk_libs}')
        L += [
            'if(NOT TARGET %s)' % t,
            '  add_library(%s SHARED IMPORTED)' % t,
            '  set_target_properties(%s PROPERTIES' % t,
            '    IMPORTED_LOCATION "${_slicer_libdir}/lib%s.so"' % t,
            '    INTERFACE_INCLUDE_DIRECTORIES "${_slicer_iface_inc}"',
            '    INTERFACE_LINK_LIBRARIES "%s")' % _ifacelibs,
            'endif()', '',
        ]

    # Imported targets for the installed loadable-module libraries (in
    # qt-loadable-modules/). Extensions link these by bare target name
    # (e.g. vtkSlicerMarkupsModuleMRML); without imported targets CMake emits
    # "-lvtkSlicerMarkupsModuleMRML" and the linker can't find it (non-standard
    # dir). Scan the install dir so every module lib resolves to its full path.
    # They also carry the VTK closure + Slicer include base so consumers inherit
    # both (the module MRML/Logic headers #include VTK and Slicer base headers).
    if module_dir and os.path.isdir(module_dir):
        L += ['', '# loadable-module libraries (qt-loadable-modules)']
        for so in sorted(os.listdir(module_dir)):
            # libfoo.so -> target "foo"; skip versioned/python-wrapper/.so.N
            if not so.startswith('lib') or not so.endswith('.so'):
                continue
            tname = so[3:-3]
            L += [
                'if(NOT TARGET %s)' % tname,
                '  add_library(%s SHARED IMPORTED)' % tname,
                '  set_target_properties(%s PROPERTIES' % tname,
                '    IMPORTED_LOCATION "${_slicer_libdir}/qt-loadable-modules/%s"' % so,
                '    INTERFACE_INCLUDE_DIRECTORIES "${_slicer_iface_inc}"',
                '    INTERFACE_LINK_LIBRARIES "${_slicer_vtk_ifacelibs};${_slicer_itk_libs}")',
                'endif()',
            ]
    return "\n".join(L) + "\n"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    root = None
    for a in sys.argv[1:]:
        if a.startswith("--root="):
            root = a.split("=", 1)[1]
    if len(args) < 2:
        print(__doc__)
        sys.exit(2)
    src, outdir = args[0], args[1]
    os.makedirs(outdir, exist_ok=True)
    with open(src) as f:
        text = f.read()
    bld = detect_build_root(text)
    print("detected build root:", bld)
    cfg = transform(text, root)
    with open(os.path.join(outdir, "SlicerConfig.cmake"), "w") as f:
        f.write(cfg)
    with open(os.path.join(outdir, "SlicerTargets.cmake"), "w") as f:
        f.write(gen_targets(root, module_dir=os.path.join(outdir, "qt-loadable-modules")))
    # report residual broken paths
    residual = [ln for ln in cfg.splitlines() if BUILD_PATH_RE.search(ln)]
    print("wrote SlicerConfig.cmake (%d lines), SlicerTargets.cmake (%d libs)"
          % (len(cfg.splitlines()), len(TARGET_LIBS)))
    print("residual build-path lines:", len(residual))
    for ln in residual[:20]:
        print("  !", ln.strip()[:140])


if __name__ == "__main__":
    main()
