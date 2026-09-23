"""Main application window"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTextEdit, QSplitter,
    QLabel, QCheckBox, QScrollArea, QFrame, QMessageBox,
    QStackedWidget, QListWidgetItem, QComboBox
)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont
from core.library_data import LIBRARY_CATEGORIES
from core.installer import PackageInstaller
from ui.theme_manager import ThemeManager
from ui.i18n import tr, set_language, get_language
from ui.package_details_dialog import PackageDetailsDialog
from ui.venv_manager_dialog import VenvManagerDialog
from ui.version_selector_dialog import VersionSelectorDialog
from ui.dependency_viewer_dialog import DependencyViewerDialog
from ui.system_tray import SystemTrayManager
from ui.python_selector_dialog import PythonSelectorDialog


class LibraryItem(QWidget):
    """Custom widget for library item with checkbox"""

    def __init__(self, name, description, install_cmd, is_installed=False, parent=None):
        super().__init__(parent)
        self.name = name
        self.description = description
        self.install_cmd = install_cmd
        self.is_installed = is_installed

        layout = QHBoxLayout()
        layout.setContentsMargins(10, 8, 10, 8)

        # Checkbox
        self.checkbox = QCheckBox()
        self.checkbox.setFixedWidth(30)
        layout.addWidget(self.checkbox)

        # Info layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Name label with installed badge
        if is_installed:
            name_label = QLabel(f"<b>{name}</b> <span style='background-color: #27ae60; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;'>✓ INSTALLED</span>")
        else:
            name_label = QLabel(f"<b>{name}</b>")
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)

        # Description label
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666;")
        info_layout.addWidget(desc_label)

        # Command label
        cmd_label = QLabel(f"<code>{install_cmd}</code>")
        cmd_label.setWordWrap(True)
        cmd_label.setStyleSheet("color: #0066cc; font-size: 11px;")
        info_layout.addWidget(cmd_label)

        layout.addLayout(info_layout, 1)

        # Buttons layout
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(5)

        # Versions button
        versions_btn = QPushButton("Versions")
        versions_btn.setFixedSize(100, 28)
        versions_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        versions_btn.clicked.connect(self.show_versions)
        buttons_layout.addWidget(versions_btn)

        # Details button
        details_btn = QPushButton("Details")
        details_btn.setFixedSize(100, 28)
        details_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        details_btn.clicked.connect(self.show_details)
        buttons_layout.addWidget(details_btn)

        # Dependencies button
        deps_btn = QPushButton("Dependencies")
        deps_btn.setFixedSize(100, 28)
        deps_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        deps_btn.clicked.connect(self.show_dependencies)
        buttons_layout.addWidget(deps_btn)

        layout.addLayout(buttons_layout)
        self.setLayout(layout)

        # Add bottom border
        self.setStyleSheet("""
            LibraryItem {
                border-bottom: 1px solid #e0e0e0;
            }
        """)

    def is_checked(self):
        """Check if item is selected"""
        return self.checkbox.isChecked()

    def set_checked(self, checked):
        """Set checkbox state"""
        self.checkbox.setChecked(checked)

    def show_details(self):
        """Show package details dialog"""
        dialog = PackageDetailsDialog(self.name, self.description, self.install_cmd, self)
        dialog.exec()

    def show_versions(self):
        """Show package version selector dialog"""
        dialog = VersionSelectorDialog(self.name, self)
        dialog.exec()

    def show_dependencies(self):
        """Show package dependency viewer dialog"""
        dialog = DependencyViewerDialog(self.name, self)
        dialog.exec()


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self, app=None):
        super().__init__()
        self.app = app
        self.installer = PackageInstaller()
        self.theme_manager = ThemeManager()
        self.library_items = []
        self.current_category = None
        self.installed_packages_cache = None  # Cache for installed packages
        self.system_tray = None
        self.selected_python_path = None  # Selected Python version path
        self.selected_python_version = None  # Selected Python version string
        self.current_view = "packages"  # Track current view: packages, scan, venv, python

        # Load persisted settings (theme + language) before building the UI
        self.settings = QSettings("DevTools", "Library Manager")
        set_language(self.settings.value("language", "en"))
        self.theme_manager.is_dark = self.settings.value("theme", "light") == "dark"

        self.init_ui()
        self.apply_theme()

        # Setup system tray (if app reference is provided)
        if self.app:
            self.system_tray = SystemTrayManager(self.app, self)
            if self.system_tray.is_available():
                self.system_tray.show_info(
                    "Library Manager",
                    "Application started. Click the tray icon to show/hide the window."
                )

        # Load first category (without checking installations to speed up)
        if LIBRARY_CATEGORIES:
            first_category = list(LIBRARY_CATEGORIES.keys())[0]
            self.load_category(first_category, check_installed=False)

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Library Manager - Cross-Platform Package Installer")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main vertical layout (header + content)
        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.setSpacing(0)
        main_vertical_layout.setContentsMargins(0, 0, 0, 0)

        # Create header toolbar
        header_toolbar = self.create_header_toolbar()
        main_vertical_layout.addWidget(header_toolbar)

        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()

        # View 1: Main package manager (sidebar + content)
        self.packages_view = self.create_packages_view()
        self.stacked_widget.addWidget(self.packages_view)

        # View 2: Scan results view
        self.scan_view = self.create_scan_view()
        self.stacked_widget.addWidget(self.scan_view)

        # View 3: Virtual Environment Manager view
        self.venv_view = self.create_venv_view()
        self.stacked_widget.addWidget(self.venv_view)

        # View 4: Python Selector view
        self.python_view = self.create_python_view()
        self.stacked_widget.addWidget(self.python_view)

        # View 5: Bulk Update Manager view
        self.update_view = self.create_update_view()
        self.stacked_widget.addWidget(self.update_view)

        # View 6: Requirements Manager view
        self.requirements_view = self.create_requirements_view()
        self.stacked_widget.addWidget(self.requirements_view)

        # View 7: Settings view
        self.settings_view = self.create_settings_view()
        self.stacked_widget.addWidget(self.settings_view)

        main_vertical_layout.addWidget(self.stacked_widget)

        central_widget.setLayout(main_vertical_layout)

        # Add status bar
        self.status_bar = self.statusBar()
        self.update_status_bar()

    def create_packages_view(self):
        """Create the main packages view with sidebar and content"""
        view = QWidget()
        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create sidebar
        sidebar = self.create_sidebar()
        layout.addWidget(sidebar)

        # Create main content area
        content_area = self.create_content_area()
        layout.addWidget(content_area, 1)

        view.setLayout(layout)
        return view

    def create_scan_view(self):
        """Create scan results view"""
        view = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header
        header = self.scan_header = QLabel(tr('scan_title'))
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #16a085; padding: 10px;")
        layout.addWidget(header)

        # Description
        desc = self.scan_desc = QLabel(tr('scan_desc'))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; font-size: 13px; padding: 5px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Scan button
        scan_btn = QPushButton("🔍 Start Scan")
        scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1abc9c;
            }
        """)
        scan_btn.setFixedWidth(200)
        scan_btn.clicked.connect(self.run_scan_in_view)

        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(scan_btn)
        button_layout.addStretch()
        button_container.setLayout(button_layout)
        layout.addWidget(button_container)

        # Results area
        self.scan_results_text = QTextEdit()
        self.scan_results_text.setReadOnly(True)
        self.scan_results_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.scan_results_text)

        view.setLayout(layout)
        return view

    def create_venv_view(self):
        """Create virtual environment manager view - embedded"""
        from core.venv_manager import VirtualEnvManager

        view = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = self.venv_header = QLabel(tr('venv_title'))
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #9b59b6; padding: 10px;")
        layout.addWidget(header)

        # Info label
        venv_mgr = VirtualEnvManager()
        info_path = venv_mgr.get_default_venv_path()
        info = QLabel(f"<b>Default Location:</b> {info_path}")
        info.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(info)

        # Toolbar
        toolbar = QHBoxLayout()

        new_btn = QPushButton("➕ New Environment")
        new_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        new_btn.clicked.connect(self.venv_create_new)
        toolbar.addWidget(new_btn)

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_btn.clicked.connect(self.venv_refresh_list)
        toolbar.addWidget(refresh_btn)

        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(self.venv_delete_selected)
        toolbar.addWidget(delete_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Virtual environments list
        self.venv_list_widget = QListWidget()
        self.venv_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #bdc3c7;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.venv_list_widget)

        # Details area
        self.venv_details_text = QTextEdit()
        self.venv_details_text.setReadOnly(True)
        self.venv_details_text.setMaximumHeight(150)
        self.venv_details_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.venv_details_text)

        view.setLayout(layout)

        # Store reference for later use
        self.venv_manager = venv_mgr

        return view

    def create_python_view(self):
        """Create Python selector view - embedded"""
        from core.python_detector import PythonDetector

        view = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = self.python_header = QLabel(tr('python_title'))
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #3498db; padding: 10px;")
        layout.addWidget(header)

        # Description
        desc = self.python_desc = QLabel(tr('python_desc'))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; font-size: 13px; padding: 5px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Toolbar
        toolbar = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        refresh_btn.clicked.connect(self.python_refresh_list)
        toolbar.addWidget(refresh_btn)

        toolbar.addStretch()

        select_btn = QPushButton("✓ Select This Python")
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        select_btn.clicked.connect(self.python_select_current)
        toolbar.addWidget(select_btn)

        layout.addLayout(toolbar)

        # Python list
        self.python_list_widget = QListWidget()
        self.python_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #bdc3c7;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.python_list_widget)

        # Info panel
        self.python_info_text = QTextEdit()
        self.python_info_text.setReadOnly(True)
        self.python_info_text.setMaximumHeight(150)
        self.python_info_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.python_info_text)

        view.setLayout(layout)

        # Store reference
        self.python_detector = PythonDetector()

        return view

    def create_update_view(self):
        """Create Bulk Update Manager view"""
        from core.update_manager import UpdateManager

        view = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = self.update_header = QLabel(tr('update_title'))
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #27ae60; padding: 10px;")
        layout.addWidget(header)

        # Description
        desc = self.update_desc = QLabel(tr('update_desc'))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; font-size: 13px; padding: 5px;")
        layout.addWidget(desc)

        # Toolbar
        toolbar = QHBoxLayout()

        check_btn = QPushButton("Check for Updates")
        check_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        check_btn.clicked.connect(self.update_check_outdated)
        toolbar.addWidget(check_btn)

        update_all_btn = QPushButton("Update All")
        update_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        update_all_btn.clicked.connect(self.update_all_packages)
        toolbar.addWidget(update_all_btn)

        toolbar.addStretch()

        # China mirror source checkbox and dropdown
        self.mirror_checkbox = QCheckBox(tr('mirror_checkbox'))
        self.mirror_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                font-weight: bold;
                color: #2c3e50;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
        """)
        self.mirror_checkbox.stateChanged.connect(self.toggle_mirror_dropdown)
        toolbar.addWidget(self.mirror_checkbox)

        self.mirror_dropdown = QComboBox()
        self._populate_mirror_dropdown()
        self.mirror_dropdown.setEnabled(False)
        self.mirror_dropdown.setStyleSheet("""
            QComboBox {
                padding: 8px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 12px;
                min-width: 350px;
                background-color: white;
            }
            QComboBox:hover {
                border: 2px solid #3498db;
            }
            QComboBox:disabled {
                background-color: #ecf0f1;
                color: #95a5a6;
            }
        """)
        toolbar.addWidget(self.mirror_dropdown)

        layout.addLayout(toolbar)

        # Outdated packages list
        self.update_list_widget = QListWidget()
        self.update_list_widget.setStyleSheet("""
            QListWidget {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 5px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #bdc3c7;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.update_list_widget)

        # Results area
        self.update_results_text = QTextEdit()
        self.update_results_text.setReadOnly(True)
        self.update_results_text.setMaximumHeight(150)
        self.update_results_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.update_results_text)

        view.setLayout(layout)

        # Store reference
        self.update_manager = UpdateManager()

        return view

    def create_requirements_view(self):
        """Create Requirements.txt Manager view"""
        from core.requirements_manager import RequirementsManager

        view = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = self.req_header = QLabel(tr('req_title'))
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #e67e22; padding: 10px;")
        layout.addWidget(header)

        # Description
        desc = self.req_desc = QLabel(tr('req_desc'))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #7f8c8d; font-size: 13px; padding: 5px;")
        layout.addWidget(desc)

        # Toolbar
        toolbar = QHBoxLayout()

        import_btn = QPushButton("Import")
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        import_btn.clicked.connect(self.req_import_file)
        toolbar.addWidget(import_btn)

        export_btn = QPushButton("Export All")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        export_btn.clicked.connect(self.req_export_all)
        toolbar.addWidget(export_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Info text
        self.req_info_text = QTextEdit()
        self.req_info_text.setReadOnly(True)
        self.req_info_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        self.req_info_text.setPlainText("Import: Load packages from requirements.txt\nExport: Save installed packages to requirements.txt")
        layout.addWidget(self.req_info_text)

        view.setLayout(layout)

        # Store reference
        self.requirements_manager = RequirementsManager()

        return view

    def create_header_toolbar(self):
        """Create header toolbar with action tabs"""
        toolbar = QFrame()
        toolbar.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-bottom: 2px solid #3498db;
            }
        """)

        layout = QHBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Home/Packages tab
        self.nav_packages_btn = QPushButton(tr('nav_packages'))
        self.nav_packages_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 13px;
                font-weight: bold;
                border-right: 1px solid #2c3e50;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.nav_packages_btn.clicked.connect(lambda: self.switch_view(0))  # Index 0 for packages view
        layout.addWidget(self.nav_packages_btn)

        # Scan System tab
        self.nav_scan_btn = QPushButton(tr('nav_scan'))
        self.nav_scan_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 13px;
                font-weight: bold;
                border-right: 1px solid #2c3e50;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.nav_scan_btn.clicked.connect(lambda: self.switch_view(1))  # Index 1 for scan view
        layout.addWidget(self.nav_scan_btn)

        # Virtual Environment Manager tab
        self.nav_venv_btn = QPushButton(tr('nav_venv'))
        self.nav_venv_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 13px;
                font-weight: bold;
                border-right: 1px solid #2c3e50;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.nav_venv_btn.clicked.connect(lambda: self.switch_view(2))  # Index 2 for venv view
        layout.addWidget(self.nav_venv_btn)

        # Python Version Selector tab
        self.nav_python_btn = QPushButton(tr('nav_python'))
        self.nav_python_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 13px;
                font-weight: bold;
                border-right: 1px solid #2c3e50;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.nav_python_btn.clicked.connect(lambda: self.switch_view(3))  # Index 3 for python view
        layout.addWidget(self.nav_python_btn)

        # Bulk Update Manager tab
        self.nav_update_btn = QPushButton(tr('nav_update'))
        self.nav_update_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 13px;
                font-weight: bold;
                border-right: 1px solid #2c3e50;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.nav_update_btn.clicked.connect(lambda: self.switch_view(4))  # Index 4 for update view
        layout.addWidget(self.nav_update_btn)

        # Requirements Manager tab
        self.nav_requirements_btn = QPushButton(tr('nav_requirements'))
        self.nav_requirements_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 13px;
                font-weight: bold;
                border-right: 1px solid #2c3e50;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.nav_requirements_btn.clicked.connect(lambda: self.switch_view(5))  # Index 5 for requirements view
        layout.addWidget(self.nav_requirements_btn)

        # Add stretch to push buttons to left
        layout.addStretch()

        # Settings button on right (replaces the old "Toggle Theme" button)
        self.nav_settings_btn = QPushButton(tr('nav_settings'))
        self.nav_settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.nav_settings_btn.clicked.connect(lambda: self.switch_view(6))
        layout.addWidget(self.nav_settings_btn)

        toolbar.setLayout(layout)
        return toolbar

    def create_sidebar(self):
        """Create category sidebar"""
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setFrameShape(QFrame.Shape.StyledPanel)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-right: 1px solid #34495e;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        self.sidebar_header = QLabel(tr('sidebar_categories'))
        self.sidebar_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sidebar_header.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                font-size: 18px;
                font-weight: bold;
                padding: 20px;
                border-bottom: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.sidebar_header)

        # Scrollable area for category buttons
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #2c3e50;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2c3e50;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #34495e;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #3498db;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Container for category buttons
        categories_widget = QWidget()
        categories_widget.setStyleSheet("background-color: #2c3e50;")
        categories_layout = QVBoxLayout()
        categories_layout.setSpacing(0)
        categories_layout.setContentsMargins(0, 0, 0, 0)

        # Category buttons
        self.category_buttons = {}
        for category in LIBRARY_CATEGORIES.keys():
            btn = QPushButton(tr('cat.' + category))
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                    padding: 15px;
                    text-align: left;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #34495e;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    font-weight: bold;
                }
            """)
            btn.clicked.connect(lambda checked, cat=category: self.load_category(cat))
            categories_layout.addWidget(btn)
            self.category_buttons[category] = btn

        categories_layout.addStretch()
        categories_widget.setLayout(categories_layout)
        scroll.setWidget(categories_widget)
        layout.addWidget(scroll, 1)

        sidebar.setLayout(layout)
        return sidebar

    def create_content_area(self):
        """Create main content area"""
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Top bar
        top_bar = QFrame()
        top_bar.setFixedHeight(60)
        top_bar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-bottom: 2px solid #e0e0e0;
            }
        """)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(20, 10, 20, 10)

        self.category_label = QLabel(tr('content_select_category'))
        self.category_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50;")
        top_layout.addWidget(self.category_label)

        top_layout.addStretch()

        # Select All / Deselect All buttons
        self.select_all_btn = QPushButton(tr('btn_select_all'))
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        top_layout.addWidget(self.select_all_btn)

        self.deselect_all_btn = QPushButton(tr('btn_deselect_all'))
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        self.deselect_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        top_layout.addWidget(self.deselect_all_btn)

        top_bar.setLayout(top_layout)
        layout.addWidget(top_bar)

        # Splitter for libraries and log
        splitter = QSplitter(Qt.Orientation.Vertical)

        # Libraries scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: white; }")

        self.libraries_widget = QWidget()
        self.libraries_layout = QVBoxLayout()
        self.libraries_layout.setSpacing(0)
        self.libraries_layout.setContentsMargins(0, 0, 0, 0)
        self.libraries_widget.setLayout(self.libraries_layout)

        scroll.setWidget(self.libraries_widget)
        splitter.addWidget(scroll)

        # Log area
        log_container = QWidget()
        log_layout = QVBoxLayout()
        log_layout.setContentsMargins(10, 10, 10, 10)

        log_label = QLabel("Installation Log:")
        log_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        log_layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #444;
                border-radius: 4px;
            }
        """)
        log_layout.addWidget(self.log_text)

        log_container.setLayout(log_layout)
        splitter.addWidget(log_container)

        # Set splitter sizes
        splitter.setSizes([500, 200])
        layout.addWidget(splitter)

        # Bottom action bar
        action_bar = QFrame()
        action_bar.setFixedHeight(70)
        action_bar.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border-top: 1px solid #bdc3c7;
            }
        """)
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(20, 15, 20, 15)

        # Install button
        self.install_btn = QPushButton("Install Selected")
        self.install_btn.setFixedHeight(40)
        self.install_btn.clicked.connect(self.install_selected)
        self.install_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        action_layout.addWidget(self.install_btn)

        # Uninstall button
        self.uninstall_btn = QPushButton("Uninstall Selected")
        self.uninstall_btn.setFixedHeight(40)
        self.uninstall_btn.clicked.connect(self.uninstall_selected)
        self.uninstall_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        action_layout.addWidget(self.uninstall_btn)

        action_layout.addStretch()

        # Exit button
        exit_btn = QPushButton("Exit")
        exit_btn.setFixedHeight(40)
        exit_btn.clicked.connect(self.close)
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 5px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        action_layout.addWidget(exit_btn)

        action_bar.setLayout(action_layout)
        layout.addWidget(action_bar)

        content.setLayout(layout)
        return content

    def load_category(self, category, check_installed=True):
        """Load libraries for selected category"""
        self.current_category = category
        self.category_label.setText(tr('cat.' + category))

        # Update button states
        for cat, btn in self.category_buttons.items():
            btn.setChecked(cat == category)

        # Clear existing items
        while self.libraries_layout.count():
            child = self.libraries_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.library_items.clear()

        # Build installed packages cache if needed and requested
        if check_installed and self.installed_packages_cache is None:
            self._build_installed_cache()

        # Add library items
        libraries = LIBRARY_CATEGORIES.get(category, [])
        for lib in libraries:
            # Check if package is installed (use cache for speed)
            is_installed = False
            if check_installed and self.installed_packages_cache is not None:
                pkg_name = lib["name"].lower().replace("-", "_")
                is_installed = (pkg_name in self.installed_packages_cache or
                               lib["name"].lower() in self.installed_packages_cache)

            item = LibraryItem(lib["name"], lib["description"], lib["install_cmd"], is_installed)
            self.libraries_layout.addWidget(item)
            self.library_items.append(item)

        # Add stretch at the end
        self.libraries_layout.addStretch()

    def _build_installed_cache(self):
        """Build cache of installed packages for fast lookup"""
        try:
            success, output = self.installer.list_installed()
            if success:
                self.installed_packages_cache = set()
                lines = output.strip().split('\n')
                for line in lines[2:]:  # Skip header lines
                    parts = line.split()
                    if parts:
                        package_name = parts[0].lower()
                        self.installed_packages_cache.add(package_name)
                        # Also add with underscores replaced by hyphens
                        self.installed_packages_cache.add(package_name.replace("_", "-"))
                        self.installed_packages_cache.add(package_name.replace("-", "_"))
        except Exception:
            self.installed_packages_cache = set()

    def select_all(self):
        """Select all libraries in current category"""
        for item in self.library_items:
            item.set_checked(True)

    def deselect_all(self):
        """Deselect all libraries"""
        for item in self.library_items:
            item.set_checked(False)

    def install_selected(self):
        """Install selected libraries"""
        selected = [item for item in self.library_items if item.is_checked()]

        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select at least one library to install.")
            return

        # Disable buttons during installation
        self.install_btn.setEnabled(False)
        self.uninstall_btn.setEnabled(False)

        self.log_text.clear()
        self.log("Starting installation...\n")
        self.log(f"Operating System: {self.installer.get_os_info()}\n")
        self.log("-" * 80 + "\n\n")

        # Install each selected library
        success_count = 0
        fail_count = 0

        for item in selected:
            self.log(f"Installing: {item.name}\n")
            self.log(f"Command: {item.install_cmd}\n")

            success, output = self.installer.install_package(item.install_cmd)

            if success:
                self.log(f"✓ Successfully installed {item.name}\n")
                success_count += 1
            else:
                self.log(f"✗ Failed to install {item.name}\n")
                fail_count += 1

            self.log(output + "\n")
            self.log("-" * 80 + "\n\n")

        # Summary
        self.log(f"\n{'=' * 80}\n")
        self.log(f"Installation Summary:\n")
        self.log(f"  Successful: {success_count}\n")
        self.log(f"  Failed: {fail_count}\n")
        self.log(f"{'=' * 80}\n")

        # Re-enable buttons
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)

        # Show completion message
        if fail_count == 0:
            QMessageBox.information(self, "Success", f"All {success_count} packages installed successfully!")
            if self.system_tray:
                self.system_tray.show_info(
                    "Installation Complete",
                    f"Successfully installed {success_count} package(s)!"
                )
        else:
            QMessageBox.warning(self, "Completed with Errors",
                                f"Installation completed.\n\nSuccessful: {success_count}\nFailed: {fail_count}")
            if self.system_tray:
                self.system_tray.show_warning(
                    "Installation Completed",
                    f"Installed {success_count} package(s), {fail_count} failed."
                )

    def uninstall_selected(self):
        """Uninstall selected libraries"""
        selected = [item for item in self.library_items if item.is_checked()]

        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select at least one library to uninstall.")
            return

        # Confirm uninstallation
        reply = QMessageBox.question(self, "Confirm Uninstall",
                                      f"Are you sure you want to uninstall {len(selected)} package(s)?",
                                      QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.No:
            return

        # Disable buttons during uninstallation
        self.install_btn.setEnabled(False)
        self.uninstall_btn.setEnabled(False)

        self.log_text.clear()
        self.log("Starting uninstallation...\n")
        self.log("-" * 80 + "\n\n")

        success_count = 0
        fail_count = 0

        for item in selected:
            self.log(f"Uninstalling: {item.name}\n")

            success, output = self.installer.uninstall_package(item.name)

            if success:
                self.log(f"✓ Successfully uninstalled {item.name}\n")
                success_count += 1
            else:
                self.log(f"✗ Failed to uninstall {item.name}\n")
                fail_count += 1

            self.log(output + "\n")
            self.log("-" * 80 + "\n\n")

        # Summary
        self.log(f"\n{'=' * 80}\n")
        self.log(f"Uninstallation Summary:\n")
        self.log(f"  Successful: {success_count}\n")
        self.log(f"  Failed: {fail_count}\n")
        self.log(f"{'=' * 80}\n")

        # Re-enable buttons
        self.install_btn.setEnabled(True)
        self.uninstall_btn.setEnabled(True)

        # Show completion message
        if fail_count == 0:
            QMessageBox.information(self, "Success", f"All {success_count} packages uninstalled successfully!")
            if self.system_tray:
                self.system_tray.show_info(
                    "Uninstallation Complete",
                    f"Successfully uninstalled {success_count} package(s)!"
                )
        else:
            QMessageBox.warning(self, "Completed with Errors",
                                f"Uninstallation completed.\n\nSuccessful: {success_count}\nFailed: {fail_count}")
            if self.system_tray:
                self.system_tray.show_warning(
                    "Uninstallation Completed",
                    f"Uninstalled {success_count} package(s), {fail_count} failed."
                )

    def run_scan_in_view(self):
        """Run scan and display results in scan view"""
        self.scan_results_text.clear()
        self.scan_results_text.append("🔍 Scanning system for installed packages...\n")
        self.scan_results_text.append("=" * 80 + "\n\n")

        # Get list of installed packages
        success, output = self.installer.list_installed()

        if not success:
            self.scan_results_text.append("✗ Failed to get installed packages list\n")
            self.scan_results_text.append(output)
            return

        # Parse installed packages
        installed_packages = set()
        lines = output.strip().split('\n')
        for line in lines[2:]:  # Skip header
            parts = line.split()
            if parts:
                installed_packages.add(parts[0].lower())

        self.scan_results_text.append(f"Found {len(installed_packages)} installed packages on your system.\n\n")

        # Match with our database
        found_packages = []
        for category, packages in LIBRARY_CATEGORIES.items():
            for pkg in packages:
                pkg_name = pkg['name'].lower().replace('-', '_')
                if pkg_name in installed_packages or pkg_name.replace('_', '-') in installed_packages:
                    found_packages.append({
                        'name': pkg['name'],
                        'category': category,
                        'description': pkg['description']
                    })

        self.scan_results_text.append(f"Matched {len(found_packages)} packages from our database:\n")
        self.scan_results_text.append("-" * 80 + "\n\n")

        # Display found packages
        for pkg in found_packages:
            self.scan_results_text.append(f"📦 {pkg['name']}\n")
            self.scan_results_text.append(f"   Category: {pkg['category']}\n")
            self.scan_results_text.append(f"   Description: {pkg['description']}\n\n")

        self.scan_results_text.append("=" * 80 + "\n")
        self.scan_results_text.append(f"\nScan Summary:\n")
        self.scan_results_text.append(f"  Total packages on system: {len(installed_packages)}\n")
        self.scan_results_text.append(f"  Packages in our database: {len(found_packages)}\n")
        self.scan_results_text.append("=" * 80 + "\n")

    def scan_system_packages(self):
        """Scan system for installed packages and create a virtual category"""
        self.log_text.clear()
        self.log("🔍 Scanning system for installed packages...\n")
        self.log("=" * 80 + "\n\n")

        # Get list of installed packages
        success, output = self.installer.list_installed()

        if not success:
            self.log("✗ Failed to get installed packages list\n")
            self.log(output)
            QMessageBox.warning(self, "Scan Failed", "Failed to scan installed packages.")
            return

        # Parse the output to get package names
        installed_packages = set()
        lines = output.strip().split('\n')

        for line in lines[2:]:  # Skip header lines
            parts = line.split()
            if parts:
                package_name = parts[0].lower()
                installed_packages.add(package_name)

        self.log(f"✓ Found {len(installed_packages)} installed packages\n\n")

        # Find matching packages from our database
        found_packages = []
        for category, packages in LIBRARY_CATEGORIES.items():
            for pkg in packages:
                pkg_name = pkg["name"].lower().replace("-", "_")
                # Check various name formats
                if (pkg_name in installed_packages or
                    pkg["name"].lower() in installed_packages or
                    pkg["name"].lower().replace("_", "-") in installed_packages):
                    found_packages.append({
                        "name": pkg["name"],
                        "description": pkg["description"],
                        "install_cmd": pkg["install_cmd"],
                        "category": category
                    })

        if not found_packages:
            self.log("No packages from the library database found on your system.\n")
            self.log("This is normal if you haven't installed packages using this tool yet.\n")
            QMessageBox.information(self, "Scan Complete",
                                    "No packages from the library database found.\n"
                                    "You can install packages from any category!")
            return

        # Display results
        self.log(f"✓ Found {len(found_packages)} packages from our database:\n")
        self.log("-" * 80 + "\n\n")

        for pkg in found_packages:
            self.log(f"📦 {pkg['name']}\n")
            self.log(f"   Category: {pkg['category']}\n")
            self.log(f"   Description: {pkg['description']}\n\n")

        self.log("=" * 80 + "\n")
        self.log(f"\nScan Summary:\n")
        self.log(f"  Total packages on system: {len(installed_packages)}\n")
        self.log(f"  Packages in our database: {len(found_packages)}\n")
        self.log("=" * 80 + "\n")

        # Show summary message
        QMessageBox.information(self, "Scan Complete",
                                f"System scan completed!\n\n"
                                f"Found {len(found_packages)} packages from our database.\n"
                                f"Check the log panel for details.")

    def log(self, message):
        """Append message to log"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )

    def switch_view(self, index):
        """Switch between different views"""
        self.stacked_widget.setCurrentIndex(index)
        self.current_view = ["packages", "scan", "venv", "python", "update", "requirements", "settings"][index]

        # Load data when switching to certain views
        if index == 2:  # Venv view
            self.venv_refresh_list()
        elif index == 3:  # Python view
            self.python_refresh_list()
        elif index == 4:  # Update view
            self.update_results_text.setPlainText("Click 'Check for Updates' to find outdated packages")
        elif index == 5:  # Requirements view
            self.req_info_text.setPlainText("Import: Load packages from requirements.txt\nExport: Save installed packages to requirements.txt")

    def venv_create_new(self):
        """Create a new virtual environment"""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "New Environment", "Environment name:")
        if ok and name:
            self.venv_details_text.setPlainText(f"Creating virtual environment '{name}'...\n")
            success, message = self.venv_manager.create_venv(name)
            if success:
                self.venv_details_text.append(f"✓ Successfully created: {name}\n")
                self.venv_details_text.append(message)
                self.venv_refresh_list()
            else:
                self.venv_details_text.append(f"✗ Failed to create: {name}\n")
                self.venv_details_text.append(message)

    def venv_refresh_list(self):
        """Refresh virtual environments list"""
        self.venv_list_widget.clear()
        venvs = self.venv_manager.list_venvs()
        if not venvs:
            item = QListWidgetItem("No virtual environments found")
            self.venv_list_widget.addItem(item)
            self.venv_details_text.setPlainText("No virtual environments found.\nClick '➕ New Environment' to create one.")
        else:
            for venv in venvs:
                item = QListWidgetItem(f"📁 {venv['name']}")
                item.setData(Qt.ItemDataRole.UserRole, venv)
                self.venv_list_widget.addItem(item)
            self.venv_list_widget.itemClicked.connect(self.venv_show_details)

    def venv_show_details(self, item):
        """Show details of selected virtual environment"""
        venv = item.data(Qt.ItemDataRole.UserRole)
        if venv:
            info = self.venv_manager.get_venv_info(venv['name'])
            details = f"""Virtual Environment: {venv['name']}
Path: {venv['path']}
Python Version: {info.get('python_version', 'Unknown')}
Packages: {info.get('package_count', 0)}
Size: {info.get('size', 'Unknown')}

Activation Command:
{info.get('activate_command', 'N/A')}
"""
            self.venv_details_text.setPlainText(details)

    def venv_delete_selected(self):
        """Delete selected virtual environment"""
        current = self.venv_list_widget.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a virtual environment to delete.")
            return

        venv = current.data(Qt.ItemDataRole.UserRole)
        if not venv:
            return

        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete '{venv['name']}'?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success, message = self.venv_manager.delete_venv(venv['name'])
            if success:
                self.venv_details_text.setPlainText(f"✓ Successfully deleted: {venv['name']}")
                self.venv_refresh_list()
            else:
                self.venv_details_text.setPlainText(f"✗ Failed to delete: {venv['name']}\n{message}")

    def python_refresh_list(self):
        """Refresh Python versions list"""
        self.python_list_widget.clear()
        self.python_info_text.setPlainText("Detecting Python installations...")

        pythons = self.python_detector.detect_all()
        if not pythons:
            item = QListWidgetItem("⚠️ No Python installations found")
            self.python_list_widget.addItem(item)
            self.python_info_text.setPlainText("No Python installations found.\nPlease install Python and refresh.")
        else:
            for python in pythons:
                display_text = f"Python {python.version}"
                if python.is_current:
                    display_text += " ★ CURRENT"
                if python.is_venv:
                    display_text += " [Virtual Env]"

                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, python)

                # Highlight current Python
                if python.is_current:
                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                self.python_list_widget.addItem(item)

            self.python_list_widget.itemClicked.connect(self.python_show_info)
            self.python_info_text.setPlainText(f"Found {len(pythons)} Python installation(s).\nSelect one to view details.")

    def python_show_info(self, item):
        """Show Python information"""
        python = item.data(Qt.ItemDataRole.UserRole)
        if python:
            info = self.python_detector.get_python_info(python.path)
            details = f"""Path: {python.path}
Version: {info.get('version', 'Unknown')}
Architecture: {info.get('architecture', 'Unknown')}
Prefix: {info.get('prefix', 'Unknown')}
Virtual Environment: {'Yes' if python.is_venv else 'No'}
Current: {'Yes' if python.is_current else 'No'}
"""
            self.python_info_text.setPlainText(details)

    def python_select_current(self):
        """Select the currently highlighted Python"""
        current = self.python_list_widget.currentItem()
        if not current:
            QMessageBox.warning(self, "No Selection", "Please select a Python installation first.")
            return

        python = current.data(Qt.ItemDataRole.UserRole)
        if not python:
            return

        # Update installer
        self.on_python_version_selected(python.path, python.version)

        QMessageBox.information(
            self,
            "Python Selected",
            f"Successfully selected Python {python.version}\n\nPath: {python.path}\n\nAll package operations will now use this Python version."
        )

    def update_check_outdated(self):
        """Check for outdated packages"""
        self.update_list_widget.clear()
        self.update_results_text.setPlainText("Checking for outdated packages...")

        success, packages = self.update_manager.check_outdated_packages()

        if not success:
            self.update_results_text.setPlainText("Failed to check for updates")
            return

        if not packages:
            self.update_results_text.setPlainText("All packages are up to date!")
            item = QListWidgetItem("✓ All packages are up to date")
            self.update_list_widget.addItem(item)
            return

        self.update_results_text.setPlainText(f"Found {len(packages)} outdated package(s)")

        for pkg in packages:
            display_text = f"{pkg['name']}: {pkg['version']} → {pkg['latest_version']}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, pkg)
            self.update_list_widget.addItem(item)

    def toggle_mirror_dropdown(self, state):
        """Toggle mirror dropdown based on checkbox state"""
        self.mirror_dropdown.setEnabled(state == Qt.CheckState.Checked.value)

    def _populate_mirror_dropdown(self):
        """(Re)fill the mirror dropdown in the current language.

        Item format stays "<name> - <url>" so update_all_packages can keep
        extracting the URL by splitting on ' - '.
        """
        mirrors = [
            ('mirror_tsinghua', 'https://pypi.tuna.tsinghua.edu.cn/simple/'),
            ('mirror_douban', 'https://pypi.douban.com/simple/'),
            ('mirror_aliyun', 'https://mirrors.aliyun.com/pypi/simple/'),
            ('mirror_ustc', 'https://pypi.mirrors.ustc.edu.cn/simple/'),
        ]
        self.mirror_dropdown.clear()
        for name_key, url in mirrors:
            self.mirror_dropdown.addItem(f"{tr(name_key)} - {url}")

    def update_all_packages(self):
        """Update all outdated packages"""
        # Get mirror URL if checkbox is checked
        mirror_url = None
        if self.mirror_checkbox.isChecked():
            mirror_text = self.mirror_dropdown.currentText()
            # Extract URL from text like "清华大学 - https://..."
            mirror_url = mirror_text.split(' - ')[-1] if ' - ' in mirror_text else mirror_text

        source_info = f" using mirror: {mirror_url}" if mirror_url else " using default PyPI"
        self.update_results_text.setPlainText(f"Updating all outdated packages{source_info}...\n")

        success, message = self.update_manager.update_all_outdated(mirror_url)

        if success:
            self.update_results_text.append(f"\n✓ {message}")
            self.update_check_outdated()  # Refresh list
        else:
            self.update_results_text.append(f"\n✗ {message}")

    def req_import_file(self):
        """Import packages from requirements.txt"""
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select requirements.txt", "", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            self.req_info_text.setPlainText(f"Importing from {file_path}...")

            success, message = self.requirements_manager.import_requirements(file_path)

            if success:
                self.req_info_text.append(f"\n✓ {message}")
            else:
                self.req_info_text.append(f"\n✗ {message}")

    def req_export_all(self):
        """Export all installed packages to requirements.txt"""
        from PyQt6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save requirements.txt", "requirements.txt", "Text Files (*.txt);;All Files (*)"
        )

        if file_path:
            self.req_info_text.setPlainText(f"Exporting to {file_path}...")

            success, message = self.requirements_manager.export_requirements(file_path, include_versions=True)

            if success:
                self.req_info_text.append(f"\n✓ {message}")
            else:
                self.req_info_text.append(f"\n✗ {message}")

    def open_venv_manager(self):
        """Open Virtual Environment Manager dialog"""
        dialog = VenvManagerDialog(self)
        dialog.exec()

    def open_python_selector(self):
        """Open Python Version Selector dialog"""
        dialog = PythonSelectorDialog(self.selected_python_path, self)
        dialog.python_selected.connect(self.on_python_version_selected)
        dialog.exec()

    def on_python_version_selected(self, python_path, python_version):
        """Handle Python version selection"""
        self.selected_python_path = python_path
        self.selected_python_version = python_version

        # Update installer to use new Python
        self.installer.set_python_executable(python_path)

        # Rebuild cache with new Python
        self._build_installed_cache()

        # Reload current category
        if self.current_category:
            self.load_category(self.current_category, check_installed=True)

        # Update window title
        self.setWindowTitle(f"Library Manager - Using Python {python_version}")

        # Update status bar
        self.status_bar.showMessage(f"Python: {python_version} | Path: {python_path}")

        # Show notification
        if self.system_tray:
            self.system_tray.show_info(
                "Python Version Changed",
                f"Now using Python {python_version}"
            )

    def create_settings_view(self):
        """Create Settings view - theme and language options"""
        view = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self.settings_header = QLabel(tr('settings_title'))
        self.settings_header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        self.settings_header.setStyleSheet("color: #3498db; padding: 10px;")
        layout.addWidget(self.settings_header)

        # Theme selector
        self.settings_theme_label = QLabel(tr('settings_theme'))
        self.settings_theme_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(self.settings_theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems([tr('theme_light'), tr('theme_dark')])
        self.theme_combo.setCurrentIndex(1 if self.theme_manager.is_dark else 0)
        self.theme_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 13px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                color: #2c3e50;
            }
        """)
        self.theme_combo.currentIndexChanged.connect(self.set_theme)
        layout.addWidget(self.theme_combo)

        # Language selector
        self.settings_language_label = QLabel(tr('settings_language'))
        self.settings_language_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(self.settings_language_label)

        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "中文"])
        self.language_combo.setCurrentIndex(1 if get_language() == 'zh' else 0)
        self.language_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 13px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                color: #2c3e50;
            }
        """)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        layout.addWidget(self.language_combo)

        # Close behavior selector
        self.settings_close_label = QLabel(tr('settings_close_behavior'))
        self.settings_close_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(self.settings_close_label)

        self.close_behavior_combo = QComboBox()
        self.close_behavior_combo.addItems([tr('close_to_tray'), tr('close_exit')])
        self.close_behavior_combo.setCurrentIndex(
            0 if self.settings.value("close_behavior", "tray") == "tray" else 1
        )
        self.close_behavior_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 13px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                color: #2c3e50;
            }
        """)
        self.close_behavior_combo.currentIndexChanged.connect(self.set_close_behavior)
        layout.addWidget(self.close_behavior_combo)

        # Hint
        self.settings_hint_label = QLabel(tr('settings_hint'))
        self.settings_hint_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        layout.addWidget(self.settings_hint_label)

        layout.addStretch()
        view.setLayout(layout)
        return view

    def set_theme(self, index):
        """Apply theme selected in Settings (0=light, 1=dark) and persist it"""
        self.theme_manager.is_dark = (index == 1)
        self.settings.setValue("theme", "dark" if self.theme_manager.is_dark else "light")
        self.apply_theme()
        # Reload current category to refresh colors
        if self.current_category:
            self.load_category(self.current_category, check_installed=True)

    def change_language(self, index):
        """Switch UI language (0=English, 1=中文) and persist it"""
        language = 'zh' if index == 1 else 'en'
        set_language(language)
        self.settings.setValue("language", language)
        self.retranslate_ui()

    def set_close_behavior(self, index):
        """Persist close behavior (0=minimize to tray, 1=exit)"""
        self.settings.setValue("close_behavior", "tray" if index == 0 else "exit")

    def update_status_bar(self):
        """Refresh the status bar Python info in the current language"""
        python_info = self.installer.get_python_info()
        self.status_bar.showMessage(
            tr('status_python').format(
                version=python_info['version'], path=python_info['path']
            )
        )

    def retranslate_ui(self):
        """Re-apply all translatable strings after a language change"""
        # Header navigation
        self.nav_packages_btn.setText(tr('nav_packages'))
        self.nav_scan_btn.setText(tr('nav_scan'))
        self.nav_venv_btn.setText(tr('nav_venv'))
        self.nav_python_btn.setText(tr('nav_python'))
        self.nav_update_btn.setText(tr('nav_update'))
        self.nav_requirements_btn.setText(tr('nav_requirements'))
        self.nav_settings_btn.setText(tr('nav_settings'))

        # Sidebar
        self.sidebar_header.setText(tr('sidebar_categories'))
        for category, btn in self.category_buttons.items():
            btn.setText(tr('cat.' + category))

        # Packages view
        if self.current_category:
            self.category_label.setText(tr('cat.' + self.current_category))
        else:
            self.category_label.setText(tr('content_select_category'))
        self.select_all_btn.setText(tr('btn_select_all'))
        self.deselect_all_btn.setText(tr('btn_deselect_all'))

        # View headers / descriptions
        self.scan_header.setText(tr('scan_title'))
        self.scan_desc.setText(tr('scan_desc'))
        self.venv_header.setText(tr('venv_title'))
        self.python_header.setText(tr('python_title'))
        self.python_desc.setText(tr('python_desc'))
        self.update_header.setText(tr('update_title'))
        self.update_desc.setText(tr('update_desc'))
        self.mirror_checkbox.setText(tr('mirror_checkbox'))
        mirror_index = self.mirror_dropdown.currentIndex()
        self._populate_mirror_dropdown()
        self.mirror_dropdown.setCurrentIndex(max(mirror_index, 0))
        self.req_header.setText(tr('req_title'))
        self.req_desc.setText(tr('req_desc'))

        # Settings view itself (block signals to avoid re-entry)
        self.settings_header.setText(tr('settings_title'))
        self.settings_theme_label.setText(tr('settings_theme'))
        self.settings_language_label.setText(tr('settings_language'))
        self.settings_close_label.setText(tr('settings_close_behavior'))
        self.settings_hint_label.setText(tr('settings_hint'))
        self.theme_combo.blockSignals(True)
        self.theme_combo.setItemText(0, tr('theme_light'))
        self.theme_combo.setItemText(1, tr('theme_dark'))
        self.theme_combo.blockSignals(False)
        self.close_behavior_combo.blockSignals(True)
        self.close_behavior_combo.setItemText(0, tr('close_to_tray'))
        self.close_behavior_combo.setItemText(1, tr('close_exit'))
        self.close_behavior_combo.blockSignals(False)

        # Status bar
        self.update_status_bar()

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.theme_manager.toggle_theme()
        self.settings.setValue("theme", "dark" if self.theme_manager.is_dark else "light")
        self.theme_combo.blockSignals(True)
        self.theme_combo.setCurrentIndex(1 if self.theme_manager.is_dark else 0)
        self.theme_combo.blockSignals(False)
        self.apply_theme()
        # Reload current category to refresh colors
        if self.current_category:
            self.load_category(self.current_category, check_installed=True)

    def apply_theme(self):
        """Apply current theme"""
        self.setStyleSheet(self.theme_manager.get_stylesheet())

    def closeEvent(self, event):
        """Handle window close event per the close_behavior setting"""
        minimize_to_tray = self.settings.value("close_behavior", "tray") == "tray"
        if minimize_to_tray and self.system_tray and self.system_tray.is_available():
            # Minimize to tray instead of closing
            event.ignore()
            self.hide()
            self.system_tray.show_info(
                "Library Manager",
                tr('tray_minimized_msg')
            )
        else:
            # Exit normally
            event.accept()
