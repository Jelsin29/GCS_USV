"""
TelemetryLogger — CSV telemetry data recorder for competition deliverables.

Logs: timestamp, lat, lon, speed, roll, pitch, heading, speed_setpoint, heading_setpoint
at minimum 1 Hz. Required by TEKNOFEST 2026 competition rules (File 2: Araç telemetri verisi).

The telemetry_data dict comes from ArdupilotConnectionThread.process_telemetry()
and contains nested dicts: global_position_int, vfr_hud, attitude, heartbeat, etc.
"""

import csv
import math
import time
import typing
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, Signal, Slot


class TelemetryLogger(QObject):
    """Records telemetry data to CSV file."""

    recording_started = Signal(str)  # file path
    recording_stopped = Signal(str)  # file path

    HEADER = [
        "timestamp",
        "lat",
        "lon",
        "speed",
        "roll",
        "pitch",
        "heading",
        "speed_setpoint",
        "heading_setpoint",
    ]

    FLUSH_INTERVAL_S = 1.0  # Flush every second to minimize data loss on crash

    def __init__(self, output_dir: str = "logs", parent=None):
        super().__init__(parent)
        self._output_dir = Path(output_dir)
        self._file: typing.IO[str] | None = None
        self._writer: typing.Any = None
        self._recording = False
        self._file_path: str = ""
        self._last_flush: float = 0
        self._row_count: int = 0

        # Accumulator — telemetry arrives as partial updates (one msg type at a time)
        self._current: dict[str, float] = {
            "lat": 0.0,
            "lon": 0.0,
            "speed": 0.0,
            "roll": 0.0,
            "pitch": 0.0,
            "heading": 0.0,
            "speed_setpoint": 0.0,
            "heading_setpoint": 0.0,
        }

    @property
    def is_recording(self) -> bool:
        """Return True if currently logging telemetry."""
        return self._recording

    @property
    def file_path(self) -> str:
        """Return the current/last recording file path."""
        return self._file_path

    @property
    def row_count(self) -> int:
        """Return number of rows written so far."""
        return self._row_count

    def start(self) -> str:
        """Start recording. Returns the output file path."""
        if self._recording:
            return self._file_path

        self._output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._file_path = str(self._output_dir / f"telemetry_{timestamp}.csv")

        self._file = open(self._file_path, "w", newline="")  # noqa: SIM115
        self._writer = csv.writer(self._file)
        self._writer.writerow(self.HEADER)
        self._recording = True
        self._last_flush = time.time()
        self._row_count = 0

        print(f"[LOGGER] Recording started: {self._file_path}")
        self.recording_started.emit(self._file_path)
        return self._file_path

    def stop(self) -> None:
        """Stop recording and close file."""
        if not self._recording:
            return

        self._recording = False
        if self._file:
            self._file.flush()
            self._file.close()
            self._file = None
        self._writer = None

        print(
            f"[LOGGER] Recording stopped: {self._row_count} rows written to {self._file_path}"
        )
        self.recording_stopped.emit(self._file_path)

    @Slot(dict)
    def log(self, telemetry_data: dict) -> None:
        """Log telemetry data from ArdupilotConnectionThread.

        The telemetry_data dict has nested keys like:
        - global_position_int: {lat, lon, hdg, alt}
        - vfr_hud: {groundspeed, heading, throttle, alt, climb}
        - attitude: {roll, pitch, yaw, ...}
        - heartbeat: {type, base_mode, custom_mode, ...}

        Values arrive incrementally (each message updates one section),
        so we accumulate into self._current and write a full row
        whenever we get a GPS update (the primary 1Hz source).
        """
        if not self._recording or self._writer is None:
            return

        wrote_row = False

        # Extract values from nested telemetry dict
        if "global_position_int" in telemetry_data:
            gps = telemetry_data["global_position_int"]
            self._current["lat"] = gps["lat"] / 1e7
            self._current["lon"] = gps["lon"] / 1e7
            self._current["heading"] = gps["hdg"] / 100.0
            # GPS update triggers a row write (this is our 1Hz clock)
            wrote_row = True

        if "vfr_hud" in telemetry_data:
            hud = telemetry_data["vfr_hud"]
            self._current["speed"] = hud["groundspeed"]

        if "attitude" in telemetry_data:
            att = telemetry_data["attitude"]
            self._current["roll"] = math.degrees(att["roll"])
            self._current["pitch"] = math.degrees(att["pitch"])

        if wrote_row:
            self._writer.writerow(
                [
                    f"{time.time():.3f}",
                    f"{self._current['lat']:.7f}",
                    f"{self._current['lon']:.7f}",
                    f"{self._current['speed']:.2f}",
                    f"{self._current['roll']:.2f}",
                    f"{self._current['pitch']:.2f}",
                    f"{self._current['heading']:.2f}",
                    f"{self._current['speed_setpoint']:.2f}",
                    f"{self._current['heading_setpoint']:.2f}",
                ]
            )
            self._row_count += 1

            # Periodic flush
            now = time.time()
            if now - self._last_flush >= self.FLUSH_INTERVAL_S:
                self._flush()
                self._last_flush = now

    def _flush(self) -> None:
        """Flush buffer to disk."""
        if self._file:
            self._file.flush()
