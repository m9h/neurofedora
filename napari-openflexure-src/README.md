# napari-openflexure

A [napari](https://napari.org) plugin to control an
[OpenFlexure microscope](https://openflexure.org) from within the viewer.

It adds an **OpenFlexure control** dock widget (Plugins → OpenFlexure) that can:

- connect to a microscope by host/IP, or auto-discover one on the network
  (zeroconf/mDNS);
- capture an image straight into a napari image layer, at full sensor
  resolution or from the fast low-res preview stream;
- jog the stage in X, Y and Z (focus) by a configurable step;
- raster a whole-slide **mosaic scan** over an NxN grid of overlapping tiles.

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

### Mosaic scanning

**Scan slide (mosaic)** rasters a square grid over the slide. Tile placement
uses the microscope's `camera_stage_mapping` calibration, so the stage move for
one (overlapped) field of view is known and tiles land on a regular pixel grid.

- **Full resolution** (default) adds one image layer per tile, translated into
  position — a zoomable mosaic at sensor resolution.
- **Overview** paints fast preview-stream tiles into a single `slide_overview`
  layer instead. Use a large grid to map the whole slide cheaply, then rescan
  the interesting regions at full resolution.

Scanning runs on a worker thread and the stage always returns to its starting
position when the scan ends.
