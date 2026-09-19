#!/usr/bin/env python3
"""
Library Manager - Cross-Platform Package Installation Tool
Main entry point for the application
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from ui.main_window import MainWindow


def _bail_if_spawned_as_interpreter():
    """Exit immediately when the frozen exe is re-launched as a "python".

    In frozen builds sys.executable is this exe; any code that runs
    ``[sys.executable, '--version'/'-m'/'-c', ...]`` would otherwise start a
    full new GUI instance, which spawns again -> infinite process loop.
    The app has no CLI, so any dash-prefixed argument means we were invoked
    as an interpreter substitute and must exit quietly.
    """
    if getattr(sys, 'frozen', False) and any(
        arg.startswith('-') for arg in sys.argv[1:]
    ):
        sys.exit(0)


def main():
    _bail_if_spawned_as_interpreter()
    """Initialize and run the application"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Library Manager")
    app.setOrganizationName("DevTools")
    app.setQuitOnLastWindowClosed(False)  # Keep app running when window is closed

    # Create and show main window
    window = MainWindow(app)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
