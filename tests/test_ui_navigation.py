"""
Tests: Page navigation
Simulates clicking the sidebar nav buttons and verifies the stacked widget switches.
"""

from PySide6.QtCore import Qt


class TestPageNavigation:
    def test_click_indicators_page_button(self, main_window, qtbot):
        qtbot.mouseClick(main_window.btn_indicators_page, Qt.LeftButton)
        assert main_window.stackedWidget.currentWidget() is main_window.indicatorswidget

    def test_click_targets_page_button(self, main_window, qtbot):
        qtbot.mouseClick(main_window.btn_targets_page, Qt.LeftButton)
        assert main_window.stackedWidget.currentWidget() is main_window.targetspage

    def test_click_home_page_button(self, main_window, qtbot):
        # Navigate away first
        qtbot.mouseClick(main_window.btn_targets_page, Qt.LeftButton)
        assert main_window.stackedWidget.currentWidget() is main_window.targetspage

        # Now go home
        qtbot.mouseClick(main_window.btn_home_page, Qt.LeftButton)
        assert main_window.stackedWidget.currentWidget() is main_window.homepage

    def test_active_page_button_becomes_disabled(self, main_window, qtbot):
        """The active page button is disabled (indicates current selection)."""
        qtbot.mouseClick(main_window.btn_targets_page, Qt.LeftButton)
        assert not main_window.btn_targets_page.isEnabled()
        assert main_window.btn_home_page.isEnabled()

        qtbot.mouseClick(main_window.btn_home_page, Qt.LeftButton)
        assert not main_window.btn_home_page.isEnabled()
        assert main_window.btn_targets_page.isEnabled()

    def test_indicators_button_becomes_disabled_when_active(self, main_window, qtbot):
        qtbot.mouseClick(main_window.btn_indicators_page, Qt.LeftButton)
        assert not main_window.btn_indicators_page.isEnabled()

        # Restore home
        qtbot.mouseClick(main_window.btn_home_page, Qt.LeftButton)


class TestMenuToggle:
    STANDARD_WIDTH = 70
    MAX_WIDTH = 240

    def _get_menu_width(self, main_window):
        return main_window.frame_left_menu.width()

    def test_menu_starts_collapsed(self, main_window):
        assert self._get_menu_width(main_window) == self.STANDARD_WIDTH

    def test_toggle_expands_menu(self, main_window, qtbot):
        # Start collapsed
        assert self._get_menu_width(main_window) == self.STANDARD_WIDTH

        qtbot.mouseClick(main_window.btn_toggle_menu, Qt.LeftButton)
        # Wait for the 300ms animation to finish
        qtbot.wait(400)

        assert self._get_menu_width(main_window) == self.MAX_WIDTH

    def test_toggle_shows_page_labels_when_expanded(self, main_window, qtbot):
        # Ensure expanded state from previous test
        if self._get_menu_width(main_window) != self.MAX_WIDTH:
            qtbot.mouseClick(main_window.btn_toggle_menu, Qt.LeftButton)
            qtbot.wait(400)

        assert "Home" in main_window.btn_home_page.text()
        assert "Indicators" in main_window.btn_indicators_page.text()
        assert "Mission" in main_window.btn_targets_page.text()

    def test_toggle_collapses_menu(self, main_window, qtbot):
        # Ensure expanded
        if self._get_menu_width(main_window) != self.MAX_WIDTH:
            qtbot.mouseClick(main_window.btn_toggle_menu, Qt.LeftButton)
            qtbot.wait(400)

        # Collapse
        qtbot.mouseClick(main_window.btn_toggle_menu, Qt.LeftButton)
        qtbot.wait(400)

        assert self._get_menu_width(main_window) == self.STANDARD_WIDTH

    def test_toggle_clears_labels_when_collapsed(self, main_window, qtbot):
        # Ensure collapsed state
        if self._get_menu_width(main_window) != self.STANDARD_WIDTH:
            qtbot.mouseClick(main_window.btn_toggle_menu, Qt.LeftButton)
            qtbot.wait(400)

        assert main_window.btn_home_page.text() == ""
        assert main_window.btn_indicators_page.text() == ""
        assert main_window.btn_targets_page.text() == ""
