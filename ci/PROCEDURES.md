# Packaging procedures (neurofedora COPR)

Hard-won gating for this repo. The recurring lesson: **a green COPR build proves
almost nothing on its own.** A package can compile yet be un-fetchable from git,
un-installable from a clean repo, frozen at a stale NVR, or unable to start. Each
stage below catches a class of failure that "it built" does not.

## The gates, in order

| # | Gate | Tool | Catches | Blocking? |
|---|------|------|---------|-----------|
| 1 | **SCM source-completeness** | `ci/audit-sources.sh` | a `Source`/`Patch` referenced but not committed (only worked via uploaded SRPM) — *vtk, paraview, +10* | yes, per push |
| 2 | **Source-URL liveness** | `ci/check-source-urls.sh` | a remote `Source` URL that 404s — *libspm, ITK6 remote modules* | scheduled / MR |
| 3 | **SRPM rebuild** | `rpkg srpm` (what COPR runs) | anything 1–2 miss + macro/spec errors | local / COPR |
| 4 | **Install from clean repo** | `ci/smoke/install-smoke.sh` | missing `Requires` (auto-deps stripped, none added back) — *paraview had no `Requires: vtk`* | local (mock) |
| 5 | **NVR actually deployed** | `ci/smoke/install-smoke.sh` | a rebuild that kept the same NVR and never superseded — *paraview `%autorelease` stuck at -1 for 9 releases* | local (mock) |
| 6 | **Binaries start / scripting works** | `ci/smoke/install-smoke.sh` | runtime breakage — *pvpython couldn't import paraview; missing runtime .so* | local (mock) |
| 7 | **rpmlint** | rpmlint | policy issues (license, rpath, SONAME) | informational |

## Golden rules

1. **Build from git (SCM), never from an uploaded SRPM.** Uploaded-SRPM "green"
   bundles files from your local `~/rpmbuild/SOURCES` and hides gates 1–2. If
   `rpkg srpm` from this repo works, COPR works. Make that your only path.
2. **Tarballs do not go in git.** Give every `Source` a real URL (or
   `%forgesource`); for un-hostable blobs use a lookaside cache. The interim
   `ci/lookaside-allowlist.txt` exempts known big tarballs from gate 1 — replace
   each with a URL/lookaside over time. (Fedora dist-git enforces exactly this.)
3. **A same-NVR rebuild does not deploy.** `%autorelease` is inert in this COPR
   (rpkg without rpmautospec) — it resolves to `1` every build, so rebuilds never
   supersede. Use an explicit incrementing `Release:` (grep `^Release:.*autorelease`
   to find offenders). Always confirm the *installed* NVR bumped, not just that a
   build went green.
4. **`__requires_exclude` needs a manual `Requires:` back.** If you strip
   auto-generated lib deps, add the package dependency explicitly or the package
   is un-installable alone.

## Failure taxonomy (triage a red build fast)

- **No `builder-live.log` (404), `version: null`, zero build-chroots** → it failed
  at the *source stage*. Read `results/.../srpm-builds/<id>/builder-live.log.gz`:
  - `Bad file: X: No such file` → gate 1 (commit X / give a URL).
  - `curl: (22) ... 404` / `Couldn't download` → gate 2 (fix/replace the URL).
- **`nothing provides` / `No matching` / `python(abi) = 3.14`** → dep-resolution.
  Often the rawhide py3.14→3.15 transition (clears when Fedora rebuilds the dep)
  or a tilde-version floor (`>= 6.0.0` can't match `6.0.0~b02`).
- **`fatal error` / `error:` with file:line** → real compile error (GCC/cmake
  forward-strictness, ITK/VTK API drift). Fix in a patch.
- **Builds green but CDash/smoke red** → gates 4–6 (deps, NVR, runtime).

## Running the gates

```bash
# fast, network-free, run on every change (also the CI source-completeness job):
bash ci/audit-sources.sh

# network: confirm all Source URLs still resolve (scheduled CI job):
bash ci/check-source-urls.sh

# heavy (needs mock): install + NVR + smoke a set of built packages:
ci/smoke/install-smoke.sh --manifest ci/smoke/manifest.txt
ci/smoke/install-smoke.sh paraview vtk ANTs      # or ad-hoc
```
