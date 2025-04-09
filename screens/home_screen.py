from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QGroupBox
from PySide6.QtCore import Qt
from .base_screen import BaseScreen
from widgets import ModelDetailsWidget
import os # For file dialog

class HomeScreen(BaseScreen):
    def __init__(self, main_window, state_manager, settings_manager, llm_handler):
        super().__init__(main_window, state_manager, settings_manager, llm_handler)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("SystemProbe")
        title_font = title.font()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Optimize system prompts without training your LLMs.")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_font = subtitle.font()
        subtitle_font.setPointSize(12)
        subtitle.setFont(subtitle_font)

        self.new_workflow_button = QPushButton("Start New Workflow")
        self.new_workflow_button.clicked.connect(self.start_new_workflow)

        self.load_session_button = QPushButton("Load Existing Session")
        self.load_session_button.clicked.connect(self.load_session)

        # Placeholder for version info
        version_label = QLabel("Version 0.1.0 (Generated)") # Example version
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_font = version_label.font()
        version_font.setPointSize(9)
        version_label.setFont(version_font)
        version_label.setStyleSheet("color: gray;")


        # Add model details widget
        model_box = QGroupBox("LLM Model Settings")
        model_box_layout = QVBoxLayout()
        self.model_details_widget = ModelDetailsWidget(self.settings_manager, self.llm_handler)
        self.model_details_widget.model_updated.connect(self.on_model_updated)
        model_box_layout.addWidget(self.model_details_widget)
        model_box.setLayout(model_box_layout)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(20)
        layout.addWidget(model_box)
        layout.addSpacing(20)
        layout.addWidget(self.new_workflow_button)
        layout.addWidget(self.load_session_button)
        layout.addStretch(1) # Push version label towards bottom
        layout.addWidget(version_label)

        self.setLayout(layout)

    def start_new_workflow(self):
        self.state_manager.clear_state()
        self.main_window.navigate_to("input_config")

    def load_session(self):
        self.main_window.load_session_action() # Trigger action in main window

    def enter_screen(self):
        # Reset anything specific to home screen if needed
        self.update_status("Ready. Start a new workflow or load a session.")
        self.state_manager.set_current_step("home")


    def on_model_updated(self, model_name):
        """Handle model selection change"""
        self.update_status(f"Model changed to {model_name}")
        # Re-initialize the LLM handler with the new model
        self.llm_handler.update_api_key()

    # No specific state to load/save for home screen itself beyond clearing on new
    def load_state(self): pass
    def save_state(self): pass