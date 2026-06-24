"""napari dock widget to control an OpenFlexure microscope."""

from __future__ import annotations

import numpy as np
from magicgui.widgets import Container, Label, LineEdit, PushButton, SpinBox

from openflexure_microscope_client import MicroscopeClient, find_first_microscope

_LAYER_NAME = "openflexure"


class OpenFlexureWidget(Container):
    """Connect to an OpenFlexure microscope, capture images and jog the stage.

    napari injects the active viewer (by type annotation) when the widget is
    created from the Plugins menu.
    """

    def __init__(self, viewer) -> None:
        super().__init__()
        self._viewer = viewer
        self._client: MicroscopeClient | None = None

        self._host = LineEdit(
            label="Host",
            tooltip="Microscope host/IP. Leave blank to auto-discover via mDNS.",
        )
        self._connect_btn = PushButton(text="Connect")
        self._status = Label(value="Not connected")
        self._capture_btn = PushButton(text="Capture image")
        self._step = SpinBox(label="Stage step", value=1000, min=1, max=100000)

        self._xm = PushButton(text="-X")
        self._xp = PushButton(text="+X")
        self._ym = PushButton(text="-Y")
        self._yp = PushButton(text="+Y")
        self._zm = PushButton(text="-Z (focus down)")
        self._zp = PushButton(text="+Z (focus up)")

        self._connect_btn.clicked.connect(self._connect)
        self._capture_btn.clicked.connect(self._capture)
        self._xm.clicked.connect(lambda: self._move(-1, 0, 0))
        self._xp.clicked.connect(lambda: self._move(1, 0, 0))
        self._ym.clicked.connect(lambda: self._move(0, -1, 0))
        self._yp.clicked.connect(lambda: self._move(0, 1, 0))
        self._zm.clicked.connect(lambda: self._move(0, 0, -1))
        self._zp.clicked.connect(lambda: self._move(0, 0, 1))

        self.extend(
            [
                self._host,
                self._connect_btn,
                self._status,
                self._capture_btn,
                self._step,
                self._xm,
                self._xp,
                self._ym,
                self._yp,
                self._zm,
                self._zp,
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
            image = np.asarray(self._client.capture_image())
            if _LAYER_NAME in self._viewer.layers:
                self._viewer.layers[_LAYER_NAME].data = image
            else:
                self._viewer.add_image(image, name=_LAYER_NAME)
            self._status.value = f"Captured {image.shape[1]}x{image.shape[0]}"
        except Exception as exc:  # noqa: BLE001
            self._status.value = f"Capture failed: {exc}"

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
