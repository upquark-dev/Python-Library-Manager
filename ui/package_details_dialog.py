"""Package details dialog window"""

from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea,
    QWidget, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess


class PackageInfoWorker(QThread):
    """Worker thread to fetch package information"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, package_name):
        super().__init__()
        self.package_name = package_name

    def run(self):
        """Fetch package information"""
        try:
            # Get package info from pip
            result = subprocess.run(
                ["pip", "show", self.package_name, "--verbose"],
                capture_output=True,
                text=True,
                timeout=10
            )

            info = {}
            if result.returncode == 0:
                # Parse pip show output
                for line in result.stdout.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        info[key.strip()] = value.strip()

            # Try to get PyPI info
            try:
                pypi_result = subprocess.run(
                    ["pip", "index", "versions", self.package_name],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if pypi_result.returncode == 0:
                    info['available_versions'] = pypi_result.stdout
            except Exception:
                pass

            self.finished.emit(info)

        except Exception as e:
            self.error.emit(str(e))


class PackageDetailsDialog(QDialog):
    """Dialog to show detailed package information"""

    def __init__(self, package_name, package_description, install_cmd, parent=None):
        super().__init__(parent)
        self.package_name = package_name
        self.package_description = package_description
        self.install_cmd = install_cmd
        self.package_info = {}

        self.setWindowTitle(f"Package Details - {package_name}")
        self.setMinimumSize(700, 600)
        self.setModal(True)

        self.init_ui()
        self.load_package_info()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel(f"<h1>{self.package_name}</h1>")
        header.setStyleSheet("color: #3498db; margin-bottom: 10px;")
        layout.addWidget(header)

        # Description
        desc_label = QLabel("<b>Description:</b>")
        layout.addWidget(desc_label)

        desc_text = QLabel(self.package_description)
        desc_text.setWordWrap(True)
        desc_text.setStyleSheet("padding: 10px; background-color: #f5f5f5; border-radius: 5px;")
        layout.addWidget(desc_text)

        # Install command
        cmd_label = QLabel("<b>Install Command:</b>")
        layout.addWidget(cmd_label)

        cmd_text = QLabel(f"<code>{self.install_cmd}</code>")
        cmd_text.setStyleSheet("""
            padding: 10px;
            background-color: #2c3e50;
            color: #00ff00;
            border-radius: 5px;
            font-family: monospace;
        """)
        layout.addWidget(cmd_text)

        # Loading indicator
        self.loading_label = QLabel("Loading package information...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        layout.addWidget(self.progress_bar)

        # Scroll area for package info
        self.info_scroll = QScrollArea()
        self.info_scroll.setWidgetResizable(True)
        self.info_scroll.setVisible(False)

        self.info_widget = QWidget()
        self.info_layout = QVBoxLayout()
        self.info_widget.setLayout(self.info_layout)
        self.info_scroll.setWidget(self.info_widget)

        layout.addWidget(self.info_scroll)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Copy install command button
        copy_btn = QPushButton("📋 Copy Install Command")
        copy_btn.clicked.connect(self.copy_install_command)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(copy_btn)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_package_info(self):
        """Load package information in background thread"""
        self.worker = PackageInfoWorker(self.package_name)
        self.worker.finished.connect(self.on_info_loaded)
        self.worker.error.connect(self.on_info_error)
        self.worker.start()

    def on_info_loaded(self, info):
        """Handle loaded package information"""
        self.package_info = info
        self.loading_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.info_scroll.setVisible(True)

        # Clear previous info
        while self.info_layout.count():
            child = self.info_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if not info:
            no_info = QLabel("⚠ Package not installed. Install it to see detailed information.")
            no_info.setStyleSheet("color: #e67e22; padding: 20px; font-size: 14px;")
            no_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.info_layout.addWidget(no_info)
            return

        # Display package information
        info_items = [
            ("Version", info.get("Version", "N/A")),
            ("Author", info.get("Author", "N/A")),
            ("Author Email", info.get("Author-email", "N/A")),
            ("License", info.get("License", "N/A")),
            ("Location", info.get("Location", "N/A")),
            ("Home Page", info.get("Home-page", "N/A")),
            ("Requires", info.get("Requires", "None")),
            ("Required By", info.get("Required-by", "None")),
        ]

        for label, value in info_items:
            self.add_info_row(label, value)

        # Summary section
        summary = info.get("Summary", "")
        if summary:
            summary_label = QLabel("<b>Summary:</b>")
            self.info_layout.addWidget(summary_label)

            summary_text = QLabel(summary)
            summary_text.setWordWrap(True)
            summary_text.setStyleSheet("padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
            self.info_layout.addWidget(summary_text)

        self.info_layout.addStretch()

    def add_info_row(self, label, value):
        """Add an information row"""
        container = QFrame()
        container.setStyleSheet("border-bottom: 1px solid #e0e0e0;")

        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(10, 10, 10, 10)

        label_widget = QLabel(f"<b>{label}:</b>")
        label_widget.setFixedWidth(150)
        row_layout.addWidget(label_widget)

        # Make URLs clickable
        if value.startswith("http"):
            value_widget = QLabel(f'<a href="{value}">{value}</a>')
            value_widget.setOpenExternalLinks(True)
        else:
            value_widget = QLabel(value)

        value_widget.setWordWrap(True)
        value_widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        row_layout.addWidget(value_widget, 1)

        container.setLayout(row_layout)
        self.info_layout.addWidget(container)

    def on_info_error(self, error_msg):
        """Handle error loading package info"""
        self.loading_label.setText(f"⚠ Error: {error_msg}")
        self.progress_bar.setVisible(False)

    def copy_install_command(self):
        """Copy install command to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.install_cmd)

        # Show confirmation
        self.loading_label.setText("✓ Install command copied to clipboard!")
        self.loading_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.loading_label.setVisible(True)
