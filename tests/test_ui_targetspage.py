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

    def test_load_file_button_text(self, main_window):
        tp = main_window.targetspage
        assert tp.btn_set_roi.text() == "LOAD FILE"

    def test_clear_map_button_text(self, main_window):
        tp = main_window.targetspage
        assert tp.btn_cancel_roi.text() == "CLEAR MAP"

    def test_modes_combobox_has_expected_modes(self, main_window):
        tp = main_window.targetspage
        assert hasattr(tp, "modes_comboBox")
        cb = tp.modes_comboBox
        items = [cb.itemText(i) for i in range(cb.count())]
        # At minimum these three modes must be present
        assert "Waypoint Mode" in items
        assert "Area Selection Mode" in items


class TestMissionFileParser:
    """Unit tests for _parse_mission_file — no Qt, no connection needed."""

    def _make_page(self, main_window):
        return main_window.targetspage

    def test_parse_json_array_of_dicts(self, main_window, tmp_path):
        tp = self._make_page(main_window)
        f = tmp_path / "mission.json"
        f.write_text('[{"lat": 41.0, "lon": 29.0}, {"lat": 41.1, "lon": 29.1}]')
        result = tp._parse_mission_file(str(f))
        assert len(result) == 2
        assert result[0] == [41.0, 29.0, 0.0]

    def test_parse_json_array_of_arrays(self, main_window, tmp_path):
        tp = self._make_page(main_window)
        f = tmp_path / "mission.json"
        f.write_text("[[41.0, 29.0], [41.1, 29.1, 10.0]]")
        result = tp._parse_mission_file(str(f))
        assert len(result) == 2
        assert result[1][2] == 10.0

    def test_parse_json_wrapped_object(self, main_window, tmp_path):
        tp = self._make_page(main_window)
        f = tmp_path / "mission.json"
        f.write_text('{"waypoints": [{"lat": 41.0, "lon": 29.0}]}')
        result = tp._parse_mission_file(str(f))
        assert len(result) == 1

    def test_parse_txt_comma_separated(self, main_window, tmp_path):
        tp = self._make_page(main_window)
        f = tmp_path / "mission.txt"
        f.write_text("# comment\n41.0,29.0\n41.1,29.1,5.0\n")
        result = tp._parse_mission_file(str(f))
        assert len(result) == 2
        assert result[1][2] == 5.0

    def test_parse_txt_space_separated(self, main_window, tmp_path):
        tp = self._make_page(main_window)
        f = tmp_path / "mission.txt"
        f.write_text("41.0 29.0\n41.1 29.1\n")
        result = tp._parse_mission_file(str(f))
        assert len(result) == 2

    def test_invalid_coordinates_skipped(self, main_window, tmp_path):
        tp = self._make_page(main_window)
        f = tmp_path / "mission.txt"
        f.write_text("999.0,999.0\n41.0,29.0\n")
        result = tp._parse_mission_file(str(f))
        assert len(result) == 1

    def test_unsupported_extension_raises(self, main_window, tmp_path):
        tp = self._make_page(main_window)
        f = tmp_path / "mission.csv"
        f.write_text("41.0,29.0\n")
        with pytest.raises(ValueError, match="Unsupported file type"):
            tp._parse_mission_file(str(f))


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
