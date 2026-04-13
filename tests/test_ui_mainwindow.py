"""
Tests: MainWindow initial state
Verifies the window opens with correct widgets and default values.
"""

from PySide6.QtWidgets import QStackedWidget, QPushButton


class TestMainWindowInit:
    def test_window_is_visible(self, main_window):
        assert main_window.isVisible()

    def test_has_stacked_widget(self, main_window):
        assert hasattr(main_window, "stackedWidget")
        assert isinstance(main_window.stackedWidget, QStackedWidget)

    def test_stacked_widget_has_three_pages(self, main_window):
        # homepage, targetspage, indicatorswidget
        assert main_window.stackedWidget.count() == 3

    def test_home_page_is_initial_page(self, main_window):
        assert main_window.stackedWidget.currentWidget() is main_window.homepage

    def test_connection_combobox_has_sitl_options(self, main_window):
        cb = main_window.combobox_connectionstring
        items = [cb.itemText(i) for i in range(cb.count())]
        assert "SITL (UDP)" in items
        assert "SITL (TCP)" in items

    def test_baudrate_defaults_to_115200(self, main_window):
        assert main_window.combobox_baudrate.currentText() == "115200"

    def test_connect_button_exists_and_enabled(self, main_window):
        btn = main_window.btn_connect
        assert isinstance(btn, QPushButton)
        assert btn.isEnabled()

    def test_header_has_separate_usv_and_drone_sections(self, main_window):
        assert main_window.label_usv_connection.text() == "Boat / USV"
        assert main_window.label_drone_connection.text() == "Drone"
        assert (
            main_window.combobox_connectionstring.parent()
            is main_window.frame_usv_connection
        )
        assert main_window.btn_connect.parent() is main_window.frame_usv_connection
        assert (
            main_window.combobox_drone_port.parent()
            is main_window.frame_drone_connection
        )
        assert (
            main_window.btn_connect_drone.parent() is main_window.frame_drone_connection
        )
        assert main_window.btn_connect.text() == "Connect Boat"
        assert main_window.btn_connect_drone.text() == "Connect Drone"

    def test_nav_buttons_exist(self, main_window):
        assert hasattr(main_window, "btn_home_page")
        assert hasattr(main_window, "btn_indicators_page")
        assert hasattr(main_window, "btn_targets_page")

    def test_home_button_disabled_on_startup(self, main_window):
        # btn_home_page starts disabled (we're already on home)
        assert not main_window.btn_home_page.isEnabled()

    def test_window_title_bar_visible(self, main_window):
        assert main_window.label_title_bar_top.isVisible()

    def test_drone_widget_has_minimal_api(self, main_window):
        """DroneStatusWidget should only expose connection + position slots."""
        widget = main_window.drone_status_widget
        # Required slots
        assert hasattr(widget, "set_connected")
        assert hasattr(widget, "update_position")
        assert hasattr(widget, "is_connected")
        # Removed slots should NOT exist
        assert not hasattr(widget, "update_battery")
        assert not hasattr(widget, "update_coordinator_state")
        assert not hasattr(widget, "update_protocol_state")
        assert not hasattr(widget, "on_target_detected")
        assert not hasattr(widget, "on_semantic_event")
        assert not hasattr(widget, "on_relay_status")

    def test_drone_widget_is_ui_file_backed(self, main_window):
        """DroneStatusWidget should load its layout from a .ui file."""
        widget = main_window.drone_status_widget
        # Must have the QUiLoader-loaded widget
        assert hasattr(widget, "_ui_widget"), (
            "DroneStatusWidget should load its UI from DroneStatusWidget.ui via QUiLoader"
        )
        # The .ui file must expose the named child widgets we depend on
        for attr in ("headerLabel", "connectionStatusLabel", "positionLabel"):
            assert hasattr(widget, attr), (
                f"DroneStatusWidget should expose '{attr}' from its .ui file"
            )

    def test_drone_widget_mounts_in_home(self, main_window):
        """DroneStatusWidget should be inside HomePage's droneFrame."""
        widget = main_window.drone_status_widget
        # Parent is the droneFrame QFrame inside HomePage, not HomePage directly
        parent = widget.parent()
        assert hasattr(parent, "objectName")
        assert parent.objectName() == "droneFrame"
