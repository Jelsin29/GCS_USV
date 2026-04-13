"""
Tests: IndicatorsPage — initial zero state, mode flags, gauge-only instrument updates.
No USV telemetry widget; drone info does NOT appear on Indicators.
"""

import math


class TestIndicatorsPageInit:
    def test_indicators_page_exists(self, main_window):
        assert hasattr(main_window, "indicatorspage")

    def test_simulation_mode_off_by_default(self, main_window):
        assert main_window.indicatorspage.simulation_mode is False

    def test_allocate_button_exists(self, main_window):
        from PySide6.QtWidgets import QPushButton

        ip = main_window.indicatorspage
        assert hasattr(ip, "btn_AllocateWidget")
        assert isinstance(ip.btn_AllocateWidget, QPushButton)

    def test_is_attached_by_default(self, main_window):
        assert main_window.indicatorspage.isAttached is True

    def test_connection_thread_none_before_connect(self, main_window):
        assert main_window.indicatorspage.connection_thread is None

    def test_no_usv_telemetry_attribute(self, main_window):
        """Indicators no longer has a USV telemetry widget."""
        assert not hasattr(main_window.indicatorspage, "usv_telemetry")

    def test_no_telemetry_container_in_ui(self, main_window):
        """The telemetryContainer widget should no longer exist in the UI."""
        ip = main_window.indicatorspage
        assert not hasattr(ip, "telemetryContainer")


class TestIndicatorsPageSetters:
    def test_set_speed_does_not_raise(self, main_window):
        main_window.indicatorspage.setSpeed(0.0)
        main_window.indicatorspage.setSpeed(5.5)

    def test_set_heading_does_not_raise(self, main_window):
        main_window.indicatorspage.setHeading(0)
        main_window.indicatorspage.setHeading(180)
        main_window.indicatorspage.setHeading(359)

    def test_set_altitude_does_not_raise(self, main_window):
        main_window.indicatorspage.setAltitude(0.0)
        main_window.indicatorspage.setAltitude(10.0)

    def test_set_simulation_mode_true(self, main_window):
        ip = main_window.indicatorspage
        ip.setSimulationMode(True)
        assert ip.simulation_mode is True
        # Restore
        ip.setSimulationMode(False)

    def test_reset_for_ardupilot_does_not_raise(self, main_window):
        main_window.indicatorspage.resetForArduPilot()

    def test_update_from_ardupilot_data_does_not_raise(self, main_window):
        ip = main_window.indicatorspage
        sample = {
            "vfr_hud": {
                "groundspeed": 1.5,
                "heading": 270,
                "throttle": 50,
                "alt": 1.0,
                "climb": 0.0,
            },
        }
        ip.updateFromArduPilotData(sample)

    def test_update_from_ardupilot_no_usv_telemetry(self, main_window):
        """updateFromArduPilotData should NOT reference usv_telemetry."""
        ip = main_window.indicatorspage
        sample = {
            "vfr_hud": {"groundspeed": 2.0, "heading": 90, "throttle": 30},
            "global_position_int": {"lat": 413717139, "lon": 290295276, "alt": 500},
        }
        # Should succeed without usv_telemetry
        ip.updateFromArduPilotData(sample)
