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
