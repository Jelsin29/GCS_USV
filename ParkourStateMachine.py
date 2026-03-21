"""
ParkourStateMachine — Competition flow manager for 3-parkour sequence.

Manages state transitions: IDLE → PARKOUR_1 → PARKOUR_2 → PARKOUR_3 → COMPLETED
Handles auto-transition between parkours, competition timer, and UI lockout.
"""

from enum import Enum, auto

from PySide6.QtCore import QObject, QTimer, Signal


class ParkourState(Enum):
    """Competition parkour states."""

    IDLE = auto()
    PARKOUR_1 = auto()
    PARKOUR_2 = auto()
    PARKOUR_3 = auto()
    RETURNING = auto()
    COMPLETED = auto()


class ParkourStateMachine(QObject):
    """Manages the 3-parkour competition flow."""

    # State signals
    state_changed = Signal(ParkourState)
    parkour_completed = Signal(int)  # parkour number (1, 2, 3)

    # Timer signals
    timer_tick = Signal(int)  # remaining seconds
    timer_warning = Signal(str)  # warning message at 5min, 2min, 30sec
    timer_expired = Signal()

    # UI control signals
    lock_ui = Signal()  # disable command buttons
    unlock_ui = Signal()  # re-enable command buttons

    COMPETITION_TIME_SECONDS = 20 * 60  # 20 minutes

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = ParkourState.IDLE
        self._timer = QTimer(self)
        self._remaining_seconds = self.COMPETITION_TIME_SECONDS

    @property
    def state(self) -> ParkourState:
        """Current parkour state."""
        return self._state

    @property
    def remaining_time(self) -> int:
        """Remaining competition time in seconds."""
        return self._remaining_seconds

    def start_competition(self) -> None:
        """Start the competition timer and enter PARKOUR_1."""
        raise NotImplementedError

    def on_waypoint_reached(self, waypoint_seq: int, total_waypoints: int) -> None:
        """Called when USV reaches a mission waypoint."""
        raise NotImplementedError

    def on_parkour_complete(self, parkour_number: int) -> None:
        """Handle parkour completion and transition to next."""
        raise NotImplementedError

    def on_target_engaged(self) -> None:
        """Called when USV makes contact with target (Parkour 3)."""
        raise NotImplementedError

    def emergency_stop(self) -> None:
        """Emergency stop — unlock UI and halt state machine."""
        raise NotImplementedError

    def _start_timer(self) -> None:
        """Start the 20-minute countdown timer."""
        raise NotImplementedError

    def _on_timer_tick(self) -> None:
        """Called every second by the timer."""
        raise NotImplementedError
