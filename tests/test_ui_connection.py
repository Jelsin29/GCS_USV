"""
Tests: Connection UI — combobox state, baudrate, connect button behaviour.
No real MAVLink connection is made.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox


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
        btn = main_window.btn_connect
        assert btn is not None
        assert btn.text() == "Connect Boat"
        assert "Connected" not in btn.text()

    def test_drone_connection_selector_exists_and_is_editable(self, main_window):
        selector = main_window.combobox_drone_port
        assert isinstance(selector, QComboBox)
        assert selector.parent() is main_window.frame_drone_connection
        assert selector.isEditable()
        items = [selector.itemText(i) for i in range(selector.count())]
        assert "udp:127.0.0.1:14550" in items
        assert "tcp:127.0.0.1:5760" in items

    def test_connect_to_drone_uses_header_selector_before_prompt(
        self, main_window, monkeypatch
    ):
        selected_port = "udp:127.0.0.1:14550"
        previous_text = main_window.combobox_drone_port.currentText()
        main_window.combobox_drone_port.setCurrentText(selected_port)

        captured = {}

        def fake_connect_drone(port, baudrate=57600):
            captured["port"] = port
            captured["baudrate"] = baudrate

        monkeypatch.setattr(
            main_window.connection_manager, "connect_drone", fake_connect_drone
        )

        def fail_prompt(*_args, **_kwargs):
            raise AssertionError("Prompt should not be used when selector has a value")

        monkeypatch.setattr("PySide6.QtWidgets.QInputDialog.getText", fail_prompt)

        main_window.connectToDrone()

        assert captured == {"port": selected_port, "baudrate": 57600}
        main_window.combobox_drone_port.setCurrentText(previous_text)
