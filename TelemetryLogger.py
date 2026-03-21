"""
TelemetryLogger — CSV telemetry data recorder for competition deliverables.

Logs: timestamp, lat, lon, speed, roll, pitch, heading, speed_setpoint, heading_setpoint
at minimum 1 Hz. Required by TEKNOFEST competition rules.
"""

import csv
from pathlib import Path

from PySide6.QtCore import QObject, Slot


class TelemetryLogger(QObject):
    """Records telemetry data to CSV file."""

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

    def __init__(self, output_dir: str = "logs", parent=None):
        super().__init__(parent)
        self._output_dir = Path(output_dir)
        self._file = None
        self._writer = None
        self._recording = False

    @property
    def is_recording(self) -> bool:
        """Return True if currently logging telemetry."""
        return self._recording

    def start(self) -> str:
        """Start recording. Returns the output file path."""
        raise NotImplementedError

    def stop(self) -> None:
        """Stop recording and close file."""
        raise NotImplementedError

    @Slot(dict)
    def log(self, telemetry_data: dict) -> None:
        """Log a single telemetry data point.

        Expected keys: lat, lon, groundspeed, roll, pitch, heading,
                       speed_setpoint, heading_setpoint
        """
        raise NotImplementedError

    def _flush(self) -> None:
        """Flush buffer to disk."""
        raise NotImplementedError
