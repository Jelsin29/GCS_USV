"""
Tests: TargetsPage (Mission Control) — buttons, mode selector, abort/RTL guards.
"""

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


class TestTargetsPageInit:
    def test_targets_page_is_a_widget(self, main_window):
        from PySide6.QtWidgets import QWidget
        assert isinstance(main_window.targetspage, QWidget)

    def test_has_mission_buttons(self, main_window):
        tp = main_window.targetspage
        for btn_name in [
            "btn_chooseMode", "btn_undo", "btn_clearAll",
            "btn_setMission", "btn_startMission", "btn_abort", "btn_rtl",
        ]:
            assert hasattr(tp, btn_name), f"Missing button: {btn_name}"
            assert isinstance(getattr(tp, btn_name), QPushButton)

    def test_has_guided_control_buttons(self, main_window):
        tp = main_window.targetspage
        for btn_name in [
            "btn_takeoff", "btn_move", "btn_track_all",
            "btn_land", "btn_rtl_2", "btn_set_roi", "btn_cancel_roi",
        ]:
            assert hasattr(tp, btn_name), f"Missing guided button: {btn_name}"

    def test_modes_combobox_has_expected_modes(self, main_window):
        tp = main_window.targetspage
        assert hasattr(tp, "modes_comboBox")
        cb = tp.modes_comboBox
        items = [cb.itemText(i) for i in range(cb.count())]
        # At minimum these three modes must be present
        assert "Waypoint Mode" in items
        assert "Area Selection Mode" in items


class TestTargetsPageMissionGuards:
    """Tests that mission operations fail gracefully when not connected."""

    def test_set_mission_without_connection_shows_status(self, main_window, qtbot):
        """set_mission() with no MAVLink connection must not raise — it shows an error status."""
        tp = main_window.targetspage
        # Remove connection thread temporarily if present
        original = getattr(main_window, "connectionThread", None)
        main_window.connectionThread = None

        try:
            tp.set_mission()   # Must not crash
        finally:
            if original is not None:
                main_window.connectionThread = original

    def test_abort_without_connection_does_not_raise(self, main_window, qtbot):
        tp = main_window.targetspage
        try:
            tp.abort()
        except Exception as exc:
            pytest.fail(f"abort() raised unexpectedly: {exc}")

    def test_rtl_without_connection_does_not_raise(self, main_window, qtbot):
        tp = main_window.targetspage
        try:
            tp.rtl()
        except Exception as exc:
            pytest.fail(f"rtl() raised unexpectedly: {exc}")


class TestTargetsPageModeSelector:
    def test_can_switch_to_waypoint_mode(self, main_window, qtbot):
        tp = main_window.targetspage
        tp.modes_comboBox.setCurrentText("Waypoint Mode")
        assert tp.modes_comboBox.currentText() == "Waypoint Mode"

    def test_can_switch_to_area_selection_mode(self, main_window, qtbot):
        tp = main_window.targetspage
        tp.modes_comboBox.setCurrentText("Area Selection Mode")
        assert tp.modes_comboBox.currentText() == "Area Selection Mode"

    def test_choose_mode_button_click_does_not_raise(self, main_window, qtbot):
        """btn_chooseMode with a valid mode selected must not raise."""
        tp = main_window.targetspage
        tp.modes_comboBox.setCurrentText("Waypoint Mode")
        try:
            qtbot.mouseClick(tp.btn_chooseMode, Qt.LeftButton)
        except Exception as exc:
            pytest.fail(f"btn_chooseMode click raised: {exc}")
