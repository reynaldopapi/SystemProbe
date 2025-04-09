from PySide6.QtWidgets import (QVBoxLayout, QLabel, QTextEdit, QPushButton,
                               QWidget, QHBoxLayout, QSizePolicy)
from PySide6.QtCore import Qt
from .base_screen import BaseScreen

class InitialPromptScreen(BaseScreen):
    def __init__(self, main_window, state_manager, settings_manager, llm_handler):
        super().__init__(main_window, state_manager, settings_manager, llm_handler)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Step 2: Set Initial System Prompt")
        title_font = title.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        guidance = QLabel("Enter the starting system prompt below. This will be the first prompt tested and the baseline for refinement.")
        guidance.setWordWrap(True)
        layout.addWidget(guidance)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.prompt_edit)

        nav_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(lambda: self.main_window.navigate_to("input_config"))
        self.start_testing_button = QPushButton("Start Testing")
        self.start_testing_button.clicked.connect(self.start_testing)

        nav_layout.addWidget(self.back_button)
        nav_layout.addStretch(1)
        nav_layout.addWidget(self.start_testing_button)
        layout.addLayout(nav_layout)

        self.setLayout(layout)

    def load_state(self):
        initial_prompt = self.state_manager.get_current_prompt()
        self.prompt_edit.setPlainText(initial_prompt)
        self.update_status("Set the initial system prompt.")

    def save_state(self):
        self.state_manager.set_initial_prompt(self.prompt_edit.toPlainText())

    def start_testing(self):
        if not self.prompt_edit.toPlainText().strip():
             self.show_error("Input Required", "Please enter an initial system prompt.")
             return
        self.leave_screen() # Saves state
        self.main_window.navigate_to("output_testing")
        # Trigger the first LLM B call from the OutputTestingScreen's enter_screen

    def enter_screen(self):
        super().enter_screen()
        self.state_manager.set_current_step("initial_prompt")