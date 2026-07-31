# Slicer CTest farm

Two ways to turn a machine into a node that builds the **Fedora** Slicer config
(`rpmbuild -bc --with testing`), runs Slicer's own CTest suite, and submits to
[my.cdash.org/neurofedora](https://my.cdash.org/index.php?project=neurofedora).
Both drive the *same* logic (`run-slicer-ctest.sh` → `slicer-ctest-loop.sh`).

## `farm-run.sh` — rootless, any host with podman (recommended)

Runs the whole build+test **inside a rootless container**. The host is never
modified (no VTK swap, no root service) — it only needs `podman`.

```sh
./farm-run.sh                       # stable, one cycle, submit to CDash
./farm-run.sh --no-submit           # build + test locally, publish nothing
./farm-run.sh --track preview --loop  # continuous preview (5.13) node, detached
./farm-run.sh --dry-run             # print the exact podman commands
```

- `--oneshot` (default) runs a single cycle and exits; `--loop` runs a detached
  `--restart=always` container (`-f` keeps it attached).
- The dashboard **site** name defaults to `<hostname>-container`; set with `--site`.
- First run builds the image (Fedora 44 base + COPR VTK 9.6 + all Slicer
  BuildRequires, baked once). The first **build cycle** is long (~7–9 h).
- Uninstall a loop node: `podman rm -f neurofedora-farm-<track>` (+ `podman rmi`).

## `farm-bootstrap.sh` — dedicated Fedora box, bare metal

Installs a 24/7 systemd service directly on the host. **It makes system-wide,
hard-to-reverse changes** — it swaps the host's system VTK 9.5 for COPR 9.6
(relinking every VTK consumer) and removes `vtk-java`. Only appropriate on a
**dedicated build box**, never a workstation you rely on. See the header of
`farm-bootstrap.sh` for the full consent notice.

## Environment knobs (both paths)

| var | meaning | default |
|-----|---------|---------|
| `SLICER_CTEST_SUBMIT` | `0` = run tests without publishing to CDash | `1` |
| `SLICER_MODEL` | `Nightly` or `Experimental` | `Nightly` |
| `SLICER_CTEST_J` | build/test parallelism | `nproc-2` |
| `SLICER_COOLDOWN` | seconds between loop cycles | `600` |
