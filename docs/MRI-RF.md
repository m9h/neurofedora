# MRI RF simulation and inverse imaging

The companion project [mri-rf-stack](https://github.com/m9h/mri-rf-stack) provides
an executable Hertzon birdcage/phantom benchmark, complex field post-processing,
power-normalized B1 and local SAR, ParaView output, JEMRIS coil-map export, and
noise-whitened minimum-norm inverse-imaging tools inspired by Fa-Hsuan Lin's InI.

`python-mri-rf-stack.spec` packages the analysis library and `mri-rf` CLI. It has
NumPy, SciPy and HDF5 dependencies, and runs its numerical tests during the RPM
build. The source archive is the public companion project's v0.1.0 tag.

## Existing stack connections

- Slicer, ITK, ANTs, SAMSEG/CHARM and FreeSurfer can prepare anatomical labels.
- SimNIBS can contribute head-model preparation; its quasi-static solver is not
  the full-wave RF engine.
- ParaView/VTK/PyVista can inspect the exported tetrahedral fields.
- JEMRIS can consume the exported relative complex coil maps. Full sequence
  interoperability is a subsequent validation task.
- BART can support reconstruction once simulated acquisitions are formatted.

## Solver dependency boundary

The optional solver is pinned to Hertzon 0.1.25 and EMerge 3.0.0a25. Hertzon
requires Python >=3.10,<3.14, so it is not currently declared as a dependency of
this system-Python analysis RPM. Do not remove that upper bound merely to make
dependency resolution succeed. Native EMerge kernel builds, interpreter support,
and the complete solver dependency chain require a separate packaging audit.

The tested solver environment uses Python 3.12 and is installed following the
companion README. This PR does not claim to deliver Hertzon/openEMS RPMs or to
submit a COPR build. The companion GitHub Actions workflow builds and installs
the analysis RPM in Fedora 44 and publishes build artifacts.

## Evidence and limits

The local reference solve met Hertzon's ΔS threshold after seven adaptive passes
and 16,189 tetrahedra. Numerical tests check RF power/phase conventions, SAR
integration, inverse reconstruction, and JEMRIS sample layout. Full evidence:
[validation record](https://github.com/m9h/mri-rf-stack/blob/main/docs/validation.md).

The current model is a synthetic homogeneous phantom with a single-feed unmatched
birdcage. It is not an anatomical 32-channel head-coil simulation. Independent
openEMS comparison, field/SAR convergence, mass-averaged SAR and phantom
measurements remain validation work. The separate 32-channel inverse example
uses synthetic sensitivities and makes no claim to reproduce published InI
spatial or temporal performance.
