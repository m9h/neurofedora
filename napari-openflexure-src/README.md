# napari-openflexure

A [napari](https://napari.org) plugin to control an
[OpenFlexure microscope](https://openflexure.org) from within the viewer.

It adds an **OpenFlexure control** dock widget (Plugins → OpenFlexure) that can:

- connect to a microscope by host/IP, or auto-discover one on the network
  (zeroconf/mDNS);
- capture a full-resolution image straight into a napari image layer;
- jog the stage in X, Y and Z (focus) by a configurable step.

It is a thin wrapper around
[`openflexure-microscope-client`](https://gitlab.com/openflexure/openflexure-microscope-pyclient),
which speaks the microscope's LabThings / Web-of-Things HTTP API.

## Usage

```python
import napari
viewer = napari.Viewer()
# Plugins -> OpenFlexure -> OpenFlexure control
napari.run()
```

Enter the microscope host (e.g. `microscope.local`) or leave it blank to
auto-discover, click **Connect**, then **Capture image**.
