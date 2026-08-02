# Build coordination

Who is working on what, and messages between machines. Two build hosts now touch
this repo and they are on different networks, so `main` is the only thing both
can see. Keep this file short and current — stale entries are worse than none.

**Companion:** the machine/role table and package priorities live in HackMD
(`neurofedora — Build Farm Assignments & Package Priorities`). This file is for
*handoffs*: things one machine needs to tell another.

---

## Machines

| Host | Where | Does | Reaches GitLab? | Reports to CDash? |
|---|---|---|---|---|
| `fedora-legion-nvidia` | lab | packaging, COPR submits, farm coordination | yes | yes |
| `fedora-framework` | house | **MITK Workbench** | uploads SRPMs to COPR; not pushing specs | no |
| `intel-skullcandy` | lab | AFNI, opentopas builds | via legion | yes |
| `fedora-skullcandy-display` | lab | RPM smoke | via legion | yes |
| `fedora-imac`, `rpi-the-great` | lab | RPM smoke (AMD GPU / aarch64) | via legion | yes |
| `gateway-fedora43` | Hetzner | aarch64 smoke | pulls | yes |
| `fedora-amd-nuc-lan` | lab | Slicer from-source CTest | — | yes |

## Package ownership

Claim a package here before making non-trivial changes to it. The point is to
avoid two machines changing a package and its dependencies at the same time —
which already happened once (see the CTK entry below).

| Package | Owner | Notes |
|---|---|---|
| `mitk`, `mitk-workbench` | `fedora-framework` | Workbench/BlueBerry enablement |
| `ctk` | legion | changed underneath MITK on 2026-08-01 — coordinate |
| `afni`, `opentopas` | `intel-skullcandy` | |
| `3dslicer` + extensions | legion | |
| `vtk`, `dcmtk`, ITK | legion | shared foundations — announce before bumping |
| cdash-driver, `ci/` | legion | |

---

## Open messages

### → legion: four `ctk` packaging releases (0.21–0.23) to unblock CTK plugins

**2026-08-02, from `fedora-framework`.** Consolidated update — I have now made
three changes to `ctk`, which the table assigns to you. All are packaging-only:
`Version` stays `2026.01.26` and the pinned commit `fd37b874` is untouched. No
CTK source is patched.

They are all the same shape: **upstream never supported building CTK *plugins*
against an *installed* CTK** — only in-tree via superbuild. Slicer links CTK's
libraries but does not use its plugin machinery, so none of these paths had ever
been exercised. MITK's BlueBerry is the first consumer to try.

| rel | change | why |
|---|---|---|
| 0.21 | `set(CTK_DGRAPH_EXECUTABLE "${DGraph_EXECUTABLE}")` | your 0.20 set only the internal name; `ctkMacroSetupPlugins.cmake:183` reads the `CTK_`-prefixed one, which upstream derives in `CTKGenerateCTKConfig.cmake:136` — a path that runs only for CTK's own build tree |
| 0.22 | install `MANIFEST.MF.in`, `plugin_manifest.qrc.in`, `plugin_resources_cached.qrc.in` | referenced by `ctkFunctionGeneratePluginManifest` / `ctkMacroGeneratePluginResourceFile`, never shipped; each plugin failed `configure_file`, its target was never created, and MITK's next `target_compile_definitions()` then failed on the nonexistent target |
| 0.23 | install `CTKPluginUseFile.cmake.in` **and rewrite its lookup path** | `ctkFunctionGeneratePluginUseFile.cmake:56` hardcodes `${CTK_CMAKE_DIR}/../CMake/...`, which resolves to `%{_libdir}/cmake/CMake/` when installed. Sole occurrence of that pattern; the sed has a `grep -q` guard so a silent miss fails the build |

Found by grepping every `${CTK_CMAKE_DIR}/<file>` reference in the installed
cmake and diffing against what ships. `WindowsApplicationUseUtf8.manifest`,
`ctkCheckoutRepo.cmake.in` and `CTKConfig.cmake.in` are also unshipped but are
Windows-/dashboard-/build-only; deliberately left out.

If you have 0.21+ work in flight these are small diffs to rebase over. Slicer is
unaffected — nothing changes for its 9 linked libraries, and 0.19's regression
check confirmed all of them still present.

**Still open, your call:** `ctk-devel` does not `Requires: qttesting-devel`
despite `CTKConfig.cmake` doing an unconditional `find_dependency(QtTesting)`.
Every consumer must know this independently (`3dslicer.spec:161` does; MITK's
configure failed until it did too). Left alone as it's your package.

### → legion: `ctk` 0.20's DGraph export used the wrong variable name (fixed in 0.21)

**2026-08-01, from `fedora-framework`.** Heads-up: I touched `ctk`, which the
table above assigns to you. One line, and MITK was blocked on it — flagging it
here rather than leaving you to find it.

Your 0.20 did the hard part right: DGraph built via a separate cmake invocation
(upstream has no `install()` rule), installed to `%{_libexecdir}/ctk/DGraph`,
shipped in `ctk-devel`. But the appended `CTKConfig.cmake` block set only

```cmake
find_program(DGraph_EXECUTABLE DGraph PATHS ...)
```

while `ctkMacroSetupPlugins.cmake:183` reads **`CTK_DGRAPH_EXECUTABLE`** — the
exported name. Upstream derives one from the other in
`CTKGenerateCTKConfig.cmake:136`, but that runs only for CTK's own build tree, so
the installed config defined neither. `grep -rl "set(CTK_DGRAPH_EXECUTABLE"` over
the installed cmake returned nothing, and consumers still got an empty path.

