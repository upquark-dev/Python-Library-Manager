"""Virtual Environment Manager Dialog"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QMessageBox,
    QInputDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from core.venv_manager import VirtualEnvManager


class VenvListWorker(QThread):
    """Worker thread to list virtual environments"""
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, venv_manager):
        super().__init__()
        self.venv_manager = venv_manager

    def run(self):
        try:
            venvs = self.venv_manager.list_venvs()
            self.finished.emit(venvs)
        except Exception as e:
            self.error.emit(str(e))


class VenvCreateWorker(QThread):
    """Worker thread to create virtual environment"""
    finished = pyqtSignal(bool, str)

    def __init__(self, venv_manager, name):
        super().__init__()
        self.venv_manager = venv_manager
        self.name = name

    def run(self):
        success, message = self.venv_manager.create_venv(self.name)
        self.finished.emit(success, message)


class VenvManagerDialog(QDialog):
    """Dialog for managing virtual environments"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.venv_manager = VirtualEnvManager()
        self.current_venvs = []

        self.setWindowTitle("Virtual Environment Manager")
        self.setMinimumSize(800, 600)
        self.setModal(True)

        self.init_ui()
        self.load_venvs()

    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Header
        header = QLabel("<h1>🔧 Virtual Environment Manager</h1>")
        header.setStyleSheet("color: #3498db; margin-bottom: 10px;")
        layout.addWidget(header)

        # Info label
        info_path = self.venv_manager.get_default_venv_path()
        info = QLabel(f"<b>Default Location:</b> {info_path}")
        info.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(info)

        # Toolbar
        toolbar = QHBoxLayout()

        self.new_btn = QPushButton("➕ New Environment")
        self.new_btn.setStyleSheet("""
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
        self.new_btn.clicked.connect(self.create_new_venv)
        toolbar.addWidget(self.new_btn)

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setStyleSheet("""
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
        self.refresh_btn.clicked.connect(self.load_venvs)
        toolbar.addWidget(self.refresh_btn)

        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.delete_btn.clicked.connect(self.delete_venv)
        self.delete_btn.setEnabled(False)
        toolbar.addWidget(self.delete_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Virtual environments list
        self.venv_list = QListWidget()
        self.venv_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #e0e0e0;
                margin-bottom: 5px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #ecf0f1;
            }
        """)
        self.venv_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.venv_list)

        # Details panel
        self.details_panel = QTextEdit()
        self.details_panel.setReadOnly(True)
        self.details_panel.setMaximumHeight(150)
        self.details_panel.setStyleSheet("""
            QTextEdit {
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                padding: 10px;
                background-color: #f8f9fa;
                font-family: monospace;
            }
        """)
        layout.addWidget(self.details_panel)

        # Action buttons
        action_layout = QHBoxLayout()

        self.activate_btn = QPushButton("✅ Show Activate Command")
        self.activate_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.activate_btn.clicked.connect(self.show_activate_command)
        self.activate_btn.setEnabled(False)
        action_layout.addWidget(self.activate_btn)

        action_layout.addStretch()

        close_btn = QPushButton("Close")
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
        close_btn.clicked.connect(self.close)
        action_layout.addWidget(close_btn)

        layout.addLayout(action_layout)
        self.setLayout(layout)

    def load_venvs(self):
        """Load virtual environments"""
        self.venv_list.clear()
        self.details_panel.clear()
        self.details_panel.append("Loading virtual environments...")

        # Disable buttons
        self.new_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)

        # Load in background thread
        self.worker = VenvListWorker(self.venv_manager)
        self.worker.finished.connect(self.on_venvs_loaded)
        self.worker.error.connect(self.on_load_error)
        self.worker.start()

    def on_venvs_loaded(self, venvs):
        """Handle loaded virtual environments"""
        self.current_venvs = venvs
        self.new_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)

        if not venvs:
            self.details_panel.clear()
            self.details_panel.append("No virtual environments found.")
            self.details_panel.append(f"\nCreate one using the '➕ New Environment' button.")
            return

        for venv in venvs:
            item = QListWidgetItem()
            item.setText(self._format_venv_item(venv))
            item.setData(Qt.ItemDataRole.UserRole, venv)
            self.venv_list.addItem(item)

        self.details_panel.clear()
        self.details_panel.append(f"Found {len(venvs)} virtual environment(s).")

    def _format_venv_item(self, venv):
        """Format virtual environment for display"""
        return (
            f"📁 {venv['name']}\n"
            f"   Python {venv['python_version']} | "
            f"{venv['package_count']} packages | "
            f"{venv['size']}"
        )

    def on_load_error(self, error):
        """Handle loading error"""
        self.new_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.details_panel.clear()
        self.details_panel.append(f"Error loading environments: {error}")

    def on_selection_changed(self):
        """Handle selection change"""
        selected = self.venv_list.selectedItems()

        if selected:
            self.delete_btn.setEnabled(True)
            self.activate_btn.setEnabled(True)

            venv = selected[0].data(Qt.ItemDataRole.UserRole)
            self.show_venv_details(venv)
        else:
            self.delete_btn.setEnabled(False)
            self.activate_btn.setEnabled(False)
            self.details_panel.clear()

    def show_venv_details(self, venv):
        """Show virtual environment details"""
        self.details_panel.clear()
        self.details_panel.append("=" * 60)
        self.details_panel.append(f"Virtual Environment: {venv['name']}")
        self.details_panel.append("=" * 60)
        self.details_panel.append(f"Python Version: {venv['python_version']}")
        self.details_panel.append(f"Location: {venv['path']}")
        self.details_panel.append(f"Packages Installed: {venv['package_count']}")
        self.details_panel.append(f"Size: {venv['size']}")
        self.details_panel.append("=" * 60)

    def create_new_venv(self):
        """Create a new virtual environment"""
        name, ok = QInputDialog.getText(
            self,
            "Create Virtual Environment",
            "Enter environment name:",
            text="my-project-env"
        )

        if not ok or not name:
            return

        # Validate name
        if not name.replace('-', '').replace('_', '').isalnum():
            QMessageBox.warning(
                self,
                "Invalid Name",
                "Environment name can only contain letters, numbers, hyphens, and underscores."
            )
            return

        # Create in background
        self.details_panel.clear()
        self.details_panel.append(f"Creating virtual environment '{name}'...")
        self.details_panel.append("This may take a minute...")

        self.new_btn.setEnabled(False)

        self.create_worker = VenvCreateWorker(self.venv_manager, name)
        self.create_worker.finished.connect(self.on_venv_created)
        self.create_worker.start()

    def on_venv_created(self, success, message):
        """Handle virtual environment creation result"""
        self.new_btn.setEnabled(True)

        if success:
            QMessageBox.information(self, "Success", message)
            self.load_venvs()
        else:
            QMessageBox.warning(self, "Error", message)
            self.details_panel.append(f"\nError: {message}")

    def delete_venv(self):
        """Delete selected virtual environment"""
        selected = self.venv_list.selectedItems()
        if not selected:
            return

        venv = selected[0].data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{venv['name']}'?\n\n"
            f"This will permanently delete:\n"
            f"  - {venv['package_count']} installed packages\n"
            f"  - {venv['size']} of disk space\n\n"
            f"This action cannot be undone!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            return

        success, message = self.venv_manager.delete_venv(venv['path'])

        if success:
            QMessageBox.information(self, "Success", message)
            self.load_venvs()
        else:
            QMessageBox.warning(self, "Error", message)

    def show_activate_command(self):
        """Show command to activate the selected environment"""
        selected = self.venv_list.selectedItems()
        if not selected:
            return

        venv = selected[0].data(Qt.ItemDataRole.UserRole)
        cmd = self.venv_manager.get_activate_command(venv['path'])

        msg = (
            f"To activate '{venv['name']}', run this command in your terminal:\n\n"
            f"{cmd}\n\n"
            f"After activation, any package you install will go into this environment."
        )

        # Copy to clipboard
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(cmd)

        QMessageBox.information(
            self,
            "Activate Command",
            msg + "\n\n✓ Command copied to clipboard!"
        )
