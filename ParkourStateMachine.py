"""
ParkourStateMachine — Competition flow manager for 3-parkour sequence.

Manages state transitions: IDLE → PARKOUR_1 → PARKOUR_2 → PARKOUR_3 → COMPLETED
Handles competition timer (20 min) and UI lockout during autonomous phases.

Per competition rules:
- Parkur-1: Waypoint following (no obstacles), 4 waypoints
- Parkur-2: Obstacle avoidance, reach final waypoint
- Parkur-3: Kamikaze engagement, contact target buoy
- Transitions between parkours are automatic (no user input)
- No commands allowed after mission start (except emergency kill)
- Total time: 20 minutes
"""

from enum import Enum, auto

from PySide6.QtCore import QObject, QTimer, Signal


class ParkourState(Enum):
    """Competition parkour states."""

    IDLE = auto()
    PARKOUR_1 = auto()
    TRANSITION_1_2 = auto()
    PARKOUR_2 = auto()
    TRANSITION_2_3 = auto()
    PARKOUR_3 = auto()
    RETURNING = auto()
    COMPLETED = auto()


class ParkourStateMachine(QObject):
    """Manages the 3-parkour competition flow."""

    # State signals
    state_changed = Signal(object)  # ParkourState
    parkour_completed = Signal(int)  # parkour number (1, 2, 3)

    # Timer signals
    timer_tick = Signal(int)  # remaining seconds
    timer_warning = Signal(str)  # warning message
    timer_expired = Signal()

    # UI control signals
    lock_ui = Signal()  # disable command buttons
    unlock_ui = Signal()  # re-enable command buttons

    # Mission signals (requests to TargetsPage/MainWindow)
    request_mission_upload = Signal(int)  # parkour number to upload
    request_mission_start = Signal()

    COMPETITION_TIME_SECONDS = 20 * 60  # 20 minutes
    WARNING_THRESHOLDS = [300, 120, 30]  # 5min, 2min, 30sec

    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = ParkourState.IDLE
        self._timer = QTimer(self)
        self._timer.setInterval(1000)  # 1 second ticks
        self._timer.timeout.connect(self._on_timer_tick)
        self._remaining_seconds = self.COMPETITION_TIME_SECONDS
        self._warnings_emitted: set[int] = set()

    @property
    def state(self) -> ParkourState:
        """Current parkour state."""
        return self._state

    @property
    def remaining_time(self) -> int:
        """Remaining competition time in seconds."""
        return self._remaining_seconds

    @property
    def remaining_time_str(self) -> str:
        """Remaining time as MM:SS string."""
        minutes = self._remaining_seconds // 60
        seconds = self._remaining_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def is_running(self) -> bool:
        """Return True if competition is active."""
        return self._state not in (ParkourState.IDLE, ParkourState.COMPLETED)

    def _set_state(self, new_state: ParkourState) -> None:
        """Change state and emit signal."""
        old_state = self._state
        self._state = new_state
        print(f"[PARKOUR] State: {old_state.name} → {new_state.name}")
        self.state_changed.emit(new_state)

    def start_competition(self) -> None:
        """Start the competition timer and enter PARKOUR_1."""
        if self._state != ParkourState.IDLE:
            print("[PARKOUR] Competition already started")
            return

        print("[PARKOUR] Competition started — 20 minute countdown begins")
        self._remaining_seconds = self.COMPETITION_TIME_SECONDS
        self._warnings_emitted.clear()
        self._timer.start()
        self._set_state(ParkourState.PARKOUR_1)
        self.lock_ui.emit()

    def on_mission_complete(self) -> None:
        """Called when the current mission is completed (all waypoints reached).

        This should be triggered by MISSION_ITEM_REACHED for the last waypoint
        or by detecting AUTO → HOLD mode transition after mission completion.
        """
        if self._state == ParkourState.PARKOUR_1:
            self.parkour_completed.emit(1)
            self._set_state(ParkourState.TRANSITION_1_2)
            print("[PARKOUR] Parkur-1 complete — transitioning to Parkur-2")
            # Request Parkur-2 mission upload
            self.request_mission_upload.emit(2)

        elif self._state == ParkourState.PARKOUR_2:
            self.parkour_completed.emit(2)
            self._set_state(ParkourState.TRANSITION_2_3)
            print("[PARKOUR] Parkur-2 complete — transitioning to Parkur-3")
            # Request Parkur-3 mission upload
            self.request_mission_upload.emit(3)

        elif self._state == ParkourState.PARKOUR_3:
            self.parkour_completed.emit(3)
            self._set_state(ParkourState.RETURNING)
            print("[PARKOUR] Parkur-3 complete — returning to start")

    def on_mission_uploaded(self, parkour_number: int) -> None:
        """Called when mission for next parkour is uploaded and ready."""
        if parkour_number == 2 and self._state == ParkourState.TRANSITION_1_2:
            self._set_state(ParkourState.PARKOUR_2)
            self.request_mission_start.emit()

        elif parkour_number == 3 and self._state == ParkourState.TRANSITION_2_3:
            self._set_state(ParkourState.PARKOUR_3)
            self.request_mission_start.emit()

    def on_target_engaged(self) -> None:
        """Called when USV makes contact with target (Parkour 3)."""
        if self._state == ParkourState.PARKOUR_3:
            self.on_mission_complete()

    def on_return_complete(self) -> None:
        """Called when USV returns to starting point."""
        if self._state == ParkourState.RETURNING:
            self._set_state(ParkourState.COMPLETED)
            self._timer.stop()
            self.unlock_ui.emit()
            print(
                f"[PARKOUR] Competition COMPLETED — "
                f"time remaining: {self.remaining_time_str}"
            )

    def emergency_stop(self) -> None:
        """Emergency stop — unlock UI and halt state machine."""
        self._timer.stop()
        self._set_state(ParkourState.IDLE)
        self.unlock_ui.emit()
        print("[PARKOUR] EMERGENCY STOP — state machine halted")

    def reset(self) -> None:
        """Reset state machine to IDLE for restart."""
        self._timer.stop()
        self._state = ParkourState.IDLE
        self._remaining_seconds = self.COMPETITION_TIME_SECONDS
        self._warnings_emitted.clear()
        self.unlock_ui.emit()
        self.state_changed.emit(ParkourState.IDLE)

    def _on_timer_tick(self) -> None:
        """Called every second by the timer."""
        self._remaining_seconds -= 1
        self.timer_tick.emit(self._remaining_seconds)

        # Check warning thresholds
        for threshold in self.WARNING_THRESHOLDS:
            if (
                self._remaining_seconds == threshold
                and threshold not in self._warnings_emitted
            ):
                self._warnings_emitted.add(threshold)
                minutes = threshold // 60
                seconds = threshold % 60
                if minutes > 0:
                    msg = f"WARNING: {minutes} minute{'s' if minutes > 1 else ''} remaining!"
                else:
                    msg = f"WARNING: {seconds} seconds remaining!"
                print(f"[PARKOUR] {msg}")
                self.timer_warning.emit(msg)

        # Timer expired
        if self._remaining_seconds <= 0:
            self._timer.stop()
            self.timer_expired.emit()
            print("[PARKOUR] TIME EXPIRED — competition over")
            # Per rules: score whatever was completed at this point
            if self._state not in (ParkourState.COMPLETED, ParkourState.IDLE):
                self._set_state(ParkourState.COMPLETED)
                self.unlock_ui.emit()
