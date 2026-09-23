"""System Tray Icon Manager"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal
import os

from ui.i18n import tr


class SystemTrayManager(QObject):
    """Manages system tray icon and notifications"""

    show_window = pyqtSignal()
    quit_app = pyqtSignal()

    def __init__(self, app, main_window):
        super().__init__()
        self.app = app
        self.main_window = main_window
        self.tray_icon = None
        self.setup_tray()

    def setup_tray(self):
        """Setup system tray icon"""
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self.main_window)

        # Try to load icon, fallback to default if not found
        icon_path = self._get_icon_path()
        if icon_path and os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            # Use default PyQt icon
            icon = self.app.style().standardIcon(self.app.style().StandardPixmap.SP_ComputerIcon)

        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("Library Manager")

        # Create context menu
        menu = QMenu()

        # Show/Hide action
        self.show_action = QAction(tr('tray_show_window'), self.main_window)
        self.show_action.triggered.connect(self.show_main_window)
        menu.addAction(self.show_action)

        menu.addSeparator()

        # Scan action
        self.scan_action = QAction(tr('tray_scan'), self.main_window)
        self.scan_action.triggered.connect(self._scan_packages)
        menu.addAction(self.scan_action)

        # Virtual Environment Manager action
        self.venv_action = QAction(tr('tray_venv'), self.main_window)
        self.venv_action.triggered.connect(self._open_venv_manager)
        menu.addAction(self.venv_action)

        menu.addSeparator()

        # Quit action
        self.quit_action = QAction(tr('tray_quit'), self.main_window)
        self.quit_action.triggered.connect(self.quit_application)
        menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(menu)

        # Connect double-click to show window
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # Show the tray icon
        self.tray_icon.show()

    def _get_icon_path(self):
        """Get icon path"""
        # Try to find icon in various locations
        possible_paths = [
            "assets/icon.png",
            "assets/icon.ico",
            "../assets/icon.png",
            "../assets/icon.ico"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def on_tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_main_window()

    def retranslate(self):
        """Refresh tray menu texts in the current language"""
        if not self.tray_icon:
            return
        self.show_action.setText(tr('tray_show_window'))
        self.scan_action.setText(tr('tray_scan'))
        self.venv_action.setText(tr('tray_venv'))
        self.quit_action.setText(tr('tray_quit'))

    def show_main_window(self):
        """Show and raise main window"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _scan_packages(self):
        """Trigger package scan"""
        self.show_main_window()
        if hasattr(self.main_window, 'scan_installed_packages'):
            self.main_window.scan_installed_packages()

    def _open_venv_manager(self):
        """Open virtual environment manager"""
        self.show_main_window()
        if hasattr(self.main_window, 'open_venv_manager'):
            self.main_window.open_venv_manager()

    def quit_application(self):
        """Quit the application"""
        if self.tray_icon:
            self.tray_icon.hide()
        self.app.quit()

    def show_notification(self, title, message, icon_type=QSystemTrayIcon.MessageIcon.Information, duration=3000):
        """Show system notification"""
        if self.tray_icon and self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(title, message, icon_type, duration)

    def show_info(self, title, message):
        """Show info notification"""
        self.show_notification(title, message, QSystemTrayIcon.MessageIcon.Information)

    def show_warning(self, title, message):
        """Show warning notification"""
        self.show_notification(title, message, QSystemTrayIcon.MessageIcon.Warning)

    def show_error(self, title, message):
        """Show error notification"""
        self.show_notification(title, message, QSystemTrayIcon.MessageIcon.Critical)

    def is_available(self):
        """Check if system tray is available"""
        return self.tray_icon is not None and QSystemTrayIcon.isSystemTrayAvailable()
