"""Python Version Selector Dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QTextEdit, QMessageBox,
    QGroupBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from core.python_detector import PythonDetector


class PythonDetectorWorker(QThread):
    """Worker thread for detecting Python installations"""

    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def run(self):
        """Run Python detection"""
        try:
            detector = PythonDetector()
            pythons = detector.detect_all()
            self.finished.emit(pythons)
        except Exception as e:
            self.error.emit(str(e))


class PythonInfoWorker(QThread):
    """Worker thread for getting Python detailed info"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, python_path):
        super().__init__()
        self.python_path = python_path

    def run(self):
        """Get Python info"""
        try:
            detector = PythonDetector()
            info = detector.get_python_info(self.python_path)
            self.finished.emit(info)
        except Exception as e:
            self.error.emit(str(e))


class PythonSelectorDialog(QDialog):
    """Dialog for selecting Python version"""

    python_selected = pyqtSignal(str, str)  # path, version

    def __init__(self, current_python_path=None, parent=None):
        super().__init__(parent)
        self.current_python_path = current_python_path
        self.selected_python = None
        self.pythons_list = []
        self.detector_worker = None
        self.info_worker = None

        self.setWindowTitle("Python Version Selector")
        self.setMinimumSize(700, 500)
        self.init_ui()
        self.start_detection()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Header
        header = QLabel("🐍 Select Python Version")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Description
        desc = QLabel(
            "Select which Python installation to use for package management.\n"
            "The application will use this Python version for all pip operations."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; padding: 10px;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)

        # Python list group
        list_group = QGroupBox("Available Python Installations")
        list_layout = QVBoxLayout()

        self.python_list = QListWidget()
        self.python_list.setMinimumHeight(200)
        self.python_list.currentItemChanged.connect(self.on_python_selected)
        list_layout.addWidget(self.python_list)

        list_group.setLayout(list_layout)
        layout.addWidget(list_group)

        # Info panel
        info_group = QGroupBox("Python Information")
        info_layout = QVBoxLayout()

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11px;
            }
        """)
        info_layout.addWidget(self.info_text)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Buttons
        button_layout = QHBoxLayout()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.start_detection)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addWidget(refresh_btn)

        button_layout.addStretch()

        select_btn = QPushButton("✓ Select This Python")
        select_btn.clicked.connect(self.select_python)
        select_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        button_layout.addWidget(select_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def start_detection(self):
        """Start Python detection in background"""
        self.python_list.clear()
        self.info_text.clear()

        # Show loading
        loading_item = QListWidgetItem("🔍 Detecting Python installations...")
        self.python_list.addItem(loading_item)

        # Start worker
        self.detector_worker = PythonDetectorWorker()
        self.detector_worker.finished.connect(self.on_detection_finished)
        self.detector_worker.error.connect(self.on_detection_error)
        self.detector_worker.start()

    def on_detection_finished(self, pythons):
        """Handle detection completion"""
        self.python_list.clear()
        self.pythons_list = pythons

        if not pythons:
            item = QListWidgetItem("⚠️ No Python installations found")
            self.python_list.addItem(item)
            return

        for python in pythons:
            # Create display text
            display_text = f"Python {python.version}"

            if python.is_current:
                display_text += " ★ CURRENT"
            if python.is_venv:
                display_text += " [Virtual Env]"

            # Create list item
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, python)

            # Highlight current Python
            if python.is_current:
                font = item.font()
                font.setBold(True)
                item.setFont(font)
                item.setBackground(Qt.GlobalColor.lightGray)

            self.python_list.addItem(item)

        # Select first item
        if self.python_list.count() > 0:
            self.python_list.setCurrentRow(0)

    def on_detection_error(self, error_msg):
        """Handle detection error"""
        self.python_list.clear()
        item = QListWidgetItem(f"❌ Error: {error_msg}")
        self.python_list.addItem(item)

    def on_python_selected(self, current, previous):
        """Handle Python selection"""
        if not current:
            return

        python = current.data(Qt.ItemDataRole.UserRole)
        if not python:
            return

        self.selected_python = python
        self.load_python_info(python.path)

    def load_python_info(self, python_path):
        """Load detailed Python information"""
        self.info_text.setPlainText("Loading information...")

        # Start worker
        self.info_worker = PythonInfoWorker(python_path)
        self.info_worker.finished.connect(self.on_info_loaded)
        self.info_worker.error.connect(self.on_info_error)
        self.info_worker.start()

    def on_info_loaded(self, info):
        """Display Python information"""
        text = f"""Path: {self.selected_python.path}
Version: {info.get('version', 'Unknown')}
Architecture: {info.get('architecture', 'Unknown')}
Prefix: {info.get('prefix', 'Unknown')}
Virtual Environment: {'Yes' if self.selected_python.is_venv else 'No'}
"""
        self.info_text.setPlainText(text)

    def on_info_error(self, error_msg):
        """Handle info loading error"""
        self.info_text.setPlainText(f"Error loading information: {error_msg}")

    def select_python(self):
        """Select the current Python"""
        if not self.selected_python:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a Python installation first."
            )
            return

        # Emit signal
        self.python_selected.emit(self.selected_python.path, self.selected_python.version)

        # Show confirmation
        QMessageBox.information(
            self,
            "Python Selected",
            f"Successfully selected Python {self.selected_python.version}\n\n"
            f"Path: {self.selected_python.path}\n\n"
            "All package operations will now use this Python version."
        )

        self.accept()

    def get_selected_python(self):
        """Get the selected Python"""
        return self.selected_python
