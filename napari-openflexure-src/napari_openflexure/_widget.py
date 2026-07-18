"""napari dock widget to control an OpenFlexure microscope."""

from __future__ import annotations

import io

import numpy as np
import requests
from magicgui.widgets import (
    CheckBox,
    Container,
    FloatSpinBox,
    Label,
    LineEdit,
    PushButton,
    SpinBox,
)
from napari.qt.threading import thread_worker
from napari.viewer import Viewer
from PIL import Image

from openflexure_microscope_client import MicroscopeClient, find_first_microscope
from openflexure_microscope_client.microscope_client import is_a_task, poll_task

_LAYER_NAME = "openflexure"
_CSM_KEY = "org.openflexure.camera_stage_mapping"


class OpenFlexureWidget(Container):
    """Connect to an OpenFlexure microscope, capture images and jog the stage.

    napari injects the active viewer (via the napari_viewer parameter) when the
    widget is created from the Plugins menu.
    """

    def __init__(self, napari_viewer: "napari.viewer.Viewer") -> None:
        super().__init__()
        self._viewer = napari_viewer
        self._client: MicroscopeClient | None = None

        self._host = LineEdit(
            label="Host",
            tooltip="Microscope host/IP. Leave blank to auto-discover via mDNS.",
        )
        self._connect_btn = PushButton(text="Connect")
        self._status = Label(value="Not connected")
        self._full_res = CheckBox(
            label="Full resolution",
            value=True,
            tooltip=(
                "Capture the full sensor image (e.g. 3280x2464) via a gallery "
                "capture. Unchecked grabs the fast low-res preview stream."
            ),
        )
        self._capture_btn = PushButton(text="Capture image")
        self._step = SpinBox(label="Stage step", value=1000, min=1, max=100000)

        self._xm = PushButton(text="-X")
        self._xp = PushButton(text="+X")
        self._ym = PushButton(text="-Y")
        self._yp = PushButton(text="+Y")
        self._zm = PushButton(text="-Z (focus down)")
        self._zp = PushButton(text="+Z (focus up)")

        # -- mosaic / whole-slide scan --
        self._scan_label = Label(value="— Mosaic scan —")
        self._grid = SpinBox(
            label="Grid (NxN)", value=3, min=1, max=60,
            tooltip="Number of tiles per side of the square raster.",
        )
        self._overlap = FloatSpinBox(
            label="Overlap", value=0.2, min=0.0, max=0.8, step=0.05,
            tooltip="Fractional overlap between adjacent tiles.",
        )
        self._scan_autofocus = CheckBox(
            label="Autofocus first", value=True,
            tooltip="Run fast autofocus at the start position before scanning.",
        )
        self._overview = CheckBox(
            label="Overview (fast, low-res)", value=False,
            tooltip=(
                "Paint fast preview-stream tiles into a single 'slide_overview' "
                "layer instead of one full-res layer per tile. Use a large grid "
                "to map the whole slide cheaply, then full-res the interesting "
                "sections."
            ),
        )
        self._scan_btn = PushButton(text="Scan slide (mosaic)")

        self._connect_btn.clicked.connect(self._connect)
        self._capture_btn.clicked.connect(self._capture)
        self._xm.clicked.connect(lambda: self._move(-1, 0, 0))
        self._xp.clicked.connect(lambda: self._move(1, 0, 0))
        self._ym.clicked.connect(lambda: self._move(0, -1, 0))
        self._yp.clicked.connect(lambda: self._move(0, 1, 0))
        self._zm.clicked.connect(lambda: self._move(0, 0, -1))
        self._zp.clicked.connect(lambda: self._move(0, 0, 1))
        self._scan_btn.clicked.connect(self._scan)

        self.extend(
            [
                self._host,
                self._connect_btn,
                self._status,
                self._full_res,
                self._capture_btn,
                self._step,
                self._xm,
                self._xp,
                self._ym,
                self._yp,
                self._zm,
                self._zp,
                self._scan_label,
                self._grid,
                self._overlap,
                self._scan_autofocus,
                self._overview,
                self._scan_btn,
            ]
        )

    # -- actions ------------------------------------------------------------
    def _connect(self) -> None:
        host = self._host.value.strip()
        try:
            self._client = MicroscopeClient(host) if host else find_first_microscope()
            self._status.value = f"Connected: {self._client.host}"
        except Exception as exc:  # noqa: BLE001 - surface any failure in the GUI
            self._client = None
            self._status.value = f"Connect failed: {exc}"

    def _capture(self) -> None:
        if self._client is None:
            self._status.value = "Not connected"
            return
        try:
            if self._full_res.value:
                image = self._capture_full_res()
                tag = "full-res"
            else:
                image = np.asarray(self._client.capture_image())
                tag = "stream"
            if _LAYER_NAME in self._viewer.layers:
                self._viewer.layers[_LAYER_NAME].data = image
            else:
                self._viewer.add_image(image, name=_LAYER_NAME)
            self._status.value = f"Captured {tag} {image.shape[1]}x{image.shape[0]}"
        except Exception as exc:  # noqa: BLE001
            self._status.value = f"Capture failed: {exc}"

    def _capture_full_res(self) -> np.ndarray:
        """Capture a full-sensor image (not the preview stream) as an array.

        ``capture_image`` can only return the low-res preview stream. For the
        real sensor resolution we trigger a gallery capture, download its
        bytes, then delete it (we mark it temporary) so the microscope's
        gallery is not left cluttered.
        """
        cap = self._client.capture_image_to_disk(
            {"temporary": True, "use_video_port": False, "bayer": False}
        )
        cid = cap.get("id") if isinstance(cap, dict) else None
        if not cid:
            raise RuntimeError(f"capture returned no id: {cap!r}")
        try:
            url = f"{self._client.base_uri}/captures/{cid}/download/download.jpg"
            resp = requests.get(url, timeout=30)
            resp.raise_for_status()
            return np.asarray(Image.open(io.BytesIO(resp.content)))
        finally:
            try:
                self._client.delete_image(cid)
            except Exception:  # noqa: BLE001 - cleanup is best-effort
                pass

    def _move(self, dx: int, dy: int, dz: int) -> None:
        if self._client is None:
            self._status.value = "Not connected"
            return
        step = int(self._step.value)
        delta = {"x": dx * step, "y": dy * step, "z": dz * step}
        try:
            self._client.move_rel(delta)
            self._status.value = f"Moved {delta}"
        except Exception as exc:  # noqa: BLE001
            self._status.value = f"Move failed: {exc}"

    # -- mosaic scan --------------------------------------------------------
    def _autofocus(self) -> None:
        """Run the server's fast autofocus at the current position."""
        url = (
            f"{self._client.base_uri}"
            "/extensions/org.openflexure.autofocus/fast_autofocus"
        )
        resp = requests.post(url, json={"dz": 2000}, timeout=60)
        resp.raise_for_status()
        task = resp.json()
        if is_a_task(task):
            poll_task(task)

    def _scan(self) -> None:
        """Raster a square grid of tiles over the slide.

        Two modes (worker thread, tiles handed to the GUI thread as captured):

        * full-res (default): one full-resolution image layer per tile,
          translated to its grid position -> a zoomable mosaic.
        * overview: fast preview-stream tiles painted into a single
          ``slide_overview`` layer -> a cheap whole-slide map for a large grid.
        """
        if self._client is None:
            self._status.value = "Not connected"
            return
        self._scan_btn.enabled = False
        self._ov_canvas = None
        if self._overview.value:
            settings = self._client.pull_settings()
            sw, sh = settings["camera"]["stream_resolution"]
            n = int(self._grid.value)
            keep = 1.0 - float(self._overlap.value)
            pc, pr = int(round(sw * keep)), int(round(sh * keep))
            self._ov_canvas = np.zeros(
                ((n - 1) * pr + sh, (n - 1) * pc + sw, 3), np.uint8
            )
            if "slide_overview" in self._viewer.layers:
                del self._viewer.layers["slide_overview"]
            self._viewer.add_image(self._ov_canvas, name="slide_overview")
        worker = self._run_scan()
        worker.yielded.connect(self._place_tile)
        worker.errored.connect(self._on_scan_error)
        worker.finished.connect(lambda: setattr(self._scan_btn, "enabled", True))
        worker.start()

    def _on_scan_error(self, exc: Exception) -> None:
        self._status.value = f"Scan failed: {exc}"

    @thread_worker
    def _run_scan(self):
        """Worker: move the stage over an NxN grid yielding (tile, (y,x), name).

        The camera_stage_mapping ``image_to_stage_displacement`` matrix turns a
        pixel step into the stage move that produces it, so stepping the stage
        by one (overlapped) field of view lands tiles on a regular pixel grid.
        """
        settings = self._client.pull_settings()
        disp = settings["extensions"][_CSM_KEY]["image_to_stage_displacement"]
        mat = np.asarray(disp, dtype=float)  # stream-px -> stage-steps
        stream_w, stream_h = settings["camera"]["stream_resolution"]
        full_w, full_h = settings["camera"]["image_resolution"]

        n = int(self._grid.value)
        overlap = float(self._overlap.value)
        half = n // 2
        keep = 1.0 - overlap
        overview = bool(self._overview.value)
        # stage move for one (overlapped) tile along image x / y
        col_vec = mat @ np.array([stream_w * keep, 0.0])
        row_vec = mat @ np.array([0.0, stream_h * keep])
        # placement pitch: stream px for the overview canvas, full px otherwise
        if overview:
            pitch_c, pitch_r = int(round(stream_w * keep)), int(round(stream_h * keep))
        else:
            pitch_c, pitch_r = full_w * keep, full_h * keep

        if self._scan_autofocus.value:
            self._autofocus()
        home = self._client.get_position_array().astype(float)

        try:
            for ri in range(n):
                cols = range(n) if ri % 2 == 0 else range(n - 1, -1, -1)  # snake
                for ci in cols:
                    r_off, c_off = ri - half, ci - half
                    target = home.copy()
                    target[0] += r_off * row_vec[0] + c_off * col_vec[0]
                    target[1] += r_off * row_vec[1] + c_off * col_vec[1]
                    self._client.move(
                        {"x": int(target[0]), "y": int(target[1]),
                         "z": int(home[2])},
                        absolute=True,
                    )
                    if overview:
                        tile = np.asarray(self._client.capture_image())
                        tile = tile[:stream_h, :stream_w, :3]
                    else:
                        tile = self._capture_full_res()
                    yield {
                        "overview": overview,
                        "y": int(ri * pitch_r),
                        "x": int(ci * pitch_c),
                        "tile": tile,
                        "name": f"tile_{ri}_{ci}",
                    }
        finally:
            # always return to where we started
            self._client.move(
                {"x": int(home[0]), "y": int(home[1]), "z": int(home[2])},
                absolute=True,
            )

    def _place_tile(self, payload) -> None:
        y, x, tile = payload["y"], payload["x"], payload["tile"]
        if payload["overview"]:
            th, tw = tile.shape[:2]
            self._ov_canvas[y:y + th, x:x + tw] = tile
            self._viewer.layers["slide_overview"].data = self._ov_canvas
            self._status.value = f"Overview tile @ ({y},{x})"
        else:
            name = payload["name"]
            if name in self._viewer.layers:
                self._viewer.layers[name].data = tile
            else:
                self._viewer.add_image(tile, name=name, translate=(y, x))
            self._status.value = f"Placed {name}"
