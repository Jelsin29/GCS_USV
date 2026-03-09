"""
Tests: Connection UI — combobox state, baudrate, connect button behaviour.
No real MAVLink connection is made.
"""

from PySide6.QtCore import Qt


class TestConnectionUI:
    SITL_OPTIONS = ["SITL (UDP)", "SITL (TCP)", "MAVROS Direct", "UDP", "TCP"]

    def test_connection_string_combobox_contains_all_network_options(self, main_window):
        cb = main_window.combobox_connectionstring
        items = [cb.itemText(i) for i in range(cb.count())]
        for opt in self.SITL_OPTIONS:
            assert opt in items, f"Expected '{opt}' in connection combobox"

    def test_can_select_sitl_tcp(self, main_window, qtbot):
        cb = main_window.combobox_connectionstring
        cb.setCurrentText("SITL (TCP)")
        assert cb.currentText() == "SITL (TCP)"

    def test_can_select_sitl_udp(self, main_window, qtbot):
        cb = main_window.combobox_connectionstring
        cb.setCurrentText("SITL (UDP)")
        assert cb.currentText() == "SITL (UDP)"

    def test_baudrate_combobox_has_common_rates(self, main_window):
        cb = main_window.combobox_baudrate
        items = [cb.itemText(i) for i in range(cb.count())]
        for rate in ["9600", "57600", "115200"]:
            assert rate in items, f"Expected baud rate '{rate}' in combobox"

    def test_baudrate_default_is_115200(self, main_window):
        assert main_window.combobox_baudrate.currentText() == "115200"

    def test_connect_button_is_enabled_before_connection(self, main_window):
        assert main_window.btn_connect.isEnabled()

    def test_connect_button_has_connect_text_or_icon(self, main_window):
        # Button text may be empty (icon only) but the button must exist
        btn = main_window.btn_connect
        assert btn is not None
        # Should not say "Connected" before any connection attempt
        assert "Connected" not in btn.text()
