# python-mne 1.12.1: COPR build times out in %check — diagnosis

Run this **off the AMD NUC** — that box is the CTest/CDash farm node and a second
heavy build there is what caused the August build-tree duel.

## What we know (confirmed from COPR build 10827012)

The package itself is fine — the wheel builds, installs, and byte-compiles.
The build dies in `%check`:

- Ran **exactly 5.00 h** (21:37:19 → 02:37:33) and was killed by COPR's default
  5 h timeout: `!! Copr timeout => sending INT`.
- The package has **no custom COPR timeout** set.
- The spec's own guard did **not** work. It passes `--session-timeout=2400`
  (40 min) with the comment *"a hard wall-clock cap ... so the build can never
  approach the COPR 5h limit"* — it approached and hit exactly that limit.
- **pytest produced ZERO output** — no `test session starts`, no
  `collected N items`. Only 2 log lines after the invocation, over 5 hours.

## Hypothesis to test

Zero output over 5 h points at pytest hanging **very early** (collection or
pytest-xdist worker startup) rather than slowly grinding through tests. The
competing explanation is that stdout was block-buffered and lost on SIGINT.
This run distinguishes the two.

Two contributing defects are fixed here regardless of which it is:

1. `--session-timeout` is not reliably enforced across **pytest-xdist** workers
   (`-n auto`), so the intended 40-min cap never fired.
2. `--timeout-method=thread` **cannot interrupt blocking C code**, and MNE spends
   its time in BLAS/HDF5/Qt native calls. `signal` (SIGALRM) can kill those.

## The run

`python-mne-check-diagnostic.patch` (next to this file) changes only `%check`:
`PYTHONUNBUFFERED=1`, an external `timeout -k 60 2700`, `--timeout-method=signal`,
and `-v`.

```bash
# on the ThinkPad
BUILD=10827012
URL=https://download.copr.fedorainfracloud.org/results/mhough/neurofedora/fedora-43-x86_64/$BUILD-python-mne
curl -O $URL/python-mne-1.12.1-4.fc43.src.rpm

rpm -ivh python-mne-1.12.1-4.fc43.src.rpm          # lands in ~/rpmbuild
patch -p1 -d ~/rpmbuild/SPECS < docs/python-mne-check-diagnostic.patch

rpmbuild -bs ~/rpmbuild/SPECS/python-mne.spec
mock -r fedora-43-x86_64 --rebuild ~/rpmbuild/SRPMS/python-mne-1.12.1-4.fc43.src.rpm \
     --resultdir=./mne-diag 2>&1 | tee mne-diag.log
```

## What the outcome tells us

| Observation | Meaning | Fix |
|---|---|---|
| Log now shows `test session starts` / `collected N items`, then stalls on a **named test** | A specific test hangs in native code | Add that test to the `-k` exclusion list; keep `--timeout-method=signal` |
| Stalls **before** `collected`, no test names | Hang is in **collection / xdist worker startup** | Try `-p no:xdist` (serial) to confirm; suspect a conftest import or plugin deadlock |
| Suite now **completes** inside 45 min | The old run was a buffering artifact + unbounded session; nothing truly hung | Ship the `timeout` + `signal` + unbuffered changes as the permanent fix |
| `timeout` fires at 45 min with visible progress | Suite is simply too big for the budget | Reduce scope (a representative subset) and/or raise the COPR per-package timeout |

## Applying the fix afterwards

If it's the last two rows, the permanent change is the same `%check` edit, plus
optionally raising COPR's cap for this package:

```bash
copr-cli edit-package-scm mhough/neurofedora --name python-mne \
    --clone-url <same> --spec python-mne.spec --type git --method rpkg \
    --webhook-rebuild on --timeout 21600
```

## Caveat on ownership

`python-mne.spec` is **not** in the GitLab neurofedora repo — this spec came out
of the SRPM, and the package appears to be maintained by a different
session/workflow. Its `%check` is deliberate and well-commented. Nothing has been
changed upstream; this directory is a diagnostic copy only.