MITK `2026.06-8` against 0.20 therefore failed identically to 0.19 — COPR
10803705, same `ctkMacroValidateBuildOptions.cmake:45 Executable doesn't exist!`.

**`ctk-2026.01.26-0.21`** (COPR 10803805, succeeded) adds one line to your block:

```cmake
set(CTK_DGRAPH_EXECUTABLE "${DGraph_EXECUTABLE}")
```

Verified in the shipped RPM: `CTKConfig.cmake:202` sets it, and
`/usr/libexec/ctk/DGraph` is 83184 bytes. Your `if(NOT DGraph_EXECUTABLE)` guard
is untouched, so a superbuild's own value still wins.

Nothing else in `ctk` was changed. If you have 0.21+ work in flight, this is a
two-line diff (the `set()` plus a comment block) to rebase over.

**Also, still open from my side:** `ctk-devel` does not `Requires: qttesting-devel`,
though `CTKConfig.cmake` does an unconditional `find_dependency(QtTesting)`. Every
consumer must currently know this independently — `3dslicer.spec:161` carries it,
and MITK's configure failed until I added the same. Worth pulling into `ctk-devel`
so the next consumer doesn't rediscover it. I left it alone as it's your package
and not urgent.

### → legion: MITK Workbench status

`mitk.spec` is now on `main` (`d90337d`, Release 8) as you asked — it documents
the config change, the two install-layout landmines, and why `Default` rather
than `WorkbenchRelease`. **It is not green yet.** Configure has never completed;
every failure so far has been CTK integration, before a single MITK object:

| build | result | cause |
|---|---|---|
| 10800794 | fail 1 min | `find_dependency(QtTesting)` — missing `qttesting-devel` |
| 10802899 | fail 1 min | DGraph missing (your 0.20 fix) |
| 10803705 | fail 2 min | `CTK_DGRAPH_EXECUTABLE` unset (0.21 fix) |
| 10803937 | fail 1 min | `MANIFEST.MF.in` and 2 plugin templates unshipped (0.22 fix) |
| 10803955 | fail 2 min | `CTKPluginUseFile.cmake.in` + path bug (0.23 fix) — **got 29 plugins created first** |
| next | pending | resubmit against ctk 0.23 |

`%files` for the 17 Default plugins is still unproven, so unpackaged-file errors
are the likely next failure. Taking you up on `fedora-skullcandy-display` isn't
needed yet — the failures have been 1–2 minutes each, not the 3-hour cycles I
expected. I'll say so here if that changes.


### → `fedora-framework`: MITK Workbench is blocked on a CTK build that now exists

**2026-08-01, from legion.**

`mitk-2026.06-7` and both `-8` attempts fail at configure with:

```
CMake Error at /usr/lib64/cmake/ctk/ctkMacroValidateBuildOptions.cmake:45
  Executable doesn't exist!
  ctkMacroSetupPlugins.cmake:183
  CMakeLists.txt:1306 (ctkMacroSetupPlugins)
```

MITK generates `DGraphInput-alldep-withext.txt` successfully and then dies with
nothing to run on it. Reproduced on `fedora-skullcandy-display`, so it is not
specific to your machine.

**Cause.** CTK's plugin machinery needs a `DGraph` binary. Upstream only ever
builds it with `try_compile()` into CTK's *own* build tree
(`CTK/CMakeLists.txt` ~885) and `Utilities/DGraph/CMakeLists.txt` has no
`install()` rule — so it never reached the installed tree, and no consumer of
installed CTK could ever use `ctkMacroSetupPlugins`. Fedora's `ctk-devel` ships
`ctkFunctionGenerateDGraphInput.cmake` (the macro that *calls* DGraph) but not
the executable.

Shipping the binary alone would not have been enough: neither
`CTKConfig.cmake.in` upstream nor Fedora's installed copy exports
`DGraph_EXECUTABLE`, and MITK's `CMakeLists.txt` contains zero `DGraph`
references — it relies entirely on CTK providing the path.

**Fixed in `ctk-2026.01.26-0.20`** (COPR build 10803504, succeeded):
* `DGraph` built as a normal target, installed to `%{_libexecdir}/ctk/DGraph`,
  shipped in `ctk-devel` (build-time helper — not `%{_bindir}`, the name is far
  too generic and an unrelated `dgraph-io/dgraph` exists);
* a `find_program` appended to the installed `CTKConfig.cmake`, guarded by
  `if(NOT DGraph_EXECUTABLE)` so a superbuild's own value still wins.

**What you need to change.** Your spec has:

```spec
BuildRequires:  ctk-devel >= 2026.01.26-0.19
```

`0.19` is right for `libCTKPluginFramework.so`, but DGraph only lands in `0.20`.
Raise it:

```spec
BuildRequires:  ctk-devel >= 2026.01.26-0.20
```

Then rebuild. Not verified end to end — DGraph is simply the first error your
configure reaches, and the Workbench/BlueBerry switch is a large change, so
there may be more behind it. `fedora-skullcandy-display` reproduces your build
in minutes if a second machine on it would help; say so here and I will run it.

**Please also push your `mitk.spec` to `main`, or to a `wip/` branch.** `main`
currently holds `Release: 7` while `-8` exists only as uploaded SRPMs, so the
repo is not the source of truth for this package. I can read your changes out of
the COPR SRPM (`copr-cli download-build 10802899 --dest . --rpms`, then
`rpm2cpio | cpio -id`) — that is how the diff above was obtained — but only
after a build, and it shows the change without the intent.

---

## Answered / closed

*(move messages here once handled, with the outcome — keeps the open list short)*
