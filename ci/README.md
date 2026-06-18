# CI: SCM source-completeness gate

COPR builds these specs with `rpkg srpm`, which clones **this git repo** and must
find every `Source`/`Patch` a spec references — either committed here or fetchable
from a URL (incl. `%forgesource`). Building from an *uploaded* SRPM instead hides
missing files (they come from the local `~/rpmbuild/SOURCES`), so a package can
read "green" on COPR while its SCM build is actually broken. That is what happened
to `vtk` and `paraview`.

## What runs

`.gitlab-ci.yml` → **`source-completeness`** job → `ci/audit-sources.sh`:
preprocesses every spec and fails the pipeline if any non-URL `Source`/`Patch`
file is neither in the repo nor allow-listed.

A non-blocking **`rpmlint`** job also reports spec findings.

## Fixing a failure

`MISSING: foo.spec -> bar.patch` means `bar.patch` is referenced but absent. Pick:

- **small patch / cmake shim / script / man page** → `git add bar.patch`
- **upstream tarball with a real URL** → make `Source0:` a URL, or use `%forgesource`
- **large un-hostable tarball (lookaside model)** → add a glob to
  `ci/lookaside-allowlist.txt` (and ideally give it a real URL/lookaside later)

Keep `lookaside-allowlist.txt` tight: anything not listed and not in the repo
fails CI — that is the gate doing its job.

## Toward Fedora

This mirrors Fedora dist-git: spec + small patches in git, big tarballs in a
lookaside cache (hash-pinned), never committed. The allow-list is the interim
stand-in for a real lookaside; replacing those entries with canonical
`Source` URLs / `%forgesource` is the path to full reproducibility and eventual
Fedora submission.
