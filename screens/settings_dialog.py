from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
                               QDialogButtonBox, QComboBox, QFormLayout, QSpinBox, QWidget, QHBoxLayout,
                               QGroupBox)
from PySide6.QtCore import Qt
from settings_manager import SettingsManager
from widgets import ModelDetailsWidget

class SettingsDialog(QDialog):
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Settings")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # --- API Key ---
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter your Groq API Key (or set GROQ_API_KEY env var)")
        self.api_key_edit.setText(self.settings_manager.get_groq_api_key())
        # self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password) # Optional: mask key
        form_layout.addRow("Groq API Key:", self.api_key_edit)
        form_layout.addRow(QLabel("<small><i>Note: Key is stored via QSettings. For higher security, use environment variables.</i></small>"))


        # --- Theme Selection ---
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        current_theme = self.settings_manager.get_theme()
        self.theme_combo.setCurrentText(current_theme)
        form_layout.addRow("Theme:", self.theme_combo)

        # --- LLM Model Selection ---
        model_box = QGroupBox("LLM Model Settings")
        model_box_layout = QVBoxLayout()
        self.model_details_widget = ModelDetailsWidget(self.settings_manager, self.parent().llm_handler)
        model_box_layout.addWidget(self.model_details_widget)
        model_box.setLayout(model_box_layout)
        form_layout.addRow("", model_box)


        # --- Font Size (Accessibility) ---
        # font_size_layout = QHBoxLayout()
        # self.font_size_spin = QSpinBox()
        # self.font_size_spin.setRange(8, 20) # Example range
        # self.font_size_spin.setValue(self.settings_manager.get_font_size())
        # font_size_layout.addWidget(self.font_size_spin)
        # font_size_layout.addWidget(QPushButton("Apply Font (Restart?)")) # Font changes might be tricky live
        # form_layout.addRow("Base Font Size:", font_size_layout)


        layout.addLayout(form_layout)

        # --- Dialog Buttons ---
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def accept(self):
        # Save settings before closing
        self.settings_manager.set_groq_api_key(self.api_key_edit.text())
        self.settings_manager.set_theme(self.theme_combo.currentText())
        # Model is already saved by the ModelDetailsWidget
        # self.settings_manager.set_font_size(self.font_size_spin.value())

        # Notify main window or LLM handler if API key or model changed significantly
        # This might require emitting a signal or calling a method on the parent/main_window
        if hasattr(self.parent(), 'settings_updated'):
             self.parent().settings_updated()

        super().accept()

    def reject(self):
        super().reject()