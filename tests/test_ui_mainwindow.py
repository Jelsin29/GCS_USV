"""
Tests: MainWindow initial state
Verifies the window opens with correct widgets and default values.
"""

import pytest
from PySide6.QtWidgets import QStackedWidget, QComboBox, QPushButton


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

    def test_nav_buttons_exist(self, main_window):
        assert hasattr(main_window, "btn_home_page")
        assert hasattr(main_window, "btn_indicators_page")
        assert hasattr(main_window, "btn_targets_page")

    def test_home_button_disabled_on_startup(self, main_window):
        # btn_home_page starts disabled (we're already on home)
        assert not main_window.btn_home_page.isEnabled()

    def test_window_title_bar_visible(self, main_window):
        assert main_window.label_title_bar_top.isVisible()
